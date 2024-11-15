from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import RPi.GPIO as GPIO
from switch import Switch
from led import LED
from pump import Pump
from timer import Timer
from sensor import *
import threading
import os
from PiControler import*
import eventlet



# Set GPIO pins for switch, LED, and pump relay
SWITCH_PIN = 17  # GPIO pin for the start switch
LED_PIN = 27     # GPIO pin for the LED
RELAY_PIN = 22   # GPIO pin for the pump relay
eventlet.monkey_patch()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')  # Use environment variable or default key
socketio = SocketIO(app, cors_allowed_origins="*")




GPIO.setmode(GPIO.BCM)  # Set GPIO mode

def monitor_switch():
    while True:
        if switch.is_pressed():
            socketio.emit('switch_status', {'status': 'active'})
        else:
            socketio.emit('switch_status', {'status': 'install_cartridge'})

        socketio.sleep(1)  # Poll the switch status every second


def handle_sensor_data(data):
    """
    Handle sensor data by emitting it.
    """
    formatted_data = f"{data:.2f}"
    print(f"Emitted sensor data: {formatted_data}")
    socketio.emit('pressure_sensor_reading_1', {'message': formatted_data})
    socketio.sleep(1)  # Sleep for 1 second bef



# Serve the HTML page
@app.route('/')
def index():
    return render_template('index_c.html')


switch = Switch(SWITCH_PIN)
led = LED(LED_PIN)

@socketio.on('switch_status_replay')
def switch_status():
    print("switch_status")







@socketio.on('start_pump')
def handle_pump(data):

    print('proces_time', data.get('proces_time'))
    time_process = data.get('proces_time')
    print("Pump started:", data)  # Log incoming data for debugging
    button_id = data.get("blockId")
    print("Button press event received:", button_id)

    pump = Pump(RELAY_PIN)
    pressure_sensor = PresureSensor()
    timer = Timer(time_process, pressure_sensor, handle_sensor_data)




    pump_controller = PiPumpController(switch, led, pump, timer)
    pump_controller.check_and_run()

thread = threading.Thread(target=monitor_switch, daemon=True)
thread.start()


# Run the server using socketio.run for WebSocket support
if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    socketio.run(app, host='127.0.0.1', port=5005, debug=True, allow_unsafe_werkzeug=True)




