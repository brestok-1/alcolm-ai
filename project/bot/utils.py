import base64
import datetime
import os
import tempfile
from io import BytesIO

from PIL import Image
import aiofiles
from fastapi import UploadFile
from fastapi.params import File

from project.bot.models import Report
from project.config import settings


async def generate_ai_report(history: list[str], language: str) -> Report:
    history = list(map(lambda x: {'role': 'user', 'content': x}, history))
    messages = [
        {
            'role': 'system',
            'content': f"""Summarize the key points from the user's messages, organizing the summary into a structured 
        format. Conclude with a brief report that encapsulates the essence of the 
        discussion. Make your answer in {language}"""
        },
        *history
    ]
    chat_completion = await settings.OPENAI_CLIENT.chat.completions.create(
        model="gpt-4-0125-preview",
        temperature=0.4,
        n=1,
        messages=messages
    )
    response = chat_completion.choices[0].message.content
    report = Report()
    report.content = response
    return report


async def encode_file_to_base64(filepath):
    async with aiofiles.open(filepath, 'rb') as file:
        content = await file.read()
        return base64.b64encode(content).decode('utf-8')


async def transcript_audio_from_base64(data: str):
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"voice_record_{current_time}.mp3"
    file_path = str(settings.BASE_DIR / 'project' / 'records' / file_name)
    data_bytes = base64.b64decode(data)
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(data_bytes)
    with open(file_path, 'rb') as f:
        transcript = await settings.OPENAI_CLIENT.audio.transcriptions.create(
            model='whisper-1',
            file=f,
        )
    text = transcript.text
    return text, file_path


async def generate_image_description(image: str, file_format: str) -> str:
    messages = [
        {
            'role': 'system',
            'content': settings.REPORT_PROMPT
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': settings.IMAGE_PROMPT
                },
                {
                    'type': 'image_url',
                    'image_url': {
                        'url': f"data:image/{file_format};base64,{image}",
                        'detail': 'low'
                    }
                }
            ]
        }
    ]
    chat_completion = await settings.OPENAI_CLIENT.chat.completions.create(
        model="gpt-4-vision-preview",
        temperature=0.5,
        n=1,
        messages=messages
    )
    response = chat_completion.choices[0].message.content
    return response


def compress_and_save_image(image_content: bytes, width=768) -> str:
    img = Image.open(BytesIO(image_content))
    orig_width, orig_height = img.size
    new_height = int((orig_height * width) / orig_width)
    resized_img = img.resize((width, new_height), Image.LANCZOS)
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_format = img.format.lower()
    file_path = str(settings.BASE_DIR / 'project' / 'images' / f'image_{current_time}.{file_format}')
    if file_format in ['jpeg', 'jpg']:
        resized_img.save(file_path, 'JPEG', optimize=True, quality=70)
    elif file_format == 'png':
        resized_img.save(file_path, 'PNG', optimize=True, compress_level=7)
    else:
        raise ValueError(f"{file_format.upper()} format is not supported.")
    return file_path
