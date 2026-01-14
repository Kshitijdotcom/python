"""
IMPROVED AI Image Enhancement Engine
Uses PIL + OpenCV for professional-quality image enhancement
Includes: denoise, smart sharpening, better color correction
"""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2
import numpy as np
import logging
from typing import Tuple
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedEnhancementEngine:
    """
    Enhanced image processing with OpenCV + PIL
    """
    
    def __init__(self):
        """Initialize the enhancement engine"""
        logger.info("Improved Enhancement Engine initialized (PIL + OpenCV)")
    
    def _pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    def _cv2_to_pil(self, cv2_image: np.ndarray) -> Image.Image:
        """Convert OpenCV image to PIL format"""
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
    
    def _denoise_image(self, image: Image.Image, strength: float = 0.5) -> Image.Image:
        """
        Advanced noise reduction using OpenCV
        Preserves edges while removing noise
        """
        cv_img = self._pil_to_cv2(image)
        
        # Use fastNlMeansDenoisingColored for color images
        # h: filter strength (higher = more denoising)
        # hColor: color component filter strength
        h = int(10 * strength)
        h_color = int(10 * strength)
        
        denoised = cv2.fastNlMeansDenoisingColored(
            cv_img,
            None,
            h=h,
            hColor=h_color,
            templateWindowSize=7,
            searchWindowSize=21
        )
        
        return self._cv2_to_pil(denoised)
    
    def _auto_color_correct(self, image: Image.Image) -> Image.Image:
        """
        Intelligent auto color correction
        Fixes white balance and exposure
        """
        cv_img = self._pil_to_cv2(image)
        
        # Convert to LAB color space
        lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        lab = cv2.merge([l, a, b])
        
        # Convert back to BGR
        corrected = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return self._cv2_to_pil(corrected)
    
    def _smart_sharpen(self, image: Image.Image, strength: float = 0.7) -> Image.Image:
        """
        Advanced sharpening that preserves natural look
        Uses unsharp mask with edge detection
        """
        cv_img = self._pil_to_cv2(image)
        
        # Create gaussian blur
        kernel_size = 5
        sigma = 1.0
        blurred = cv2.GaussianBlur(cv_img, (kernel_size, kernel_size), sigma)
        
        # Unsharp mask: original + (original - blurred) * amount
        amount = strength * 1.5
        sharpened = cv2.addWeighted(cv_img, 1.0 + amount, blurred, -amount, 0)
        
        # Clip values to valid range
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return self._cv2_to_pil(sharpened)
    
    def _enhance_details(self, image: Image.Image, strength: float = 0.6) -> Image.Image:
        """
        Enhance fine details using bilateral filter
        Preserves edges while enhancing texture
        """
        cv_img = self._pil_to_cv2(image)
        
        # Bilateral filter: smooths while preserving edges
        d = 9  # diameter
        sigma_color = 75
        sigma_space = 75
        smooth = cv2.bilateralFilter(cv_img, d, sigma_color, sigma_space)
        
        # Extract details by subtracting smooth from original
        details = cv2.subtract(cv_img, smooth)
        
        # Enhance details
        enhanced_details = cv2.multiply(details, strength + 1.0)
        
        # Add enhanced details back
        result = cv2.add(cv_img, enhanced_details)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        return self._cv2_to_pil(result)
    
    def _detect_image_quality(self, image: Image.Image) -> dict:
        """
        Analyze image quality metrics
        Returns: brightness, contrast, sharpness scores
        """
        cv_img = self._pil_to_cv2(image)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # Brightness (mean pixel value)
        brightness = float(np.mean(gray) / 255.0)
        
        # Contrast (standard deviation)
        contrast = float(np.std(gray) / 128.0)
        
        # Sharpness (Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = float(laplacian.var() / 1000.0)
        sharpness = min(sharpness, 1.0)  # Normalize
        
        needs_enhancement = brightness < 0.4 or contrast < 0.5 or sharpness < 0.3
        
        return {
            'brightness': round(brightness, 2),
            'contrast': round(contrast, 2),
            'sharpness': round(sharpness, 2),
            'needs_enhancement': 'yes' if needs_enhancement else 'no'
        }

    
    def enhance(
        self, 
        image: Image.Image, 
        preset: str = 'general', 
        scale: int = 1, 
        strength: int = 80
    ) -> Tuple[Image.Image, dict]:
        """
        Enhanced image processing with pre-processing and better algorithms
        
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
        original_image = image.copy()
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # STEP 1: Analyze image quality
        quality_metrics = self._detect_image_quality(image)
        logger.info(f"Image quality: {quality_metrics}")
        
        # STEP 2: Pre-processing - Denoise if needed
        if quality_metrics['sharpness'] < 0.4 or strength > 60:
            denoise_strength = 0.3 if strength < 70 else 0.5
            logger.info(f"Applying denoise (strength: {denoise_strength})")
            image = self._denoise_image(image, denoise_strength)
        
        # STEP 3: Auto color correction
        if quality_metrics['brightness'] < 0.35 or quality_metrics['contrast'] < 0.4:
            logger.info("Applying auto color correction")
            image = self._auto_color_correct(image)
        
        # STEP 4: Upscaling if requested
        if scale > 1:
            new_width = original_width * scale
            new_height = original_height * scale
            # Use LANCZOS for high-quality upscaling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            logger.info(f"Upscaled from {original_width}x{original_height} to {new_width}x{new_height}")
        
        # STEP 5: Apply preset-specific enhancements
        if strength > 0:
            factor = strength / 100.0
            image = self._apply_preset_enhancement(image, preset, factor, quality_metrics)
        
        # STEP 6: Blend with original based on strength
        if strength < 100:
            # Progressive blending for natural look
            blend_factor = (strength / 100.0) * 0.85
            image = Image.blend(original_image.resize(image.size, Image.Resampling.LANCZOS), 
                              image, blend_factor)
        
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
            'model_used': f'improved_{preset}',
            'preset': preset,
            'scale': scale,
            'strength': strength,
            'quality_metrics': quality_metrics,
            'device': 'cpu',
            'enhancements_applied': ['denoise', 'color_correction', 'smart_sharpen']
        }
        
        logger.info(f"Enhancement complete in {processing_time:.2f}s")
        
        return image, metadata
    
    def _apply_preset_enhancement(self, image: Image.Image, preset: str, 
                                  factor: float, quality_metrics: dict) -> Image.Image:
        """
        Apply preset-specific enhancements with quality-aware adjustments
        """
        if preset == 'portrait':
            logger.info("Applying portrait enhancement")
            
            # Gentle brightness adjustment
            if quality_metrics['brightness'] < 0.5:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.0 + (0.1 * factor))
            
            # Moderate contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.0 + (0.15 * factor))
            
            # Smart sharpening for facial details
            image = self._smart_sharpen(image, factor * 0.6)
            
            # Subtle color enhancement
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + (0.1 * factor))
            
        elif preset == 'landscape':
            logger.info("Applying landscape enhancement")
            
            # Vibrant colors for landscapes
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + (0.25 * factor))
            
            # Strong contrast for dramatic effect
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.0 + (0.2 * factor))
            
            # Detail enhancement
            image = self._enhance_details(image, factor * 0.7)
            
            # Sharpening
            image = self._smart_sharpen(image, factor * 0.8)
            
        else:  # general
            logger.info("Applying general enhancement")
            
            # Balanced enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.0 + (0.18 * factor))
            
            # Color boost
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + (0.15 * factor))
            
            # Smart sharpening
            image = self._smart_sharpen(image, factor * 0.7)
            
            # Detail enhancement
            if factor > 0.6:
                image = self._enhance_details(image, factor * 0.5)
        
        return image
    
    def blur_background(self, image: Image.Image, blur_strength: int = 15) -> Tuple[Image.Image, dict]:
        """
        Apply background blur effect (portrait mode style)
        """
        start_time = time.time()
        
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            width, height = image.size
            
            # Create radial gradient mask
            mask = Image.new('L', (width, height), 255)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            
            center_x, center_y = width // 2, height // 2
            max_radius = min(width, height) // 2
            
            steps = 50
            for i in range(steps):
                radius = int(max_radius * (i / steps) * 1.5)
                opacity = int(255 * (1 - (i / steps) ** 0.6))
                draw.ellipse(
                    [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                    fill=opacity
                )
            
            mask = mask.filter(ImageFilter.GaussianBlur(radius=40))
            blurred = image.filter(ImageFilter.GaussianBlur(radius=blur_strength))
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


# Global instance
_improved_engine_instance = None

def get_improved_enhancement_engine() -> ImprovedEnhancementEngine:
    """Get or create the improved enhancement engine instance"""
    global _improved_engine_instance
    if _improved_engine_instance is None:
        _improved_engine_instance = ImprovedEnhancementEngine()
    return _improved_engine_instance
