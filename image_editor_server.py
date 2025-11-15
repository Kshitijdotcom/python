from PIL import Image, ImageFilter
from io import BytesIO
from flask import Flask, request, jsonify, send_file, render_template_string, redirect, url_for, session
import base64
import time
from enhancement_engine import get_enhancement_engine
import logging
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
import secrets
import os

# Initialize the Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MAX_DOWNLOAD_TIMEOUT = 10 # seconds
ENHANCEMENT_TIMEOUT = 60 # seconds

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database on startup
def init_database():
    """Initialize or migrate database schema"""
    with app.app_context():
        try:
            import sqlite3
            from pathlib import Path
            
            db_path = Path('instance/users.db')
            
            # Check if database exists and has the user table
            if db_path.exists():
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    
                    # Check if user table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
                    table_exists = cursor.fetchone() is not None
                    
                    if table_exists:
                        # Check if is_guest column exists
                        cursor.execute("PRAGMA table_info(user)")
                        columns = {col[1] for col in cursor.fetchall()}
                        
                        if 'is_guest' not in columns:
                            logger.warning("Database schema outdated - recreating database")
                            conn.close()
                            db_path.unlink()  # Delete old database
                            db.create_all()
                            logger.info("Database recreated with new schema")
                        else:
                            logger.info("Database schema is up to date")
                            conn.close()
                    else:
                        # Table doesn't exist, create it
                        conn.close()
                        db.create_all()
                        logger.info("Database tables created")
                except Exception as e:
                    logger.error(f"Error checking database schema: {e}")
                    try:
                        conn.close()
                    except:
                        pass
                    # Try to create tables anyway
                    db.create_all()
                    logger.info("Database initialized after error")
            else:
                # Database doesn't exist, create it
                db.create_all()
                logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Fatal error initializing database: {e}")
            import traceback
            traceback.print_exc()
            # Last resort - just try to create tables
            try:
                db.create_all()
                logger.info("Database created as fallback")
            except Exception as e2:
                logger.error(f"Could not create database: {e2}")

# Run database initialization
init_database()

# --- Error Handlers ---

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors with JSON response"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'error_code': 'SERVER_ERROR'
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions with JSON response for API routes"""
    logger.error(f"Unhandled exception: {e}")
    import traceback
    traceback.print_exc()
    
    # Check if this is an API request (JSON expected)
    if request.path.startswith('/enhance') or request.path.startswith('/apply_filter'):
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': 'SERVER_ERROR'
        }), 500
    
    # For non-API routes, re-raise the exception
    raise e

# --- Core Image Fetching and Decoding Logic ---

def decode_base64_image(image_data):
    """Decodes base64 string into a PIL Image object."""
    try:
        # Remove header (e.g., 'data:image/png;base64,')
        if ',' in image_data:
             header, encoded_data = image_data.split(',', 1)
        else:
             encoded_data = image_data

        binary_data = base64.b64decode(encoded_data)
        # Convert to RGB for consistent processing across different client image formats
        return Image.open(BytesIO(binary_data)).convert('RGB'), None
    except Exception as e:
        return None, f"Error decoding base64 image data: {e}"


# --- Flask Routes ---

@app.route('/')
@login_required
def index():
    """Serves the index.html file - requires login"""
    return send_file('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                logger.info(f"User {username} logged in successfully")
                return redirect(url_for('index'))
            else:
                with open('templates/login.html', 'r', encoding='utf-8') as f:
                    return render_template_string(f.read(), error='Invalid username or password')
        
        with open('templates/login.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except Exception as e:
        logger.error(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return f"Login error: {e}", 500

@app.route('/register', methods=['POST'])
def register():
    """Register new user"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if User.query.filter_by(username=username).first():
        with open('templates/login.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read(), error='Username already exists')
    
    user = User(username=username, email=email)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    logger.info(f"New user registered: {username}")
    with open('templates/login.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read(), success='Account created! Please login.')

@app.route('/guest', methods=['GET', 'POST'])
def guest_login():
    """Login as guest"""
    try:
        import uuid
        guest_username = f"guest_{uuid.uuid4().hex[:8]}"
        
        # Create temporary guest user
        guest = User(username=guest_username, is_guest=True)
        guest.set_password(secrets.token_hex(16))
        
        db.session.add(guest)
        db.session.commit()
        
        login_user(guest)
        logger.info(f"Guest user created: {guest_username}")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Guest login error: {e}")
        import traceback
        traceback.print_exc()
        return f"Error creating guest user: {e}", 500

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = current_user.username
    
    # Delete guest users on logout
    if current_user.is_guest:
        db.session.delete(current_user)
        db.session.commit()
        logger.info(f"Guest user deleted: {username}")
    
    logout_user()
    logger.info(f"User {username} logged out")
    return redirect(url_for('login'))

@app.route('/apply_filter', methods=['POST'])
@login_required
def apply_filter_route():
    """
    Applies a specified filter (sharpen, blur, etc.) to the received base64 image data using Pillow.
    This is non-destructive as the client must always send the original image data.
    """
    data = request.json
    image_data = data.get('image_data') 
    filter_type = data.get('filter_type', '').lower()

    if not image_data or not filter_type:
        return jsonify({'success': False, 'error': 'Missing image data or filter type.'}), 400

    # Filter mapping: Map client string names to Pillow constants
    filter_map = {
        'sharpen': ImageFilter.SHARPEN,
        'blur': ImageFilter.BLUR,
    }

    selected_filter = filter_map.get(filter_type)
    if not selected_filter:
        return jsonify({'success': False, 'error': f'Invalid filter type: {filter_type}'}), 400

    # Decode the base64 string back into a PIL Image object
    img, error_message = decode_base64_image(image_data)
    if error_message:
        return jsonify({'success': False, 'error': error_message}), 400

    try:
        # Core Pillow processing: Apply the selected filter
        processed_img = img.filter(selected_filter)

        # Encode the processed image back to Base64
        buffer = BytesIO()
        processed_img.save(buffer, format="PNG") 
        processed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'processed_image_base64': processed_base64
        })

    except Exception as e:
        return jsonify({'success': False, 'error': f"Pillow Filtering Error: {e}"}), 500


