Gesture Remote Car


## remote_car_controller.py
> python3 remote_car_controller.py --ip <ip address> --port <port> -A <arm sleep time>

```=python
parse.add_argument("--ip", default= ip, type= str, help= "ip address")
parse.add_argument("--port", default= 5000, type= int, help= "port")
parse.add_argument("-A", "--arm_sleep", default= 0.001, type= float, help= "arm sleep time")
```

