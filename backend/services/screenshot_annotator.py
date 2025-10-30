"""Screenshot annotation service for visual recommendations."""

from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class Annotation:
    """Visual annotation on a screenshot."""
    type: str  # 'box', 'arrow', 'label', 'highlight'
    x: int
    y: int
    width: Optional[int] = None
    height: Optional[int] = None
    text: Optional[str] = None
    color: str = "#EF4444"  # Red for issues
    severity: str = "medium"  # low, medium, high


class ScreenshotAnnotator:
    """Service for annotating screenshots with visual indicators."""
    
    SEVERITY_COLORS = {
        "low": "#F59E0B",      # Amber
        "medium": "#EF4444",   # Red
        "high": "#DC2626",     # Dark red
        "success": "#10B981",  # Green
    }
    
    def __init__(self):
        if not PIL_AVAILABLE:
            logger.warning("Pillow not installed. Screenshot annotations disabled.")
        
    def annotate_screenshot(
        self,
        screenshot_base64: str,
        annotations: list[Annotation],
    ) -> Optional[str]:
        """
        Add visual annotations to a screenshot.
        
        Args:
            screenshot_base64: Base64 encoded screenshot
            annotations: List of annotations to draw
            
        Returns:
            Base64 encoded annotated screenshot, or None if annotation fails
        """
        if not PIL_AVAILABLE:
            logger.warning("Cannot annotate screenshot - Pillow not available")
            return None
            
        if not screenshot_base64 or not annotations:
            return screenshot_base64
            
        try:
            # Decode screenshot
            image_data = base64.b64decode(screenshot_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Create drawing context
            draw = ImageDraw.Draw(image, 'RGBA')
            
            # Try to load a font (fallback to default if not available)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Draw each annotation
            for ann in annotations:
                color = self.SEVERITY_COLORS.get(ann.severity, ann.color)
                
                if ann.type == "box":
                    self._draw_box(draw, ann, color)
                elif ann.type == "highlight":
                    self._draw_highlight(draw, ann, color)
                elif ann.type == "arrow":
                    self._draw_arrow(draw, ann, color)
                elif ann.type == "label":
                    self._draw_label(draw, font, ann, color)
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            annotated_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            logger.info(f"✓ Added {len(annotations)} annotations to screenshot")
            return annotated_base64
            
        except Exception as e:
            logger.error(f"Failed to annotate screenshot: {e}")
            return screenshot_base64  # Return original on error
    
    def _draw_box(self, draw: ImageDraw.ImageDraw, ann: Annotation, color: str):
        """Draw a bounding box."""
        if ann.width and ann.height:
            # Draw semi-transparent fill
            fill_color = self._hex_to_rgba(color, alpha=30)
            draw.rectangle(
                [ann.x, ann.y, ann.x + ann.width, ann.y + ann.height],
                fill=fill_color,
                outline=color,
                width=3
            )
    
    def _draw_highlight(self, draw: ImageDraw.ImageDraw, ann: Annotation, color: str):
        """Draw a semi-transparent highlight overlay."""
        if ann.width and ann.height:
            fill_color = self._hex_to_rgba(color, alpha=50)
            draw.rectangle(
                [ann.x, ann.y, ann.x + ann.width, ann.y + ann.height],
                fill=fill_color
            )
    
    def _draw_arrow(self, draw: ImageDraw.ImageDraw, ann: Annotation, color: str):
        """Draw an arrow pointing to a location."""
        # Simple arrow: vertical line with arrowhead
        arrow_length = 60
        start_y = ann.y - arrow_length
        
        # Draw line
        draw.line(
            [(ann.x, start_y), (ann.x, ann.y)],
            fill=color,
            width=4
        )
        
        # Draw arrowhead (triangle)
        arrow_size = 10
        draw.polygon(
            [
                (ann.x, ann.y),
                (ann.x - arrow_size, ann.y - arrow_size),
                (ann.x + arrow_size, ann.y - arrow_size)
            ],
            fill=color
        )
    
    def _draw_label(self, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, ann: Annotation, color: str):
        """Draw a text label with background."""
        if not ann.text:
            return
            
        # Calculate text size (for older Pillow versions, use textsize if available)
        try:
            bbox = draw.textbbox((0, 0), ann.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback for older Pillow
            text_width, text_height = draw.textsize(ann.text, font=font)
        
        padding = 8
        
        # Draw background rectangle
        bg_color = self._hex_to_rgba(color, alpha=220)
        draw.rectangle(
            [
                ann.x - padding,
                ann.y - padding,
                ann.x + text_width + padding,
                ann.y + text_height + padding
            ],
            fill=bg_color
        )
        
        # Draw text
        draw.text((ann.x, ann.y), ann.text, fill="white", font=font)
    
    def _hex_to_rgba(self, hex_color: str, alpha: int = 255) -> tuple:
        """Convert hex color to RGBA tuple."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, alpha)


# Singleton instance
_annotator = None

def get_annotator() -> ScreenshotAnnotator:
    """Get or create the screenshot annotator instance."""
    global _annotator
    if _annotator is None:
        _annotator = ScreenshotAnnotator()
    return _annotator
