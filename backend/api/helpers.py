import base64
import uuid

from django.core.files.base import ContentFile


def process_base64_avatar(avatar_data):
    """Обрабатывает аватар в формате base64 и возвращает файл."""
    if isinstance(avatar_data, str) and avatar_data.startswith('data:image'):
        format_part, data_part = avatar_data.split(',', 1)
        file_extension = format_part.split('/')[1].split(';')[0]
        
        file_data = base64.b64decode(data_part)
        
        file_name = f"avatar_{uuid.uuid4().hex}.{file_extension}"
        return ContentFile(file_data, name=file_name)
    
    return avatar_data
