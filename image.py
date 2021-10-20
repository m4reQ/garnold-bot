from PIL import Image
import hashlib
from constants import *

def hash_image(img: Image.Image) -> str:
    img.resize(DEFAULT_IMAGE_SIZE, Image.ANTIALIAS)
    img.convert('L')
    
    return hashlib.md5(img.tobytes()).hexdigest()

def from_file_like(obj) -> Image.Image:
    return Image.open(obj, mode='r')

def hash_bytes(buffer: bytes) -> str:
    return hashlib.md5(buffer).hexdigest()
