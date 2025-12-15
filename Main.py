from multiprocessing import Process, Queue
from threading import Thread
from gimble import Gimble
from Tracking import Track
from Driving import Rover_control
from View_frame import WebServer


if __name__ == "__main__":
    q1 = Queue()
    q2 = Queue()
    q3 = Queue(maxsize=2)
    
    # Multiprocessing for camera and gimble logic
    Camera_process = Process(target=Track, args=(q1,q3))
    Gimble_process = Process(target=Gimble, args=(q1, q2))
    Rover_drive_thread = Thread(target=Rover_control, args=(q1, q2))
    View_frame = Process(target =WebServer, args=(q3,))
    
    
    try:
        # Start all processes/threads
        Camera_process.start()
        Rover_drive_thread.start()
        Gimble_process.start()
        View_frame.start()
        
        # Wait for camera and gimble processes to finish
        Camera_process.join()

    except KeyboardInterrupt:
        # Graceful exit
        Camera_process.terminate()
        Gimble_process.terminate()
        print("Exiting, cleaning GPIO")
