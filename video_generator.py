import openai
import re, os
import shutil
from gtts import gTTS
from moviepy.editor import *
from urllib.request import urlretrieve
from api_key import API_KEY
import time

# Thiết lập API key
openai.api_key = API_KEY

def ensure_directories_exist():
      # Xóa các thư mục nếu đã tồn tại và tạo mới
    for folder in ["audio", "images", "videos"]:
        if os.path.exists(folder):
            for attempt in range(3):  # Thử xóa các tệp trong thư mục 3 lần
                try:
                    for root, dirs, files in os.walk(folder):
                        for file in files:
                            os.remove(os.path.join(root, file))
                    if not os.listdir(folder):
                        os.rmdir(folder)  # Xóa thư mục nếu nó rỗng
                    break
                except PermissionError:
                    print(f"Folder {folder} is in use, retrying...")
                    time.sleep(1)  # Đợi 1 giây trước khi thử lại

        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # Xóa các tệp tạm thời nếu tồn tại
    temp_files = ["final_video.mp4", "final_videoTEMP_MPY_wvf_snd.mp3"]
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            for attempt in range(3):  # Thử xóa tệp 3 lần
                try:
                    os.remove(temp_file)
                    break
                except PermissionError:
                    print(f"File {temp_file} is in use, retrying...")
                    time.sleep(1)  # Đợi 1 giây trước khi thử lại

def process_paragraphs(paragraphs):
    for i, para in enumerate(paragraphs[:-1], start=1):
        if para.strip():
            try:
                response = openai.Image.create(
                    prompt=para.strip(),
                    n=1,
                    size="1024x1024"
                )
                image_url = response['data'][0]['url']
                urlretrieve(image_url, f"images/image{i}.jpg")
                
                tts = gTTS(text=para, lang='vi', slow=False)
                tts.save(f"audio/voiceover{i}.mp3")

                create_video(i, para)
                print(f"The Video{i} Has Been Successfully Generated.")
            except Exception as e:
                print(f"Error generating content for paragraph {i}: {e}")

def create_video(index, text):
    # Tạo video từ hình ảnh và âm thanh
    image_clip = ImageClip(f"images/image{index}.jpg").set_duration(5)
    audio_clip = AudioFileClip(f"audio/voiceover{index}.mp3")
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.write_videofile(f"videos/video{index}.mp4", codec="libx264", fps=24)
def process_text_file():
    # Đọc nội dung tệp generated_text.txt
    with open("generated_text.txt", "r", encoding='utf-8') as file:
        text = file.read()

    # Chia văn bản thành các đoạn dựa trên dấu phẩy và dấu chấm
    paragraphs = re.split(r"[.]", text)

    ensure_directories_exist()
    process_paragraphs(paragraphs)

    # Kết hợp tất cả các video thành một video cuối cùng
    video_clips = [VideoFileClip(f"videos/video{i}.mp4") for i in range(1, len(paragraphs))]
    final_video = concatenate_videoclips(video_clips)
    final_video.write_videofile("final_video.mp4", codec="libx264", audio_codec='aac', temp_audiofile='final_video_TEMP_AUDIO.m4a', remove_temp=True)
if __name__ == "__main__":
    process_text_file()
