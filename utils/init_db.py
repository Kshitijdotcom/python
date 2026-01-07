"""Initialize the database with correct schema"""
from image_editor_server import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
        print("You can now start your server.")
