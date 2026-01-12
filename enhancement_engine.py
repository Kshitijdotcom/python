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
        Uses improved center-weighted detection to identify subject
        
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
            
            width, height = image.size
            
            # Create radial gradient mask - simple and effective
            # Center = sharp (subject), edges = blurred (background)
            mask = Image.new('L', (width, height), 255)
            
            # Apply radial gradient using ImageDraw
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            
            center_x, center_y = width // 2, height // 2
            max_radius = min(width, height) // 2
            
            # Draw concentric circles with decreasing opacity
            # This creates a radial gradient effect
            steps = 50
            for i in range(steps):
                radius = int(max_radius * (i / steps) * 1.5)
                opacity = int(255 * (1 - (i / steps) ** 0.6))
                draw.ellipse(
                    [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                    fill=opacity
                )
            
            # Smooth the mask heavily for natural transition
            mask = mask.filter(ImageFilter.GaussianBlur(radius=40))
            
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
        Advanced noise reduction while preserving details
        """
        if strength > 0.3:
            # Bilateral-like filter: smooth while preserving edges
            # Apply selective smoothing
            smoothed = image.filter(ImageFilter.SMOOTH_MORE)
            # Blend to preserve some texture
            image = Image.blend(image, smoothed, 0.5 * strength)
        
        if strength > 0.6:
            # Additional median filter for heavy noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
        
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
        Enhanced facial details with better algorithms - IMPROVED VERSION
        """
        # Step 1: Gentle auto color balance (less aggressive)
        image = ImageOps.autocontrast(image, cutoff=0.5)
        
        # Step 2: Subtle brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.0 + (0.05 * strength))  # Reduced from 0.08
        
        # Step 3: Moderate contrast boost (much less aggressive)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.0 + (0.12 * strength))  # Reduced from 0.25
        
        # Step 4: Gentle sharpening (preserve natural look)
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.0 + (0.2 * strength))  # Reduced from 0.4
        
        # Step 5: Conservative unsharp mask
        if strength > 0.4:
            radius = 1.0  # Smaller radius
            percent = int(80 * strength)  # Much lower percent
            threshold = 4  # Higher threshold to preserve smooth areas
            image = image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
        
        # Step 6: Very subtle color enhancement
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.0 + (0.08 * strength))  # Reduced from 0.15
        
        return image
    
    def _enhance_natural(self, image: Image.Image, strength: float) -> Image.Image:
        """
        Natural enhancement - very subtle improvements that preserve the original look
        """
        # Step 1: Very gentle auto contrast
        image = ImageOps.autocontrast(image, cutoff=0.2)
        
        # Step 2: Minimal brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.0 + (0.03 * strength))
        
        # Step 3: Subtle contrast boost
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.0 + (0.08 * strength))
        
        # Step 4: Very gentle sharpening
        if strength > 0.5:
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.0 + (0.15 * strength))
        
        # Step 5: Minimal color enhancement
        if strength > 0.6:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + (0.05 * strength))
        
        return image
        """
        Enhanced clarity with advanced algorithms - IMPROVED VERSION
        """
        # Step 1: Gentle auto color balance
        image = ImageOps.autocontrast(image, cutoff=0.5)
        
        # Step 2: Conservative edge enhancement
        if strength > 0.5:
            edges = image.filter(ImageFilter.EDGE_ENHANCE)  # Less aggressive than EDGE_ENHANCE_MORE
            image = Image.blend(image, edges, 0.15 * strength)  # Reduced from 0.3
        
        # Step 3: Moderate contrast (much less aggressive)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.0 + (0.15 * strength))  # Reduced from 0.3
        
        # Step 4: Subtle color enhancement
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.0 + (0.12 * strength))  # Reduced from 0.25
        
        # Step 5: Gentle sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.0 + (0.25 * strength))  # Reduced from 0.5
        
        # Step 6: Conservative unsharp mask
        if strength > 0.6:
            radius = 1.5  # Smaller radius
            percent = int(100 * strength)  # Much lower percent
            threshold = 4  # Higher threshold
            image = image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
        
        # Step 7: Minimal detail enhancement
        if strength > 0.7:
            detailed = image.filter(ImageFilter.DETAIL)
            image = Image.blend(image, detailed, 0.2 * strength)  # Reduced from 0.4
        
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
            # Landscape: Enhanced with better color and detail algorithms - IMPROVED VERSION
            logger.info("Applying landscape enhancement with advanced optimization")
            
            # Step 1: Gentle auto color balance
            image = ImageOps.autocontrast(image, cutoff=0.5)
            
            # Step 2: Moderate color enhancement (much less aggressive)
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + (0.2 * factor))  # Reduced from 0.45
            
            # Step 3: Conservative contrast for natural effect
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.0 + (0.18 * factor))  # Reduced from 0.4
            
            # Step 4: Gentle edge enhancement
            if factor > 0.6:
                edges = image.filter(ImageFilter.EDGE_ENHANCE)  # Less aggressive
                image = Image.blend(image, edges, 0.12 * factor)  # Reduced from 0.25
            
            # Step 5: Moderate sharpening
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.0 + (0.25 * factor))  # Reduced from 0.5
            
            # Step 6: Conservative unsharp mask
            if factor > 0.7:
                radius = 2.0
                percent = int(120 * factor)  # Reduced from 180
                threshold = 4  # Higher threshold
                image = image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))
            
            # Step 7: Minimal brightness boost
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.0 + (0.05 * factor))  # Reduced from 0.1
            
        else:  # general
            # General: Enhanced clarity with better algorithms - IMPROVED VERSION
            logger.info("Applying general enhancement with advanced clarity optimization")
            
            image = self._enhance_clarity(image, factor)
            
            # Additional pass for vibrant look (much more conservative)
            if factor > 0.8:
                # Very subtle saturation boost
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(1.0 + (0.08 * factor))  # Reduced from 0.15
        
        # Natural blending with original to keep realistic look - IMPROVED
        if strength < 100:
            # More conservative blending for natural appearance
            alpha = factor * 0.7  # Reduced from 0.9 for more subtle effect
            image = Image.blend(original, image, alpha)
        else:
            # Even at 100% strength, blend slightly for natural look
            alpha = 0.85
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
