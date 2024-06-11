import requests


def send_api(ip= "192.168.0.104", port = "5000", car_data= 0, arm_data= 0):
    
    url = "http://" + ip + ":" + port + "/?car=" + str(car_data) + "&arm=" + str(arm_data)
    web = requests.get(url)
    print(web.text)
