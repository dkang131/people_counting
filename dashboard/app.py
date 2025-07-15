from flask import Flask, render_template, Response, jsonify
import cv2, threading, time
from counter.counting import get_counter

app = Flask(__name__)

lock = threading.Lock()
main_counter = None
video_capture = None
streaming_thread = None

def video_streaming_thread():
    """
    This function runs in a background thread and continuously
    processes frames from the webcam.
    """
    global main_counter, video_capture, lock

    while True:
        with lock:
            # If the video_capture is None, the stream has been stopped.
            if video_capture is None:
                break
        
        success, frame = video_capture.read()
        if not success:
            print("Failed to read frame from camera. Stopping stream.")
            break
            
        results = main_counter(frame)
        frame_processed = results.plot_im
        if frame_processed is None:
            print("Warning: frame_processed is None after processing.")
            continue

        # Encode the frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame_processed)
        if not ret:
            print("Failed to encode frame.")
            continue
        
        # We need to yield this frame in the gen_frames function,
        # so we'll store it globally.
        with lock:
            app.config['latest_frame'] = buffer.tobytes()

    print("Streaming thread has finished.")


def gen_frames():
    """
    This generator function reads the latest processed frame and
    yields it to the client.
    """
    while True:
        # Wait until the first frame is available
        if 'latest_frame' not in app.config:
            time.sleep(0.1)
            continue
            
        with lock:
            frame_bytes = app.config.get('latest_frame')

        if frame_bytes is None:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        # A small sleep to prevent the browser from overwhelming the server
        # if the stream is very fast.
        time.sleep(1/30) # Aim for 30fps

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_stream', methods=['POST'])
def start_stream():
    global main_counter, video_capture, streaming_thread
    with lock:
        if streaming_thread is None: # Only start if not already running
            print("Starting stream...")
            # Initialize the camera and the counter
            video_capture = cv2.VideoCapture(0)
            if not video_capture.isOpened():
                print("Error: Could not open video stream.")
                video_capture = None
                return jsonify({'status': 'error', 'message': 'Could not open camera.'})
            
            main_counter = get_counter()
            
            # Start the background thread
            streaming_thread = threading.Thread(target=video_streaming_thread, daemon=True)
            streaming_thread.start()
            print("Stream started.")
            return jsonify({'status': 'started'})
    return jsonify({'status': 'already_running'})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    global video_capture, streaming_thread
    
    with lock:
        if video_capture:
            # Signal the thread to stop by setting video_capture to None
            video_capture.release()
            video_capture = None
    
    # Wait for the thread to finish
    if streaming_thread:
        streaming_thread.join()
        streaming_thread = None

    # Clear the last frame
    app.config.pop('latest_frame', None)
    
    print("Stream stopped.")
    return jsonify({'status': 'stopped'})

@app.route('/get_counts')
def get_counts():
    global main_counter
    # Check the global counter object
    if main_counter is not None:
        # Access its attributes directly
        in_count = main_counter.in_count
        out_count = main_counter.out_count
    else:
        # If streaming hasn't started, return 0
        in_count = 0
        out_count = 0
    
    print(f"API returning: IN={in_count}, OUT={out_count}") # This will now print the correct counts
    return jsonify({'in_count': in_count, 'out_count': out_count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3131, debug=False, threaded=True)