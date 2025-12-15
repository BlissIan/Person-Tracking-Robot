from flask import Flask, Response
import queue

app = Flask(__name__)

def WebServer(frame_queue):

    def gen():
        while True:
            try:
                frame = frame_queue.get(timeout=1)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' +
                       frame + b'\r\n')
            except queue.Empty:
                continue

    @app.route('/')
    def video_feed():
        return Response(
            gen(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

    print("Web stream on port 8080")
    app.run(host='0.0.0.0', port=8080, threaded=True)
