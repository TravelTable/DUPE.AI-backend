import cloudinary
import cloudinary.uploader
from app.config import settings
from loguru import logger

# Configure Cloudinary using the CLOUDINARY_URL from settings
if settings.CLOUDINARY_URL:
    cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL)
else:
    logger.warning("CLOUDINARY_URL not set in configuration")

def upload_image(image_bytes: bytes, folder: str = "dupe-ai-uploads") -> str:
    """
    Uploads image bytes to Cloudinary and returns the secure URL.
    """
    try:
        response = cloudinary.uploader.upload(
            image_bytes,
            folder=folder,
            resource_type="image"
        )
        return response.get("secure_url")
    except Exception as e:
        logger.error(f"Cloudinary upload failed: {e}")
        raise ValueError(f"Failed to upload image to Cloudinary: {e}")
