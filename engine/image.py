"""Pure Pillow image-editing operations used by Image Studio."""

from PIL import Image, ImageEnhance, ImageOps


def crop(image, box):
    """Crop an image using an (left, top, right, bottom) pixel box."""
    left, top, right, bottom = (int(value) for value in box)
    left = max(0, min(left, image.width - 1))
    top = max(0, min(top, image.height - 1))
    right = max(left + 1, min(right, image.width))
    bottom = max(top + 1, min(bottom, image.height))
    return image.crop((left, top, right, bottom))


def resize(image, width, height):
    """Resize with a validated positive target size and high-quality resampling."""
    width, height = int(width), int(height)
    if width < 1 or height < 1:
        raise ValueError("Image dimensions must be positive")
    return image.resize((width, height), Image.Resampling.LANCZOS)


def rotate(image, angle):
    """Rotate around the image center while preserving the complete result."""
    return image.rotate(float(angle), expand=True, resample=Image.Resampling.BICUBIC)


def flip(image, direction):
    """Flip horizontally or vertically."""
    if direction == "horizontal":
        return ImageOps.mirror(image)
    if direction == "vertical":
        return ImageOps.flip(image)
    raise ValueError("Direction must be horizontal or vertical")


def adjust(image, brightness=1.0, contrast=1.0, grayscale=False):
    """Apply non-destructive brightness, contrast, and grayscale adjustments."""
    adjusted = image
    if brightness != 1.0:
        adjusted = ImageEnhance.Brightness(adjusted).enhance(float(brightness))
    if contrast != 1.0:
        adjusted = ImageEnhance.Contrast(adjusted).enhance(float(contrast))
    if grayscale:
        adjusted = ImageOps.grayscale(adjusted).convert("RGB")
    return adjusted
