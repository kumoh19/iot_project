import threading
import socket
import time
import RPi.GPIO as GPIO
from grovepi import *
import os


def infrared_remote_control():
    SOCKET_PATH = '/var/run/lirc/lircd'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
    print('Connect:', SOCKET_PATH)
    sock.connect(SOCKET_PATH)

    # Function to read key from IR remote
    def read_key_try():
        try:
            data = sock.recv(128)
        except BlockingIOError:
            return None
        return data

    def read_key():
        data = read_key_try()
        if data:
            word = data.split()
            return word[2]
        return ''

    # Setup for LED
    led = 22
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led, GPIO.OUT)
    time.sleep(1)
    GPIO.output(led, GPIO.LOW)

    # Main loop
    while True:
        keyname = read_key()
        if keyname == '':
            time.sleep(0.1)  # Small delay to prevent CPU overuse
            continue

        # Check if KEY_1 is pressed
        if keyname == b'KEY_1':
            GPIO.output(led, GPIO.HIGH)
            print("LED ON!")

        # Check if KEY_2 is pressed
        elif keyname == b'KEY_2':
            GPIO.output(led, GPIO.LOW)
            print("LED OFF!")

        time.sleep(0.1)  # Debounce delay

        try:
            # Additional code for handling other keys or events can be added here
            pass
        except KeyboardInterrupt:
            GPIO.output(led, GPIO.LOW)
            break
        except IOError:
            print("Error")

def beacon_wand():
    ultrasonic_ranger = 3
    buzzer_pin = 2
    pinMode(buzzer_pin,"OUTPUT")

    while True:
        try:
            distant = ultrasonicRead(ultrasonic_ranger)
            print (distant,'cm')
            if distant <= 10: # 거리가 10cm 이하이면
                digitalWrite(buzzer_pin,1) #작동
                time.sleep(0.5)
            else:
                digitalWrite(buzzer_pin,0)
                time.sleep(0.5)
        
        except TypeError:
            digitalWrite(buzzer_pin,0)
            print ("Error")
            break
        except IOError:
            print ("Error")
            break

def traffic_light():
    def text_speak(text):
        os.system('espeak -v ko ' + text)

    GPIO.setmode(GPIO.BCM)
    GREEN_LED = 27
    RED_LED = 4
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setwarnings(False)

    try:
        while True:
            GPIO.output(GREEN_LED, GPIO.HIGH)
            GPIO.output(RED_LED, GPIO.LOW)
            text_speak("green_light__cross_the_street")
            time.sleep(3)

            GPIO.output(GREEN_LED, GPIO.LOW)
            GPIO.output(RED_LED, GPIO.HIGH)
            text_speak("red_light__Do_not_cross_the_street")
            time.sleep(3)

    except KeyboardInterrupt:
        GPIO.output(GREEN_LED, GPIO.LOW)
        GPIO.output(RED_LED, GPIO.LOW)
        GPIO.cleanup()

def detect_and_alert():
    # 초음파 센서와 부저 핀 설정
    ultrasonic_ranger_sidewalk = 4
    ultrasonic_ranger_driveway = 8
    buzzer_pin = 2
    pinMode(buzzer_pin,"OUTPUT")

    sidewalk_detected = False

    while True:
        try:
            # 보도와 차도 센서로부터 거리 읽기
            distance_sidewalk = ultrasonicRead(ultrasonic_ranger_sidewalk)
            distance_driveway = ultrasonicRead(ultrasonic_ranger_driveway)

            print("Sidewalk:", distance_sidewalk, "cm, Driveway:", distance_driveway, "cm")

            # 보도 센서에 무언가 감지되었는지 확인
            if distance_sidewalk <= 10:
                sidewalk_detected = True

            # 차도 센서에 무언가 감지되고, 이전에 보도 센서에 감지된 경우
            if sidewalk_detected and distance_driveway <= 10:
    			print("buzzer on")
                digitalWrite(buzzer_pin, 1)  # 부저 작동
                time.sleep(1)
                sidewalk_detected = False  # 상태 초기화
            else:
                digitalWrite(buzzer_pin, 0)

            time.sleep(2)

        except TypeError as e:
            digitalWrite(buzzer_pin, 0)
            print("Error:", e)
            break
        except IOError as e:
            print("Error:", e)
            break

thread1 = threading.Thread(target=infrared_remote_control)
thread2 = threading.Thread(target=beacon_wand)
thread3 = threading.Thread(target=traffic_light)
thread4 = threading.Thread(detect_and_alert)

thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()