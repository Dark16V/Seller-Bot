from aiogram.types import BufferedInputFile

async def get_media(file_name: str) -> BufferedInputFile:
    with open(f"media/{file_name}.mp4", "rb") as f:
        img_bytes = f.read()
    return BufferedInputFile(img_bytes, filename=f"{file_name}.mp4")