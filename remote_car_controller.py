import RPi.GPIO as GPIO
import threading
from time import sleep
from flask import Flask, request


GPIO.setwarnings(False)
# left weel
in1 = 5
in2 = 6
# right weel
in3 = 17
in4 = 27

# arm controller
# elbow(left) servo
elbow_pin = 1
# gripper servo
gripper_pin = 7
# base sevo
base_pin = 8
# shoulder(rigt) servo
shoulder_pin = 25



class arm_control():
    
    def __init__(self):
        self.arm_duty = [180, 30, 70, 125]
        self.elbow_pwm = GPIO.PWM(elbow_pin, 0.1)
        self.elbow_pwm.start(0)
        
        self.shoulder_pwm = GPIO.PWM(shoulder_pin, 0.1)
        self.shoulder_pwm.start(0)

        self.base_pwm = GPIO.PWM(base_pin, 0.1)
        self.base_pwm.start(0)
        
        self.gripper_pwm = GPIO.PWM(gripper_pin, 50)
        self.gripper_pwm.start(0)
        
        #self.set_angle(self.elbow_pwm, self.arm_duty[0])
        #self.set_angle(self.shoulder_pwm, self.arm_duty[1])
        #self.set_angle(self.base_pwm, self.arm_duty[2])
        self.set_angle(self.gripper_pwm, self.arm_duty[3])
        
    def set_angle(self,pwm, angle):
      
        duty = 2.5 + (angle / 180) * 10
        pwm.ChangeDutyCycle(duty);
    
    def update(self, mode):
     
        print(mode)
        # 10 ~ 200
        if mode == 'd':
            if self.arm_duty[0] - 1 >= 10:
                self.arm_duty[0] = self.arm_duty[0] - 1 
            self.set_angle(self.elbow_pwm, self.arm_duty[0])
    
        elif mode == 'u':
            if self.arm_duty[0] + 1 <= 200:
                self.arm_duty[0] = self.arm_duty[0] + 1 
            self.set_angle(self.elbow_pwm, self.arm_duty[0])
        # 20 ~ 160
        elif mode == 'l':
            if self.arm_duty[2] + 1 <= 150:
                self.arm_duty[2] = self.arm_duty[2] + 1 
            self.set_angle(self.base_pwm, self.arm_duty[2])
        elif mode == 'r':
            if self.arm_duty[2] - 1 >= 0:
                self.arm_duty[2] = self.arm_duty[2] - 1 
            self.set_angle(self.base_pwm, self.arm_duty[2])
        # 60 ~ 180
        elif mode == 'f':
            if self.arm_duty[1] + 1 <= 120:
                self.arm_duty[1] = self.arm_duty[1] + 1 
            self.set_angle(self.shoulder_pwm, self.arm_duty[1])
            
        elif mode == 'b':
            if self.arm_duty[1] - 1 >= 40:
                self.arm_duty[1] = self.arm_duty[1] - 1
            self.set_angle(self.shoulder_pwm, self.arm_duty[1])
        # 10 ~ 125
        elif mode == 'o':

            if self.arm_duty[3] - 1 >= 10:
                self.arm_duty[3] = self.arm_duty[3] - 1 
            self.set_angle(self.gripper_pwm, self.arm_duty[3])
         
        elif mode == 'c':
            
            if self.arm_duty[3] + 1 <= 125:
                self.arm_duty[3] = self.arm_duty[3] + 1
            self.set_angle(self.gripper_pwm, self.arm_duty[3])
        
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
        GPIO.setup(elbow_pin, GPIO.OUT)
        GPIO.setup(gripper_pin, GPIO.OUT)
        GPIO.setup(base_pin, GPIO.OUT)
        GPIO.setup(shoulder_pin, GPIO.OUT)
        
        self.arm_control = arm_control()
        
        self.car_control_data = -1
        self.arm_control_data = -1
    
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
            sleep(0.05)
    
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
            return f"<h1> Ok, receive car: {car_controll}, arm_controll: {arm_controll} </h1>"

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

