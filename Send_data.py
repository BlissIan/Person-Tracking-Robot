import threading
import serial
import time
from multiprocessing import Queue

def lidar_reader(distance_holder):
    ser2 = serial.Serial('/dev/ttyAMA1', baudrate=115200, timeout=0.1)
    buffer = bytearray()
    
    while True:
        buffer += ser2.read(ser2.in_waiting or 1)
        while len(buffer) >= 9:
            if buffer[0] == 0x59 and buffer[1] == 0x59:
                frame = buffer[:9]
                buffer = buffer[9:]
                distance_holder[0] = frame[2] + (frame[3] << 8)
            else:
                buffer = buffer[1:]
        time.sleep(0.005)  # small delay to prevent CPU spinning

def send_data(Queue1):
    ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=0.1)
    
    distance_holder = [-1]  # shared between thread and main loop

    # start lidar reading in background thread
    t = threading.Thread(target=lidar_reader, args=(distance_holder,), daemon=True)
    t.start()

    while True:
        Data1 = Queue1.get()  # block here safely, we won’t miss lidar updates

        if Data1 != 'No_Target':
            Cordinate = Data1[0]
            Command = Data1[3]
        else:
            Cordinate = 0
            Command = 2

        dist = distance_holder[0]  # latest lidar value
        data_to_send = f"{Cordinate}, {Command}, {dist}\n"
        ser.write(data_to_send.encode())
        print(f"Sent: {data_to_send.strip()}")
