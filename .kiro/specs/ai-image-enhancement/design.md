# AI Image Enhancement Feature - Design Document

## Overview

This design document outlines the architecture and implementation approach for adding AI-powered image enhancement to the PhotoJS editor. The feature will leverage Real-ESRGAN (Real-Enhanced Super-Resolution Generative Adversarial Network) for general image enhancement and upscaling, with optional GFPGAN integration for portrait-specific face enhancement.

### Key Design Decisions

1. **Model Selection**: Real-ESRGAN for its balance of quality, speed, and ease of integration
2. **Backend Processing**: All AI processing happens server-side to avoid browser limitations
3. **Async Processing**: Non-blocking enhancement with progress feedback
4. **Graceful Degradation**: CPU fallback when GPU is unavailable
5. **Preset-Based Approach**: Simplified UX with predefined enhancement modes

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (Browser)                         │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Enhancement UI │  │ Image Canvas │  │ Compare View    │ │
│  └────────┬───────┘  └──────┬───────┘  └────────┬────────┘ │
│           │                  │                    │          │
│           └──────────────────┴────────────────────┘          │
│                              │                               │
│                    ┌─────────▼─────────┐                    │
│                    │  API Client       │                    │
│                    │  (Fetch/Axios)    │                    │
│                    └─────────┬─────────┘                    │
└──────────────────────────────┼──────────────────────────────┘
                               │ HTTPS/JSON
                               │ (Base64 Image Data)
┌──────────────────────────────▼──────────────────────────────┐
│                    Flask Backend Server                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              /enhance Endpoint                         │ │
│  │  - Receives: image_data, preset, scale, strength      │ │
│  │  - Returns: enhanced_image_base64, metadata           │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │         Enhancement Engine                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │ Image Loader │  │ Model Manager│  │ Post-Process│ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │ │
│  │         │                  │                  │        │ │
│  │         └──────────────────┴──────────────────┘        │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │         AI Models (Real-ESRGAN, GFPGAN)                │ │
│  │  - Loaded on server startup                            │ │
│  │  - GPU/CPU inference                                   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Initiates Enhancement**
   - User selects preset, scale, and strength
   - Clicks "AI Enhance" button
   - UI shows loading indicator

2. **Client → Server**
   - Client sends POST request to `/enhance` endpoint
   - Payload: `{ image_data: "base64...", preset: "general", scale: 2, strength: 80 }`

3. **Server Processing**
   - Decode base64 image to PIL Image
   - Load appropriate model based on preset
   - Run inference (GPU/CPU)
   - Apply strength blending if < 100%
   - Encode result to base64

4. **Server → Client**
   - Return enhanced image as base64
   - Include metadata (processing time, dimensions)

5. **Client Display**
   - Replace editor image with enhanced version
   - Store original for comparison/undo
   - Hide loading indicator

## Components and Interfaces

### Frontend Components

#### 1. Enhancement UI Section (HTML/CSS/JS)

**Location**: New accordion section in sidebar

**Elements**:
- Enhancement preset buttons (General, Portrait, Landscape)
- Scale selector (1x, 2x, 4x)
- Strength slider (0-100%)
- "AI Enhance" primary button
- "Compare" toggle button
- "Undo Enhancement" button
- Processing indicator with progress

**State Management**:
```javascript
const enhancementState = {
    isProcessing: false,
    originalImage: null,
    enhancedImage: null,
    currentPreset: 'general',
    currentScale: 1,
    currentStrength: 80,
    compareMode: false
};
```

#### 2. API Client Module

**Purpose**: Handle communication with Flask backend

**Key Functions**:
```javascript
async function enhanceImage(imageData, preset, scale, strength) {
    // POST to /enhance endpoint
    // Handle response and errors
    // Return enhanced image base64
}

async function checkServerStatus() {
    // Verify AI models are loaded
    // Return available presets and capabilities
}
```

### Backend Components

#### 1. Enhancement Endpoint (`/enhance`)

**Route**: `POST /enhance`

**Request Schema**:
```json
{
    "image_data": "base64_encoded_image",
    "preset": "general|portrait|landscape",
    "scale": 1|2|4,
    "strength": 0-100
}
```

**Response Schema**:
```json
{
    "success": true,
    "enhanced_image_base64": "base64_encoded_result",
    "metadata": {
        "processing_time": 5.2,
        "original_dimensions": [800, 600],
        "output_dimensions": [1600, 1200],
        "model_used": "realesrgan-x2plus"
    }
}
```

**Error Response**:
```json
{
    "success": false,
    "error": "Error message",
    "error_code": "TIMEOUT|INVALID_INPUT|MODEL_ERROR"
}
```

#### 2. Enhancement Engine Class

**Purpose**: Core AI processing logic

**Class Structure**:
```python
class EnhancementEngine:
    def __init__(self):
        self.models = {}
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._load_models()
    
    def _load_models(self):
        # Load Real-ESRGAN models for different scales
        # Load GFPGAN for portrait mode
        pass
    
    def enhance(self, image, preset, scale, strength):
        # Select appropriate model
        # Run inference
        # Apply strength blending
        # Return enhanced PIL Image
        pass
    
    def _blend_images(self, original, enhanced, strength):
        # Blend original and enhanced based on strength
        pass
```

#### 3. Model Manager

**Purpose**: Handle model loading, caching, and selection

