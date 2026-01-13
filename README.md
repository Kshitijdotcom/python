# PhotoCrest - Professional AI-Powered Image Enhancement Platform (Updated 2025-01-13)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![PIL](https://img.shields.io/badge/PIL-Pillow-orange.svg)](https://pillow.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

PhotoCrest is a sophisticated, browser-based image enhancement platform that combines real-time CSS filters with advanced AI-powered processing algorithms. This professional-grade application allows users to upload, edit, and enhance images through an intuitive interface without requiring any software installation.

![PhotoCrest Interface](https://via.placeholder.com/800x400/0a0a0a/c9a961?text=PhotoCrest+Professional+Photo+Editor)

## ✨ Features

### 🎨 **Advanced Image Enhancement**
- **Real-time CSS Filters**: Instant visual feedback for basic adjustments
- **AI-Powered Enhancement**: Server-side processing with multiple presets
- **Before/After Split View**: Professional comparison slider
- **Smart Auto-Adjust**: Automatic image analysis and optimization

### 🔧 **Professional Tools**
- **Dual-Mode Clarity**: CSS-based instant clarity + advanced server processing
- **Enhancement Presets**: Portrait, Landscape, and General optimization
- **Undo/Redo System**: 50-state history with keyboard shortcuts
- **Quick Enhancement Buttons**: One-click presets for common adjustments

### 🎯 **User Experience**
- **Drag & Drop Upload**: Seamless image loading
- **Clipboard Support**: Paste images directly (Ctrl+V)
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Professional UI**: Dark theme with golden accents

### 🔐 **Security & Authentication**
- **User Management**: Registration, login, and guest mode
- **Session Security**: Secure authentication with automatic cleanup
- **Input Validation**: Comprehensive server-side validation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/photocrest.git
cd photocrest
```

2. **Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python image_editor_server.py
```

5. **Open your browser:**
Navigate to `http://localhost:5000`

## 🛠️ Technology Stack

### **Frontend**
- **HTML5 & CSS3**: Modern responsive design with CSS Grid and Flexbox
- **Vanilla JavaScript**: Advanced DOM manipulation and async processing
- **CSS Custom Properties**: Dynamic filter system with real-time feedback
- **Canvas API**: High-quality image rendering and download functionality

### **Backend**
- **Python Flask**: RESTful API architecture with comprehensive error handling
- **PIL (Pillow)**: Advanced image processing with multi-pass algorithms
- **SQLite**: User authentication and session management
- **Flask-Login**: Secure user authentication with guest mode support

### **Image Processing**
- **Multi-pass Sharpening**: Unsharp mask with optimized parameters
- **Adaptive Contrast Enhancement**: CLAHE-like algorithms
- **Edge Enhancement**: Selective detail enhancement
- **Color Space Optimization**: RGB channel processing

## 📁 Project Structure

```
photocrest/
├── index.html                 # Main application interface
├── image_editor_server.py     # Flask backend server
├── enhancement_engine.py      # AI image processing engine
├── models.py                  # Database models
├── requirements.txt           # Python dependencies
├── templates/
│   └── login.html            # Authentication page
├── instance/
│   └── users.db              # SQLite database
├── backup/                   # Backup files
├── utils/                    # Development utilities
└── .kiro/                    # Kiro AI development specs
```

## 🎮 Usage

### **Basic Editing**
1. **Upload Image**: Click "Upload Image" or drag & drop
2. **Adjust Filters**: Use sliders for brightness, contrast, saturation, etc.
3. **Apply Presets**: Click quick enhancement buttons
4. **Download**: Save your enhanced image

### **Advanced Features**
- **Before/After View**: Toggle split view to compare original vs edited
- **AI Enhancement**: Use preset-specific optimization algorithms
- **Undo/Redo**: Use Ctrl+Z/Ctrl+Y or click buttons
- **Auto-Adjust**: Let AI analyze and optimize your image automatically

### **Keyboard Shortcuts**
- `Ctrl+V`: Paste image from clipboard
- `Ctrl+Z`: Undo last action
- `Ctrl+Y` or `Ctrl+Shift+Z`: Redo action

## 🔧 API Endpoints

### **Image Processing**
- `POST /enhance` - AI-powered image enhancement
- `POST /clarity` - Advanced clarity processing
- `POST /apply_filter` - Apply specific filters
- `POST /blur_background` - Portrait mode background blur

### **Authentication**
- `GET/POST /login` - User authentication
- `POST /register` - User registration
- `GET/POST /guest` - Guest mode access
- `GET /logout` - User logout

## 🎨 Enhancement Algorithms

### **Portrait Mode**
- Facial feature enhancement
- Skin tone optimization
- Adaptive contrast (CLAHE-like)
- Multi-pass sharpening

### **Landscape Mode**
- Vibrant color enhancement
- Edge sharpening
- Dramatic contrast improvements
- Texture enhancement

### **General Mode**
- Multi-pass clarity enhancement
- Unsharp masking
- Detail preservation
- Color balance optimization

## 🚀 Deployment

### **Local Development**
```bash
python image_editor_server.py
```

### **Production Deployment**
The application is ready for deployment on:
- **Render**: `render.yaml` configuration included
- **Heroku**: `Procfile` and `runtime.txt` included
- **Railway**: Direct deployment support
- **PythonAnywhere**: WSGI compatible

### **Environment Variables**
```bash
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

## 📊 Performance

- **Processing Speed**: 0.5-30 seconds depending on image size
- **Maximum Resolution**: 4096x4096 pixels (auto-resized)
- **Memory Efficiency**: Optimized for 512MB RAM environments
- **Browser Compatibility**: Modern browsers supporting ES6+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PIL/Pillow**: Powerful Python imaging library
- **Flask**: Lightweight and flexible web framework
- **Inter Font**: Clean and modern typography
- **CSS Grid & Flexbox**: Modern layout techniques

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/yourusername/photocrest/issues) page
2. Create a new issue with detailed information
3. Include browser version and error messages

---

**Built with ❤️ for professional image enhancement**