"""
AI Image Enhancement Engine
Uses PIL for image quality improvement and upscaling
Note: This is a simplified version that works without complex AI dependencies
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat, ImageChops
import logging
from typing import Tuple
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancementEngine:
    """
    Image enhancement engine using PIL and OpenCV
    """
    
    def __init__(self):
        """Initialize the enhancement engine"""
        logger.info("Enhancement Engine initialized (PIL/OpenCV-based)")
    
    def blur_background(self, image: Image.Image, blur_strength: int = 15) -> Tuple[Image.Image, dict]:
        """
        Apply background blur effect (portrait mode style)
        Uses edge detection to identify subject and blur background
        
        Args:
            image: PIL Image to process
            blur_strength: Blur intensity (1-30)
        
        Returns:
            Tuple of (blurred PIL Image, metadata dict)
        """
        start_time = time.time()
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create edge detection mask to identify subject
            # Subjects typically have more edges/details than backgrounds
            edges = image.filter(ImageFilter.FIND_EDGES)
            edges_gray = edges.convert('L')
            
            # Enhance edges to create better mask
            enhancer = ImageEnhance.Contrast(edges_gray)
            edges_enhanced = enhancer.enhance(3.0)
            
            # Threshold to create binary mask (subject vs background)
            # Higher values = more area considered as subject
            threshold = 30
            mask = edges_enhanced.point(lambda x: 255 if x > threshold else 0)
            
            # Dilate mask to include more of the subject
            mask = mask.filter(ImageFilter.MaxFilter(size=15))
            
            # Smooth mask edges for natural transition
            mask = mask.filter(ImageFilter.GaussianBlur(radius=10))
            
            # Create blurred version of entire image
            blurred = image.filter(ImageFilter.GaussianBlur(radius=blur_strength))
            
            # Composite: use original where mask is white (subject), blurred where black (background)
            result = Image.composite(image, blurred, mask)
            
            processing_time = time.time() - start_time
            
            metadata = {
                'processing_time': round(processing_time, 2),
                'effect': 'background_blur',
                'blur_strength': blur_strength,
                'original_dimensions': [image.width, image.height],
                'output_dimensions': [result.width, result.height]
            }
            
            logger.info(f"Background blur complete in {processing_time:.2f}s")
            
            return result, metadata
            
        except Exception as e:
            logger.error(f"Background blur error: {e}")
            raise
    
    def enhance(
        self, 
        image: Image.Image, 
        preset: str = 'general', 
        scale: int = 1, 
        strength: int = 80
    ) -> Tuple[Image.Image, dict]:
        """
        Enhance an image using PIL and OpenCV
        
        Args:
            image: PIL Image to enhance
            preset: Enhancement preset ('general', 'portrait', 'landscape')
            scale: Upscaling factor (1, 2, or 4)
            strength: Enhancement strength (0-100)
        
        Returns:
            Tuple of (enhanced PIL Image, metadata dict)
        """
        start_time = time.time()
        
        # Validate inputs
        if preset not in ['general', 'portrait', 'landscape']:
            raise ValueError(f"Invalid preset: {preset}")
        if scale not in [1, 2, 4]:
            raise ValueError(f"Invalid scale: {scale}")
        if not 0 <= strength <= 100:
            raise ValueError(f"Invalid strength: {strength}")
        
        original_width, original_height = image.size
        
        # Apply upscaling if requested
        if scale > 1:
            new_width = original_width * scale
            new_height = original_height * scale
            # Use LANCZOS for high-quality upscaling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(f"Upscaled image from {original_width}x{original_height} to {new_width}x{new_height}")
        
        # Apply enhancement based on preset and strength
        if strength > 0:
            image = self._apply_enhancement(image, preset, strength)
        
        # Check dimension limits
        output_width, output_height = image.size
        max_dimension = 4096
        if output_width > max_dimension or output_height > max_dimension:
            logger.warning(f"Output dimensions exceed {max_dimension}px, resizing...")
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            output_width, output_height = image.size
        
        processing_time = time.time() - start_time
        
        metadata = {
            'processing_time': round(processing_time, 2),
            'original_dimensions': [original_width, original_height],
            'output_dimensions': [output_width, output_height],
            'model_used': f'pil_{preset}',
            'preset': preset,
            'scale': scale,
            'strength': strength,
            'device': 'cpu'
        }
        
        logger.info(f"Enhancement complete in {processing_time:.2f}s")
        
        return image, metadata
    
    def _auto_color_balance(self, image: Image.Image) -> Image.Image:
        """
        Automatically balance colors and fix lighting issues
        """
        # Auto-level to improve dynamic range
        image = ImageOps.autocontrast(image, cutoff=1)
        return image
    
    def _reduce_noise(self, image: Image.Image, strength: float) -> Image.Image:
        """
        Reduce noise while preserving details
        """
        if strength > 0.3:
            # Apply median filter for noise reduction
            image = image.filter(ImageFilter.MedianFilter(size=3))
        if strength > 0.6:
            # Additional smoothing for heavy noise
            image = image.filter(ImageFilter.SMOOTH)
        return image
    
    def _enhance_details(self, image: Image.Image, strength: float) -> Image.Image:
        """
        Enhance fine details and texture
        """
        # Apply detail filter
        detailed = image.filter(ImageFilter.DETAIL)
        
        # Blend with original based on strength
        if strength < 1.0:
            image = Image.blend(image, detailed, strength)
        else:
            image = detailed
        
        return image
    
    def _sharpen_advanced(self, image: Image.Image, strength: float) -> Image.Image:
        """
        Advanced sharpening with multiple passes
        """
        # First pass: moderate sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.0 + (0.5 * strength))
        
        # Second pass: unsharp mask for fine details
        if strength > 0.5:
            radius = 1 + int(strength * 2)
            percent = int(100 + (strength * 150))
            image = image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=3))
        
        return image
    
    def _enhance_facial_features(self, image: Image.Image, strength: float) -> Image.Image:
        """
        Enhance facial details - eyes, skin tone, texture (FAST VERSION)
        """
        # Step 1: Auto color balance
        image = self._auto_color_balance(image)
        
        # Step 2: Enhance brightness
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.0 + (0.1 * strength))
        
        # Step 3: Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.0 + (0.2 * strength))
        
        # Step 4: Light sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.0 + (0.5 * strength))
        
        return image
    
    def _enhance_clarity(self, image: Image.Image, strength: float) -> Image.Image:
        """
        Enhance overall clarity, sharpness, and detail (FAST VERSION)
        """
        # Step 1: Auto color balance
        image = self._auto_color_balance(image)
        
        # Step 2: Boost contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.0 + (0.25 * strength))
        
        # Step 3: Enhance color saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.0 + (0.2 * strength))
        
        # Step 4: Sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.0 + (0.6 * strength))
        
        return image

    def _apply_enhancement(self, image: Image.Image, preset: str, strength: int) -> Image.Image:
        """
        Apply enhancement filters based on preset
        
        Args:
            image: PIL Image to enhance
            preset: Enhancement preset
            strength: Enhancement strength (0-100)
        
        Returns:
            Enhanced PIL Image
        """
        # Store original for blending
        original = image.copy()
        
        # Calculate enhancement factor based on strength (0.0 to 1.0)
        factor = strength / 100.0
        
        if preset == 'portrait':
            # Portrait: Enhance facial detail, remove noise, sharpen features naturally
            # Fix lighting, texture, eyes, skin tone, and contrast
            # No over-smoothing, no new elements. Only realistic enhancement.
            logger.info("Applying portrait enhancement with facial detail optimization")
            
            image = self._enhance_facial_features(image, factor)
            
        elif preset == 'landscape':
            # Landscape: Enhance clarity, color balance, brightness, contrast, sharpness (FAST VERSION)
            logger.info("Applying landscape enhancement with clarity optimization")
            
            # Step 1: Auto color balance
            image = self._auto_color_balance(image)
            
            # Step 2: Boost color saturation
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + (0.4 * factor))
            
            # Step 3: Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.0 + (0.35 * factor))
            
            # Step 4: Sharpening
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.0 + (0.6 * factor))
            
        else:  # general
            # General: Enhance clarity, color balance, brightness, contrast, sharpness
            # Reduce noise and improve overall detail and quality
            # Keep the original style of the photo
            logger.info("Applying general enhancement with clarity optimization")
            
            image = self._enhance_clarity(image, factor)
        
        # Natural blending with original to keep realistic look
        if strength < 100:
            # Smooth blend for natural appearance
            alpha = factor * 0.9  # Slightly reduce intensity for more natural look
            image = Image.blend(original, image, alpha)
        
        return image


# Global instance (singleton pattern)
_engine_instance = None

def get_enhancement_engine() -> EnhancementEngine:
    """Get or create the global enhancement engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = EnhancementEngine()
    return _engine_instance
