import RPi.GPIO as GPIO
import threading
from time import sleep
from flask import Flask, request
import pigpio

GPIO.setwarnings(False)
# left weel
in1 = 5
in2 = 6
# right weel
in3 = 17
in4 = 27

# arm controller
# elbow(left) servo
elbow_pin = 19
# gripper servo
gripper_pin = 13
# base sevo
base_pin = 12
# shoulder(rigt) servo
shoulder_pin = 18



class arm_control():
    
    def __init__(self):
        
        # 500 ~ 2400
        self.angles = [1300, 2200, 1450, 1400]
        self.change_pulsewidth = 1

        self.elbow_servo = pigpio.pi()
        self.elbow_servo.set_mode(elbow_pin, pigpio.OUTPUT)
        self.elbow_servo.set_PWM_frequency(elbow_pin, 50)
        
        self.gripper_servo = pigpio.pi()
        self.gripper_servo.set_mode(gripper_pin, pigpio.OUTPUT)
        self.gripper_servo.set_PWM_frequency(gripper_pin, 50)
        
        self.base_servo = pigpio.pi()
        self.base_servo.set_mode(base_pin, pigpio.OUTPUT)
        self.base_servo.set_PWM_frequency(base_pin, 50)
        
        self.shoulder_servo = pigpio.pi()
        self.shoulder_servo.set_mode(shoulder_pin, pigpio.OUTPUT)
        self.shoulder_servo.set_PWM_frequency(shoulder_pin, 50)
        
        
        # set initial angle
        self.elbow_servo.set_servo_pulsewidth(elbow_pin, self.angles[0])
        self.gripper_servo.set_servo_pulsewidth(gripper_pin, self.angles[1])
        self.base_servo.set_servo_pulsewidth(base_pin, self.angles[2])
        self.shoulder_servo.set_servo_pulsewidth(shoulder_pin, self.angles[3])
        
    def update(self, mode):
        
        if mode == 'f':
            if self.angles[0] + self.change_pulsewidth <= 1900:
                self.angles[0] += self.change_pulsewidth
                self.elbow_servo.set_servo_pulsewidth(elbow_pin, self.angles[0])
        
        elif mode == 'b':
            if self.angles[0] - self.change_pulsewidth >= 1300:
                self.angles[0] -= self.change_pulsewidth
                self.elbow_servo.set_servo_pulsewidth(elbow_pin, self.angles[0])
  
        elif mode == 'c':
            if self.angles[1] + self.change_pulsewidth <= 2200:
                self.angles[1] += self.change_pulsewidth
                self.gripper_servo.set_servo_pulsewidth(gripper_pin, self.angles[1])
        
        elif mode == 'o':
            if self.angles[1] - self.change_pulsewidth >= 800:
                self.angles[1] -= self.change_pulsewidth
                self.gripper_servo.set_servo_pulsewidth(gripper_pin, self.angles[1])
            
        elif mode == 'l':
            if self.angles[2] + self.change_pulsewidth <= 2100:
                self.angles[2] += self.change_pulsewidth
                self.base_servo.set_servo_pulsewidth(base_pin, self.angles[2])
            
        elif mode == 'r':
            if self.angles[2] - self.change_pulsewidth >= 800:
                self.angles[2] -= self.change_pulsewidth
                self.base_servo.set_servo_pulsewidth(base_pin, self.angles[2])

        
        elif mode == 'd':
            if self.angles[3] + self.change_pulsewidth <= 2400:
                self.angles[3] += self.change_pulsewidth
                self.shoulder_servo.set_servo_pulsewidth(shoulder_pin, self.angles[3])

        
        elif mode == 'u':
            if self.angles[3] - self.change_pulsewidth >= 1400:
                self.angles[3] -= self.change_pulsewidth
                self.shoulder_servo.set_servo_pulsewidth(shoulder_pin, self.angles[3])
                print(self.angles[3] )
        elif mode == 's':
           pass

class all_control():
    
    def __init__(self):
        
        GPIO.setmode(GPIO.BCM)
    
        """
        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(in3, GPIO.OUT)
        GPIO.setup(in4, GPIO.OUT)
        """
    
        self.arm_control = arm_control()
        
        self.car_control_data = -1
        self.arm_control_data = -1
    
    def stop_GPIO(self):
        self.arm_control.elbow_servo.stop()
        self.arm_control.gripper_servo.stop()
        self.arm_control.base_servo.stop()
        self.arm_control.shoulder_servo.stop()
    
    def car_control(self, mode):
    
        if mode == 'f':
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)
        elif mode == 'b':
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.HIGH)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.HIGH)
        elif mode == 'l':
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.L)
        elif mode == 'r':
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)
        elif mode == 's':
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)

    def arm_controller(self):
    
        while(True):
            self.arm_control.update(self.arm_control_data)
            sleep(0.005)
    
    def car_controller(self):
        pass
    
    def update_controll_data(self, car_controll, arm_controll):
        self.car_control_data = car_controll
        self.arm_control_data = arm_controll
    
    def __del__(self):
        GPIO.cleanup()
        

class API_Service():
    
    def __init__(self, host= "127.0.0.1", port= 5000):
        
        
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        
        
        self.all_controller = all_control()
        
        @self.app.route("/", methods=['GET'])
        def control():
            
            car_controll = -1
            arm_controll = -1
            data = request.args
                    
            if "car" in data.keys():
                car_controll = data["car"]
            if "arm" in data.keys():
                arm_controll = data["arm"]
            
            self.all_controller.update_controll_data(car_controll, arm_controll)
            return f"<h1> Ok, receive car: {car_controll}, arm: {arm_controll} </h1>"

    def api_start(self):
        self.app.run(host= self.host, port= self.port)

    def controller(self):
        
        thread_arm_controller = threading.Thread(target = self.all_controller.arm_controller())
        thread_arm_controller.start()
        
        #thread_car_controller = threading.Thread(target = self.all_controller.car_controller())
        #thread_car_controller.start()
   

if __name__ == "__main__":
   
    # open API service
    api_service = API_Service("192.168.0.104")
    thread_api_service = threading.Thread(target = api_service.api_start)
    thread_api_service.start()
    
    # arm & car controller
    controller = threading.Thread(target = api_service.controller)
    controller.start()
