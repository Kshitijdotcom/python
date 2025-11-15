"""Test guest user creation"""
from image_editor_server import app, db, User
import uuid
import secrets

with app.app_context():
    # Try creating a guest user
    guest_username = f"guest_{uuid.uuid4().hex[:8]}"
    
    try:
        guest = User(username=guest_username, is_guest=True)
        guest.set_password(secrets.token_hex(16))
        
        db.session.add(guest)
        db.session.commit()
        
        print(f"✓ Guest user created successfully: {guest_username}")
        print(f"  ID: {guest.id}")
        print(f"  Is Guest: {guest.is_guest}")
        
        # Clean up
        db.session.delete(guest)
        db.session.commit()
        print("✓ Guest user deleted successfully")
        
    except Exception as e:
        print(f"✗ Error creating guest user: {e}")
        import traceback
        traceback.print_exc()
