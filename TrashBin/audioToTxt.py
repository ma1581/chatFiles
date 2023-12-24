from faster_whisper import WhisperModel
import psutil
from environment import env
model_size = "large-v3"

file_loc="/home/ma1581/projects/chatFiles/Data/TempFiles/audio.mp3"

print(file_loc,model_size)
memory_info = psutil.virtual_memory()
print(memory_info.used / (1024 * 1024))
model = WhisperModel(model_size, device="cuda", compute_type="float16")
segments, info = model.transcribe(file_loc, beam_size=5)
data=""
for i in segments:
    data+=" "+i.text
print(data)


