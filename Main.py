from multiprocessing import Process, Queue
from threading import Thread
from gimble import Gimble
from Tracking import Track
from Driving import Rover_control

if __name__ == "__main__":
    q1 = Queue()
    q2 = Queue()
    
    # Multiprocessing for camera and gimble logic
    Camera_process = Process(target=Track, args=(q1,))
    Gimble_process = Process(target=Gimble, args=(q1, q2))
    Rover_drive_thread = Thread(target=Rover_control, args=(q1, q2))
    
    try:
        # Start all processes/threads
        Camera_process.start()
        Rover_drive_thread.start()
        Gimble_process.start()
        
        # Wait for camera and gimble processes to finish
        Camera_process.join()

    except KeyboardInterrupt:
        # Graceful exit
        Camera_process.terminate()
        Gimble_process.terminate()
        print("Exiting, cleaning GPIO")