@app.route('/enhance', methods=['POST'])
@login_required
def enhance_route():
    """
    AI-powered image enhancement endpoint
    Accepts: image_data (base64), preset, scale, strength
    Returns: enhanced image as base64 with metadata
    """
    try:
        logger.info("Enhancement request received")
        data = request.json
        
        if data is None:
            logger.error("No JSON data received")
            return jsonify({
                'success': False,
                'error': 'No JSON data received',
                'error_code': 'INVALID_INPUT'
            }), 400
        
        # Extract parameters
        image_data = data.get('image_data')
        preset = data.get('preset', 'general')
        scale = data.get('scale', 1)
        strength = data.get('strength', 80)
        
        # Validate required fields
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'Missing image data',
                'error_code': 'INVALID_INPUT'
            }), 400
        
        # Validate preset
        if preset not in ['general', 'portrait', 'landscape']:
            return jsonify({
                'success': False,
                'error': f'Invalid preset: {preset}. Must be general, portrait, or landscape',
                'error_code': 'INVALID_INPUT'
            }), 400
        
        # Validate scale
        if scale not in [1, 2, 4]:
            return jsonify({
                'success': False,
                'error': f'Invalid scale: {scale}. Must be 1, 2, or 4',
                'error_code': 'INVALID_INPUT'
            }), 400
        
        # Validate strength
        if not isinstance(strength, (int, float)) or not 0 <= strength <= 100:
            return jsonify({
                'success': False,
                'error': f'Invalid strength: {strength}. Must be between 0 and 100',
                'error_code': 'INVALID_INPUT'
            }), 400
        
        # Decode image
        logger.info("Decoding image...")
        img, error_message = decode_base64_image(image_data)
        if error_message:
            logger.error(f"Image decode error: {error_message}")
            return jsonify({
                'success': False,
                'error': error_message,
                'error_code': 'INVALID_INPUT'
            }), 400
        
        # Check image size to prevent memory issues
        width, height = img.size
        max_pixels = 4000 * 4000  # 16 megapixels max
        if width * height > max_pixels:
            logger.warning(f"Image too large: {width}x{height}")
            return jsonify({
                'success': False,
                'error': f'Image too large ({width}x{height}). Maximum size is 4000x4000 pixels.',
                'error_code': 'IMAGE_TOO_LARGE'
            }), 400
        
        logger.info(f"Image size: {width}x{height}, preset: {preset}, scale: {scale}, strength: {strength}")
        
        # Get enhancement engine
        logger.info("Getting enhancement engine...")
        engine = get_enhancement_engine()
        
        # Perform enhancement with timeout handling
        try:
            logger.info("Starting enhancement process...")
            enhanced_img, metadata = engine.enhance(img, preset, scale, int(strength))
            logger.info("Enhancement completed successfully")
        except TimeoutError:
            logger.error("Enhancement timed out")
            return jsonify({
                'success': False,
                'error': 'Enhancement processing timed out (>60s)',
                'error_code': 'TIMEOUT'
            }), 504
        except MemoryError:
            logger.error("Out of memory during enhancement")
            return jsonify({
                'success': False,
                'error': 'Image too large to process. Try a smaller image or lower scale.',
                'error_code': 'OUT_OF_MEMORY'
            }), 507
        except Exception as e:
            logger.error(f"Enhancement error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Enhancement failed: {str(e)}',
                'error_code': 'MODEL_ERROR'
            }), 500
        
        # Encode enhanced image to base64
        logger.info("Encoding enhanced image...")
        buffer = BytesIO()
        enhanced_img.save(buffer, format="PNG")
        enhanced_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        logger.info(f"Enhancement complete. Output size: {len(enhanced_base64)} bytes")
        
        return jsonify({
            'success': True,
            'enhanced_image_base64': enhanced_base64,
            'metadata': metadata
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in enhance endpoint: {e}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'error_code': 'SERVER_ERROR'
        }), 500


if __name__ == '__main__':
    # host='0.0.0.0' allows access from any device on your network
    # For public access, consider using ngrok or deploying to a cloud service
    app.run(debug=True, host='0.0.0.0', port=5000)