**Responsibilities**:
- Load models on server startup
- Cache models in memory
- Select appropriate model based on preset and scale
- Handle GPU/CPU device management

**Model Mapping**:
```python
MODEL_CONFIG = {
    'general': {
        1: None,  # No enhancement
        2: 'RealESRGAN_x2plus',
        4: 'RealESRGAN_x4plus'
    },
    'portrait': {
        1: 'GFPGANv1.4',
        2: 'GFPGANv1.4',  # GFPGAN handles upscaling
        4: 'GFPGANv1.4'
    },
    'landscape': {
        1: None,
        2: 'RealESRGAN_x2plus',
        4: 'RealESRGAN_x4plus'
    }
}
```

## Data Models

### Enhancement Request

```python
@dataclass
class EnhancementRequest:
    image_data: str  # Base64 encoded
    preset: str  # 'general', 'portrait', 'landscape'
    scale: int  # 1, 2, or 4
    strength: int  # 0-100
    
    def validate(self):
        # Validate all fields
        # Raise ValueError if invalid
        pass
```

### Enhancement Result

```python
@dataclass
class EnhancementResult:
    success: bool
    enhanced_image_base64: Optional[str]
    metadata: Dict[str, Any]
    error: Optional[str]
    error_code: Optional[str]
```

## Error Handling

### Client-Side Error Handling

1. **Network Errors**
   - Display: "Unable to connect to enhancement server"
   - Action: Retry button, check server status

2. **Timeout Errors**
   - Display: "Enhancement is taking longer than expected"
   - Action: Option to cancel or continue waiting

3. **Invalid Image Errors**
   - Display: "Image format not supported for enhancement"
   - Action: Suggest supported formats

### Server-Side Error Handling

1. **Model Loading Failures**
   - Log error details
   - Return 503 Service Unavailable
   - Provide fallback message

2. **Out of Memory Errors**
   - Catch CUDA OOM errors
   - Fallback to CPU processing
   - If still fails, suggest smaller image or lower scale

3. **Processing Timeouts**
   - Implement 60-second timeout
   - Clean up resources
   - Return timeout error to client

4. **Invalid Input**
   - Validate all parameters
   - Return 400 Bad Request with specific error
   - Log validation failures

### Error Recovery Strategies

```python
def enhance_with_fallback(image, preset, scale, strength):
    try:
        # Try GPU processing
        return enhance_gpu(image, preset, scale, strength)
    except torch.cuda.OutOfMemoryError:
        # Fallback to CPU
        logger.warning("GPU OOM, falling back to CPU")
        return enhance_cpu(image, preset, scale, strength)
    except Exception as e:
        # Log and re-raise
        logger.error(f"Enhancement failed: {e}")
        raise
```

## Testing Strategy

### Unit Tests

1. **Image Processing Tests**
   - Test base64 encoding/decoding
   - Test image format conversions
   - Test strength blending algorithm
   - Test dimension validation

2. **Model Manager Tests**
   - Test model loading
   - Test model selection logic
   - Test device management (GPU/CPU)
   - Mock model inference

3. **API Endpoint Tests**
   - Test request validation
   - Test response formatting
   - Test error responses
   - Test timeout handling

### Integration Tests

1. **End-to-End Enhancement Flow**
   - Upload image → enhance → download
   - Test all presets
   - Test all scale factors
   - Test strength variations

2. **Compare Mode Tests**
   - Toggle between original and enhanced
   - Verify image switching
   - Test undo functionality

3. **Performance Tests**
   - Measure processing time for different image sizes
   - Test concurrent requests
   - Test memory usage

### Manual Testing Checklist

- [ ] Test with various image formats (JPEG, PNG, WebP)
- [ ] Test with different image sizes (small, medium, large)
- [ ] Test portrait mode with face photos
- [ ] Test landscape mode with nature photos
- [ ] Test general mode with mixed content
- [ ] Verify enhancement quality visually
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test error scenarios (invalid image, server down)
- [ ] Test UI responsiveness during processing
- [ ] Verify downloaded images retain enhancement

## Implementation Notes

### Dependencies

**Python Backend**:
```
torch>=2.0.0
torchvision>=0.15.0
realesrgan>=0.3.0
gfpgan>=1.3.8
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
```

### Model Download

Models will be automatically downloaded on first use:
- Real-ESRGAN x2plus: ~17MB
- Real-ESRGAN x4plus: ~17MB
- GFPGAN v1.4: ~350MB

Total storage: ~400MB

### Performance Considerations

1. **Model Caching**: Keep models in memory after first load
2. **Batch Processing**: Not needed for single-image editor
3. **GPU Memory**: Monitor and implement OOM recovery
4. **Image Size Limits**: Warn users about very large images (>4096px)

### Security Considerations

1. **Input Validation**: Validate image data before processing
2. **Resource Limits**: Implement timeouts and memory limits
3. **Rate Limiting**: Consider adding rate limiting for production
4. **Sanitization**: Ensure base64 data is properly validated

## Future Enhancements

1. **Batch Processing**: Enhance multiple images at once
2. **Custom Models**: Allow users to upload custom enhancement models
3. **Real-time Preview**: Show enhancement preview before full processing
4. **Advanced Controls**: Expose model-specific parameters
5. **Cloud Processing**: Offload to cloud GPU for faster processing
