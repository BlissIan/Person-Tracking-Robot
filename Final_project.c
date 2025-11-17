
/**
 * @file rc_uart_loopback.c
 * @example    rc_uart_loopback
 *
 * This is a test to check read and write operation of UART buses. For this
 * example to work, connect the RX and TX wires of one of the included 4-pin
 * JST-SH pigtails and plug into the UART1 or UART5 headers. You may also elect
 * t0 test UART0 on the debug header or UART2 on the GPS header. The test
 * strings this programs transmits will then loopback to the RX channel.
 */
 
#include <stdio.h>
#include <stdlib.h> // for atoi
#include <string.h>
#include <rc/uart.h>
 
#define BUF_SIZE        32
#define TIMEOUT_S       1
#define BAUDRATE        9600
 

// for motor control
#include <signal.h>
#include <getopt.h>
#include <rc/motor.h>
#include <rc/time.h>
// for motor control 


static void __print_usage(void)
{
        printf("\n");
      	printf("Usage: rc_uart_loopback {bus}\n");
        printf("This sends a short message out the specified bus and then\n");
        printf("reads it back in. This requires connecting RX to TX to make a loopback.\n");
        printf("For Robotics Cape or BeagleBone Blue specify bus 0,1,2 or 5\n");
        printf("\n");
        return;
}

void right_side(double speed) {
	rc_motor_set(1, speed);
//	rc_motor_set(2, speed);
}

void left_side(double speed) {
	rc_motor_set(3, speed);
//	rc_motor_set(4, speed);
}

void drive(double w, double v) {
	// define variables
	double wheelRad = 0.03175; // meters
	double wheelBase = 0.13335;// meters

	// inverse kinematics equations | LEFT +, RIGHT -
	double wL = (v - w * wheelBase / 2) / wheelRad;
	double wR = (v + w * wheelBase / 2) / wheelRad;
	
	// print initial wL and wR (before bounds)
	printf("wL = %f, wR = %f\n", wL, wR);

	// bounds (-14.66 to 14.66)
	double bound = 14.66;

	if(wL > bound) {
	 wL = bound;
	 }

	else if(wL < -bound) {
	 wL = -bound;
	 }

	if(wR > bound) {
	wR = bound;
	}
	
	else if(wR < -bound) {
	wR = -bound;
	}
	
	// map values
	double wR_percent = ((wR - (-bound)) / (bound - (-bound)) * (0.5 - (-0.5)) + (-0.5));
	double wL_percent = ((wL - (-bound)) / (bound - (-bound)) * (0.5 - (-0.5)) + (-0.5));

	// printed values (for testing)
	printf("wL = %f, wR = %f\n", wL, wR);
	printf("wL_percent = %f, wR_percent = %f\n", wL_percent, wR_percent);

	// send mapped values to motors
	right_side(wR_percent);
	left_side(wL_percent);
}



int main()
{
	int bytes = 16;
	int cord=0, cmd=0, dist=0; // dist from target to center, hand guesture command, lidar distance

        uint8_t buf[BUF_SIZE];
        int ret; // return value
        int bus=2;// which bus to use

        if(!(bus==0||bus==1||bus==2||bus==5)){
                __print_usage();
                return -1;
        }

        printf("\ntesting UART bus %d\n\n", bus);
        // disable canonical (0), 1 stop bit (1), disable parity (0)
        if(rc_uart_init(bus, BAUDRATE, TIMEOUT_S, 0,1,0)){
                printf("Failed to rc_uart_init%d\n", bus);
                return -1;
        }
	//initialize motors
	int freq_hz = RC_MOTOR_DEFAULT_PWM_FREQ;
	if(rc_motor_init_freq(freq_hz)) return -1;

        while(1){
	//send
	rc_uart_flush(bus);

        // Read

        memset(buf,0,sizeof(buf));
        ret = rc_uart_read_bytes(bus, buf, bytes);
        if(ret<0) fprintf(stderr,"Error reading bus\n");
        else if(ret==0) printf("timeout reached, %d bytes read\n", ret);
        else{
		//parse recived string
		if(sscanf(buf,"%d,%d,%d", &cord, &cmd, &dist) == 3){
		// printf("Received: Cord =  %d Cmd = %d \n", cord, cmd);
			}
		}

	printf("Cord: %d ", cord);
	printf("CMD: %d ", cmd);
	printf("Dist: %d\n", dist);
	//Motor Code here
	rc_motor_set(3, 0.2); // CH0: all, CH1: back right, CH3: back left
//	right_side(1);
//	left_side(1);
//	drive(-2, 0.15);



	// PID logic, calculating w for given cord
	double turn = cord * 0.01;
	
	// if target is seen, and robot is greter than 130 cm away --> drive towards target
	if (cord != 999 && dist > 130) {
		drive(turn, 0.15);
	}
	// if robot is less than or equal to 130 cm away from the target, and the target is within 10 units of the center of the camera --> break
	else if (dist <= 130 && abs(cord) < 10) { 
		drive(0,0); 
	}
	// if target is not seen --> break
	else {
		drive(0,0);
	}



	
	
	

	}
	

        // close
        rc_uart_close(bus);
       	rc_motor_cleanup();
	return 0;
}

