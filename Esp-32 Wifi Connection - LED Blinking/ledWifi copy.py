# Run this in boot.py

import time
import machine


from machine import Pin, PWM
import time

servo = PWM(Pin(23), freq=1000)


led = machine.Pin(2,machine.Pin.OUT)
led.off()

# ************************
# Configure the ESP32 wifi
import network

sta = network.WLAN(network.STA_IF)
if not sta.isconnected():
    print('connecting to network...')
    sta.active(True)
    #sta.connect('your wifi ssid', 'your wifi password')
    sta.connect('VM6093624', )
    while not sta.isconnected():
        pass
print('network config:', sta.ifconfig())

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',80))
s.listen(5)

# ************************
# Function for creating the web page to be displayed
def web_page():
    if isLedBlinking==True:
        led_state = 'Blinking'
        print('led is Blinking')
    else:
        if led.value()==1:
            led_state = 'ON'
            print('led is ON')
        elif led.value()==0:
            led_state = 'OFF'
            print('led is OFF')

    html_page = """
    <html>
    <head>
     <meta content="width=device-width, initial-scale=1" name="viewport"></meta>
    </head>
    <body>
     <center><h2>ESP32 Web Server in MicroPython </h2></center>
     <center>
      <form>
      <button name="LED" type="submit" value="1"> LED ON </button>
      <button name="LED" type="submit" value="0"> LED OFF </button>
      <button name="LED" type="submit" value="2"> LED BLINK </button>
      </form>
     </center>
     <center><p>LED is now <strong>""" + led_state + """</strong>.</p></center>
    </body>
    </html>"""
    return html_page


tim0 = machine.Timer(0)
def handle_callback(timer):
    led.value( not led.value() )
isLedBlinking = False

while True:

    # Socket accept()
    conn, addr = s.accept()
    print("Got connection from %s" % str(addr))

    # Socket receive()
    request=conn.recv(1024)
    print("")
    print("")
    print("Content %s" % str(request))

    # Socket send()
    request = str(request)
    led_on = request.find('/?LED=1')
    led_off = request.find('/?LED=0')
    led_blink = request.find('/?LED=2')
    if led_on == 6:
        print('LED ON')
        print(str(led_on))
        led.value(1)
        if isLedBlinking==True:
            tim0.deinit()
            isLedBlinking = False

    elif led_off == 6:
        print('LED OFF')
        print(str(led_off))
        led.value(0)
        if isLedBlinking==True:
            tim0.deinit()
            isLedBlinking = False

    elif led_blink == 6:
        print('LED Blinking')
        print(str(led_blink))
        isLedBlinking = True
        tim0.init(period=500, mode=machine.Timer.PERIODIC, callback=handle_callback)

    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)

    # Socket close()
    conn.close()
