from multiprocessing import Process, Queue
from gimble import Gimble
from Tracking import Track





if __name__ =="__main__":
    q = Queue()


    Camera_process = Process(target=Track, args=(q,))
    Gimble_process = Process(target=Gimble, args=(q,))


    Camera_process.start()
    Gimble_process.start()

    Camera_process.join()
    Gimble_process.join()                                                                                                        
