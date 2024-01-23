import aiofiles
from pydub import AudioSegment 
import threading
async def export_audio(file_path, audio_segment:AudioSegment):
    async with aiofiles.open(file_path, 'wb') as file:
        file.write(audio_segment.raw_data)