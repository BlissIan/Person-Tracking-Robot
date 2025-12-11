from gpiozero import Motor, PWMOutputDevice
from multiprocessing import Process, Queue
import time



right_motor = Motor(forward=6, backward=5)
right_pwm = PWMOutputDevice(26)
right_pwm.value = 0

left_motor = Motor(forward=25, backward=24)
left_pwm = PWMOutputDevice(23)
left_pwm.value = 0

#Right side speed function
def right_side(speed):
    if speed > 0:
        right_motor.forward()
        right_pwm.value = abs(speed)
    elif speed < 0:
        right_motor.backward()
        right_pwm.value = abs(speed)
    else:
        right_pwm.value = abs(speed)

   

#Left side speed function
def left_side(speed):
    if speed > 0:
        left_motor.forward()
        left_pwm.value = abs(speed)
    elif speed < 0:
        left_motor.backward()
        left_pwm.value = abs(speed)
    else:
        left_pwm.value = abs(speed)

#Driving using inverse kinamatics
def drive(w, v):
    wheelRad = 0.03175
    wheelBase = 0.13335

    wL = (v - w * wheelBase / 2) / wheelRad
    wR = (v + w * wheelBase / 2) / wheelRad

    bound = 14.66
    output_bound = 1

    #Bound left wheel
    if wL > bound:
        wL = bound
    elif wL < -bound:
        wL = -bound

    #Bound Right wheel
    if wR > bound:
        wR = bound
    elif wR < -bound:
        wR = -bound

    wR_percent = ((wR - (-bound)) / (bound -(-bound)) * (output_bound - (-output_bound)) + (-output_bound))
    wL_percent = ((wL - (-bound)) / (bound -(-bound)) * (output_bound - (-output_bound)) + (-output_bound))

    wR_percent = round(wR_percent,2)
    wL_percent = round(wL_percent,2)

    print(f"Right Wheel = {wR_percent} Left Wheel = {wL_percent}")

    right_side(wR_percent)
    left_side(wL_percent)



#Driving logic
def Rover_control(queue1, queue2):
    kp = 0.007
    ki = 0.001
    kd = 0.005

    i_term = 0
    d_term = 0
    p_term = 0
    prev_error = 0
    X_Error = 0
    Y_Error = 0
    Command = 0

    try:
        while True:
            
            cords = queue1.get() 
            distance = queue2.get()

            print(f"cords: {cords}")

            if cords != 'No_Target':
                X_Error = cords[0]        
            else:
                X_Error = X_Error
                


            p_term = X_Error

            i_term += X_Error
            i_term = max(-50, min(i_term, 50))

            d_term = X_Error - prev_error

            turn = p_term * kp + i_term * ki + d_term *kd

            print(f"Turn: {turn}")
            prev_error = X_Error
            if cords != 'No_Target':
                if distance <= 100: #is to close back up
                    drive(0,-0.3)
                elif distance > 130:
                    drive(turn, 0.3)
                elif 100 < distance <= 130 and abs(X_Error) < 10: #if in good range stay put
                    drive(0,0)
                else:
                    drive(0,0)
            else:
                drive(0,0)
                print("Stop, no target detected")
                continue

    except KeyboardInterrupt:
        print("Rover exiting, cleaning GPIO")
        right_pwm.close()
        left_pwm.close()
        right_motor.close()
        left_motor.close()


