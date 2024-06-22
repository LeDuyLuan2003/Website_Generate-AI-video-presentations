from flask import Flask, render_template, request, jsonify, send_file
import openai
import subprocess
import os
from api_key import API_KEY

app = Flask(__name__)

# Thiết lập khóa API của OpenAI
openai.api_key = API_KEY

def generate_text(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "User: " + prompt}
            ],
            max_tokens=300,
            stop=None,
            temperature=0.5,
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating text: {e}")
        return None


# Endpoint xử lý tin nhắn từ người dùng và sinh ra phản hồi từ mô hình text generation
@app.route('/get_response', methods=['POST'])
def get_response():
    if request.method == 'POST':
        user_message = request.form['user_message']  # Lấy tin nhắn từ người dùng
        bot_response = generate_text(user_message)  # Sinh ra phản hồi từ mô hình text generation

        return jsonify(bot_response)
    
# Route hiển thị giao diện chatbox và text-to-video
@app.route('/')
def index():
    return render_template('index.html')

# Route xử lý text-to-video generation
@app.route('/generate-video', methods=['POST'])
def generate_video():
    text = request.form['video_text']
    
    # Lưu văn bản vào tệp generated_text.txt
    with open('generated_text.txt', 'w', encoding='utf-8') as file:
        file.write(text)
    
    # Chạy script video_generator.py
    subprocess.run(['python', 'video_generator.py'])

    # Trả về video dưới dạng Blob
    return send_file('final_video.mp4', as_attachment=True, mimetype='video/mp4')


if __name__ == '__main__':
    app.run(debug=True)
