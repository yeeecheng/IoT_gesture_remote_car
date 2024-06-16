import threading
from time import sleep
from flask import Flask, request
import pigpio
import socket
import argparse

# left weel
in1_pin = 5
in2_pin = 6
# right weel
in3_pin= 17
in4_pin = 27

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
    
    def __init__(self, arm_sleep):
        
        # car wheel servo I/O
        self.in1_servo = pigpio.pi()
        self.in1_servo.set_mode(in1_pin, pigpio.OUTPUT)
        self.in1_servo.set_PWM_frequency(in1_pin, 50)
        
        self.in2_servo = pigpio.pi()
        self.in2_servo.set_mode(in2_pin, pigpio.OUTPUT)
        self.in2_servo.set_PWM_frequency(in2_pin, 50)
        
        self.in3_servo = pigpio.pi()
        self.in3_servo.set_mode(in3_pin, pigpio.OUTPUT)
        self.in3_servo.set_PWM_frequency(in3_pin, 50)
        
        self.in4_servo = pigpio.pi()
        self.in4_servo.set_mode(in4_pin, pigpio.OUTPUT)
        self.in4_servo.set_PWM_frequency(in4_pin, 50)
        
        # arm servo I/O
        self.arm_control = arm_control()
        # data control      
        self.car_control_data = -1
        self.arm_control_data = -1
        
        self.arm_sleep = arm_sleep
    
    def stop_GPIO(self):
        self.arm_control.elbow_servo.stop()
        self.arm_control.gripper_servo.stop()
        self.arm_control.base_servo.stop()
        self.arm_control.shoulder_servo.stop()
    
    def car_control(self, mode):
        
        if mode == 'b':
            
            self.in1_servo.write(in1_pin, 1)
            self.in2_servo.write(in2_pin, 0)
            self.in3_servo.write(in3_pin, 1)
            self.in4_servo.write(in4_pin, 0)

        elif mode == 'f':
            
            self.in1_servo.write(in1_pin, 0)
            self.in2_servo.write(in2_pin, 1)
            self.in3_servo.write(in3_pin, 0)
            self.in4_servo.write(in4_pin, 1)

        elif mode == 'l':
            
            self.in1_servo.write(in1_pin, 0)
            self.in2_servo.write(in2_pin, 0)
            self.in3_servo.write(in3_pin, 0)
            self.in4_servo.write(in4_pin, 1)

        elif mode == 'r':
            
            self.in1_servo.write(in1_pin, 0)
            self.in2_servo.write(in2_pin, 1)
            self.in3_servo.write(in3_pin, 0)
            self.in4_servo.write(in4_pin, 0)
            
        elif mode == 's':
            
            self.in1_servo.write(in1_pin, 0)
            self.in2_servo.write(in2_pin, 0)
            self.in3_servo.write(in3_pin, 0)
            self.in4_servo.write(in4_pin, 0)

    def arm_controller(self):
    
        while True:
            self.arm_control.update(self.arm_control_data)
            sleep(self.arm_sleep)
           
    
    def car_controller(self):
        while True:
            self.car_control(self.car_control_data)
    
    def update_controll_data(self, car_controll, arm_controll):
        self.car_control_data = car_controll
        self.arm_control_data = arm_controll
    
        

class API_Service():
    
    def __init__(self, args):
        
        
        self.app = Flask(__name__)
        self.host = args.ip
        self.port = args.port
        
        
        self.all_controller = all_control(args.arm_sleep)
        
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
        
        thread_arm_controller = threading.Thread(target = self.all_controller.arm_controller)
        thread_car_controller = threading.Thread(target = self.all_controller.car_controller)
        
        thread_car_controller.start()
        thread_arm_controller.start()

def get_ip():
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def parse_args():
    
    ip = get_ip()
    parse = argparse.ArgumentParser()
    parse.add_argument("--ip", default= ip, type= str, help= "ip address")
    parse.add_argument("--port", default= 5000, type= int, help= "port")
    parse.add_argument("-A", "--arm_sleep", default= 0.001, type= float, help= "arm sleep time")
    args = parse.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    # open API service
    api_service = API_Service(args)
    thread_api_service = threading.Thread(target = api_service.api_start)
    thread_api_service.start()
    
    # arm & car controller
    controller = threading.Thread(target = api_service.controller)
    controller.start()
