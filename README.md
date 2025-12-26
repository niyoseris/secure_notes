# Secure Notes

A secure, encrypted note-taking application built with Flask and AES-GCM encryption. This application allows users to create, store, and manage encrypted notes using a passphrase and PIN-based authentication system.

## Features

- **End-to-End Encryption**: All notes are encrypted using AES-GCM with 256-bit keys
- **Zero-Knowledge Architecture**: Encryption keys are derived from user credentials and never stored
- **Stateless Sessions**: No server-side storage of encryption keys
- **Title Support**: Notes can have optional titles for better organization
- **Secure Key Derivation**: PBKDF2 with 100,000 iterations for strong key generation
- **Modern UI**: Clean, responsive interface with glass-morphism design
- **Backward Compatibility**: Supports both new and legacy note formats

## Security Model

The application implements a "dead drop" security model where:

1. **Derivation Function**: Keys are derived from a user-provided phrase and 4-digit PIN
2. **Session-Based**: Keys exist only in memory during the user's session
3. **No Server Storage**: Encryption keys are never persisted on the server
4. **User Responsibility**: Users must remember their phrase + PIN to access notes

## Use Cases

### Personal Use
- **Private Journaling**: Keep personal thoughts and reflections secure
- **Password Management**: Store sensitive passwords and credentials
- **Financial Records**: Track financial information privately
- **Medical Notes**: Keep health-related information confidential

### Professional Use
- **Client Information**: Store sensitive client data securely
- **Research Notes**: Keep confidential research data
- **Legal Documents**: Temporary storage of sensitive legal information
- **IP Protection**: Store intellectual property drafts

### Emergency Scenarios
- **Digital Dead Drops**: Leave encrypted messages for others
- **Backup Information**: Store recovery information securely
- **Emergency Contacts**: Keep important contact information
- **Travel Documents**: Store digital copies of important documents

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/niyoseris/secure_notes.git
cd secure_notes

# Install dependencies
pip install flask cryptography

# Run the application
python3 app.py
```

The application will be available at `http://localhost:5001`

## Usage

### Authentication
1. **Phrase**: Enter a memorable phrase (e.g., "My favorite book is...")
2. **PIN**: Enter a 4-digit PIN (e.g., "1234")
3. **Login**: The system derives your encryption key from these credentials

### Creating Notes
1. Navigate to the dashboard
2. Click "New Note"
3. Enter an optional title
4. Enter your note content
5. Click "Encrypt & Save"

### Managing Notes
- **View**: Click on any note to view its decrypted content
- **Edit**: Use the "Edit Note" button to modify existing notes
- **Delete**: Use the delete button with confirmation

### Important Security Notes
- **Remember Credentials**: If you forget your phrase + PIN, your notes become inaccessible
- **Key Strength**: Use strong, unique phrases and PINs
- **Session Timeout**: Keys are cleared when you log out or close the browser
- **No Recovery**: There is no password recovery mechanism by design

## Architecture

### Encryption Flow
```
Phrase + PIN → PBKDF2 → AES-256-GCM Key → Encrypt Note Data
```

### File Structure
```
storage/
└── {folder_id}/
    └── {note_id}.enc
```

Where:
- `folder_id`: SHA256 hash of user credentials (deterministic)
- `note_id`: UUID for each note
- `.enc`: AES-GCM encrypted JSON data

### Data Format
```json
{
  "title": "Note Title",
  "content": "Encrypted note content"
}
```

## API Endpoints

- `GET /` - Login page
- `POST /` - Authenticate user
- `GET /dashboard` - List user's notes
- `GET /note/new` - Create new note form
- `POST /note/new` - Save new note
- `GET /note/<id>` - View note
- `GET /note/<id>/edit` - Edit note form
- `POST /note/<id>/edit` - Update note
- `POST /note/<id>/delete` - Delete note

## Dependencies

- **Flask**: Web framework
- **cryptography**: AES-GCM encryption implementation
- **Jinja2**: Template engine (included with Flask)

## Security Considerations

### Production Deployment
- Change the `app.secret_key` to a secure random key
- Use HTTPS in production
- Implement rate limiting
- Add CSRF protection
- Use a WSGI server (Gunicorn, uWSGI)
- Enable logging and monitoring

### Best Practices
- Use strong, memorable phrases
- Change PINs periodically
- Don't reuse credentials across services
- Keep backups of important information
- Use the application offline when possible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open-source. Please check the license file for details.

## Disclaimer

This application provides client-side encryption but relies on the security of your deployment environment. Always ensure your server is properly secured in production deployments.

---

**Remember**: With great encryption comes great responsibility. Keep your credentials safe!
