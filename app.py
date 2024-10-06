from flask import Flask, render_template, Response
import cv2
import os
from datetime import datetime, timedelta
from flask import send_file, request

app = Flask(__name__)

# Configuration
VIDEO_SAVE_DURATION = timedelta(minutes=5)  # Duration to save video for playback

def gen_frames(save_video=False):
    camera = cv2.VideoCapture(0)  # Use the first camera
    if save_video:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
        start_time = datetime.now()

    while True:
        if save_video and (datetime.now() - start_time) > VIDEO_SAVE_DURATION:
            break
        success, frame = camera.read()  # Read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            if save_video:
                out.write(frame)

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Concatenate frame one by one and show result

    if save_video:
        out.release()
    camera.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/playback')
def playback():
    return render_template('playback.html')

@app.route('/video_feed_playback')
def video_feed_playback():
    return Response(gen_frames(save_video=True), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/download_image')
def download_image():
    camera = cv2.VideoCapture(0)
    success, frame = camera.read()
    if success:
        filename = 'capture.jpg'
        cv2.imwrite(filename, frame)
        camera.release()
        return send_file(filename, as_attachment=True)
    camera.release()
    return "Failed to capture image", 500

@app.route('/download_video')
def download_video():
    return send_file('output.avi', as_attachment=True)
    app.run(host='0.0.0.0', port=8080)
