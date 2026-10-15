from PIL import Image

from engine.image import adjust, crop, flip, resize, rotate


def test_image_transformations():
    image = Image.new("RGB", (10, 8), "white")
    assert crop(image, (2, 1, 8, 6)).size == (6, 5)
    assert resize(image, 20, 16).size == (20, 16)
    assert rotate(image, 90).size == (8, 10)
    assert flip(image, "horizontal").size == image.size
    assert adjust(image, brightness=0.5, contrast=1.5, grayscale=True).mode == "RGB"
