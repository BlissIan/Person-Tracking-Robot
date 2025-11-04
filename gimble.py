import RPi.GPIO as GPIO
import time
from multiprocessing import Process, Queue
from adafruit_servokit import ServoKit





def Gimble(Queue):

    kit = ServoKit(channels=16, address=0x40)
    kit.servo[0].set_pulse_width_range(500, 2500)
    kit.servo[1].set_pulse_width_range(500, 2500)


    #Define variables
    bottom_angle = 0
    top_angle = 0

    base_angle_b = 90
    base_angle_t = 90

    prev_X_Error = 0
    prev_Y_Error = 0

        
    kp_1 = 0.01 
    ki_1 = 0.015
    kd_1 = 0.01 

    kp_2 = 0.01
    ki_2 = 0.015
    kd_2 = 0.01

    P_term1 = 0
    P_term2 = 0

    I_term_1 = 0
    I_term_2 = 0

    D_term1 = 0
    D_term2 = 0

    X_Error = 0
    Y_Error = 0

    def set_angle_bot(angle):
        """
        Sets the servo angle (0-180 degrees).
        Angle to duty cycle formula: duty_cycle = (angle / 18) + 2.5
        """
        kit.servo[0].angle = angle

    def set_angle_top(angle):
        """
        Sets the servo angle (0-180 degrees).
        Angle to duty cycle formula: duty_cycle = (angle / 18) + 2.5
        """
        kit.servo[1].angle = angle

    try:
        while True:

            cords = Queue.get()
            if cords != 'No_Target':
                X_Error = cords[0]
                Y_Error = cords[1]
            else:
    
                X_Error = X_Error
                Y_Error = Y_Error

            P_term1 = X_Error
            P_term2 = Y_Error

            I_term_1 += X_Error
            I_term_1 = max(-30, min(I_term_1, 30))

            I_term_2 += Y_Error
            I_term_2 = max(-30, min(I_term_2, 30))

            D_term1 = X_Error - prev_X_Error

            D_term2 = Y_Error - prev_Y_Error

            bottom_angle = kp_1 * P_term1 + ki_1 * I_term_1 + kd_1 * D_term1
            
            top_angle = kp_2 * P_term2 + ki_2 * I_term_2 + kd_2 * D_term2

            top_angle = int(max(-60, min(top_angle, 60)))
            bottom_angle = int(max(-90, min(bottom_angle, 90)))

            base_angle_b += bottom_angle
            base_angle_t += top_angle

            base_angle_b = int(max(0, min(base_angle_b, 180)))
            base_angle_t = int(max(40, min(base_angle_t, 180)))
            

            print(f"Y Error: {Y_Error} | Top Angle {base_angle_t}")
            print(f"X Error: {X_Error} | Bottom Angle {base_angle_b}")
            if cords != 'No_Target':
                #only send new angle
                if -1 <  X_Error < 1:
                    pass
                else:
                    set_angle_bot(base_angle_b) 
                
                if -1 < Y_Error < 1:
                    pass 
                else:
                    set_angle_top(base_angle_t)
            else:
                print(f"Waiting for target")
                continue
                

            prev_X_Error = X_Error
            prev_Y_Error = Y_Error

    except KeyboardInterrupt:
        # Clean up GPIO on program exit
        print("Exiting and cleaning up GPIO")
        GPIO.cleanup()

