from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import os
import uuid
from functools import wraps
from crypto_utils import derive_folder_id, derive_encryption_key, encrypt_content, decrypt_content

app = Flask(__name__)
# In a real production app, this should be a persistent secure random key.
# For this "dead drop" style app, we can generate it on startup, 
# but that would invalidate sessions on restart.
# We'll use a fixed key for dev convenience for now.
app.secret_key = b'development_secret_key_change_in_prod'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')

# Ensure storage exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'folder_id' not in session or 'encryption_key' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_session_data():
    return session.get('folder_id'), session.get('encryption_key')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phrase = request.form.get('phrase')
        pin = request.form.get('pin')
        
        if not phrase or not pin or len(pin) != 4 or not pin.isdigit():
            flash("Invalid Phrase or PIN (must be 4 digits)", "error")
            return redirect(url_for('login'))

        # Derive keys
        folder_id = derive_folder_id(phrase, pin)
        encryption_key = derive_encryption_key(phrase, pin)

        # Store in session (client-side encrypted cookie)
        # Note: In a high-security context, storing the key in the cookie is a trade-off.
        # It allows the server to be stateless regarding keys, but exposes the key to the client.
        session['folder_id'] = folder_id
        session['encryption_key'] = encryption_key # This will be serialized/signed by Flask

        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    folder_id, _ = get_session_data()
    user_storage_path = os.path.join(STORAGE_DIR, folder_id)
    
    notes = []
    if os.path.exists(user_storage_path):
        for filename in os.listdir(user_storage_path):
            if filename.endswith('.enc'):
                note_id = filename[:-4]
                # We can't read the title without decrypting. 
                # For this simple version, we'll just show the Note ID or a generic name.
                # Ideally, we might store a specialized metadata file or just decrypt the first few bytes if structured.
                # Let's list the files.
                notes.append({'id': note_id, 'name': f"Note {note_id[:8]}..."})
    
    return render_template('dashboard.html', notes=notes)

@app.route('/note/new', methods=['GET', 'POST'])
@login_required
def new_note():
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash("Content cannot be empty", "error")
            return redirect(url_for('new_note'))
            
        folder_id, encryption_key = get_session_data()
        
        # Encrypt
        try:
            encrypted_data = encrypt_content(content, encryption_key)
        except Exception as e:
            flash(f"Encryption failed: {str(e)}", "error")
            return redirect(url_for('new_note'))

        # Save
        note_id = str(uuid.uuid4())
        user_storage_path = os.path.join(STORAGE_DIR, folder_id)
        os.makedirs(user_storage_path, exist_ok=True)
        
        with open(os.path.join(user_storage_path, f"{note_id}.enc"), 'wb') as f:
            f.write(encrypted_data)
            
        return redirect(url_for('dashboard'))

    return render_template('note_form.html')

@app.route('/note/<note_id>')
@login_required
def view_note(note_id):
    folder_id, encryption_key = get_session_data()
    user_storage_path = os.path.join(STORAGE_DIR, folder_id)
    file_path = os.path.join(user_storage_path, f"{note_id}.enc")
    
    if not os.path.exists(file_path):
        abort(404)
        
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
            
        content = decrypt_content(encrypted_data, encryption_key)
    except Exception:
        flash("Failed to decrypt note. Wrong credentials?", "error")
        content = "Error: Could not decrypt file."

    return render_template('note_form.html', content=content, note_id=note_id, readonly=True)

@app.route('/note/<note_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    folder_id, encryption_key = get_session_data()
    user_storage_path = os.path.join(STORAGE_DIR, folder_id)
    file_path = os.path.join(user_storage_path, f"{note_id}.enc")
    
    if not os.path.exists(file_path):
        abort(404)

    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash("Content cannot be empty", "error")
            return redirect(url_for('edit_note', note_id=note_id))
            
        # Encrypt
        try:
            encrypted_data = encrypt_content(content, encryption_key)
        except Exception as e:
            flash(f"Encryption failed: {str(e)}", "error")
            return redirect(url_for('edit_note', note_id=note_id))

        # Overwrite
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        
        flash("Note updated successfully.", "success")
        return redirect(url_for('view_note', note_id=note_id))

    # GET: Decrypt and show form
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()  
        content = decrypt_content(encrypted_data, encryption_key)
    except Exception:
        flash("Failed to decrypt note for editing.", "error")
        return redirect(url_for('dashboard'))

    return render_template('note_form.html', content=content, note_id=note_id, readonly=False)

@app.route('/note/<note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    folder_id, _ = get_session_data()
    user_storage_path = os.path.join(STORAGE_DIR, folder_id)
    file_path = os.path.join(user_storage_path, f"{note_id}.enc")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        flash("Note deleted.", "success")
    else:
        flash("Note not found.", "error")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=8888)
