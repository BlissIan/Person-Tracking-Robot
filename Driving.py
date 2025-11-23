from gpiozero import Motor, PWMOutputDevice
from multiprocessing import Process, Queue



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

    wR_percent = ((wR - (-bound)) / (bound -(-bound)) * (0.5 - (-0.5)) + (-0.5))
    wL_percent = ((wL - (-bound)) / (bound -(-bound)) * (0.5 - (-0.5)) + (-0.5))

    wR_percent = round(wR_percent,2)
    wL_percent = round(wL_percent,2)

    print(f"Right Wheel = {wR_percent} Left Wheel = {wL_percent}")

    right_side(wR_percent)
    left_side(wL_percent)



#Driving logic
def Rover_control(queue1, queue2):
    kp = 0.01
    try:
        while True:
            cords = queue1.get()
            distance = queue2.get()


            print(f"distance: {distance}")

            if cords != 'No_Target':
                X_Error = cords[0]
                Y_Error = cords[1]
                Command = cords[3]
                        
            else:
                X_Error = X_Error
                Y_Error = Y_Error
                Command = 0

            turn = X_Error * kp
            print(f"Turn: {turn}")

            if X_Error != 999 and distance > 130:
                drive(turn, 0.15)
            elif distance <= 130 and abs(X_Error) < 10:
                drive(0,0)
            else:
                drive(0,0)
    except KeyboardInterrupt:
        print("Rover exiting, cleaning GPIO")
        right_pwm.close()
        left_pwm.close()
        right_motor.close()
        left_motor.close()

def Rover_control_test(X_Error, distance):
    kp = 0.01
    try:
        while True:
            
            turn = X_Error * kp
            print(f"Turn: {turn}")

            if X_Error != 999 and distance > 130:
                drive(turn, 0.15)
            elif distance <= 130 and abs(X_Error) < 10:
                drive(0,0)
            else:
                drive(0,0)
    except KeyboardInterrupt:
        print("Rover exiting, cleaning GPIO")
        right_pwm.close()
        left_pwm.close()
        right_motor.close()
        left_motor.close()

