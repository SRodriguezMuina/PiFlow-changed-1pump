# Various PiFlow functions needed for pump control
# Flow rate arguments (Q) are in uL/min and duration (T) is in seconds
# Last updated 27/02/2026 by Timothy Kassis and Paola Perez

import time
import pandas as pd
import numpy as np
import RPi.GPIO as GPIO

# Calibration function to convert flow rate in uL/min to frequency
# Using calibration curve from pump 2 (original code)
def Q_to_f(Q):
    if Q <= 1:
        f = 0.001
    elif 1 < Q <= 2526.67:
        f = Q / 26.36
    elif 2526.67 < Q <= 3786.67:
        f = (Q - 1895) / 6.53
    else:
        print('Flow rate out of range')
        return
    return round(f, 3)

# Constant flow, supply Q in uL/min and duration T in sec
def Constant_Flow(Q, T):
    GPIO.setmode(GPIO.BCM)
    # Convert flow rate from uL/min to frequency (Hz)
    f = Q_to_f(Q)
    # Setup power pin
    GPIO.setup(19, GPIO.OUT)
    GPIO.output(19, GPIO.HIGH)
    # Setup PWM pin
    GPIO.setup(18, GPIO.OUT)
    # Assign PWM frequency
    Pump = GPIO.PWM(18, f)
    # Start pump and run for given time
    Pump.start(95)
    time.sleep(T)
    # Stop pump and clean up
    Pump.stop()
    GPIO.output(19, GPIO.LOW)
    GPIO.cleanup()
    print("Constant flow complete")

# Dynamic flow, supply csv file path
# CSV format: two columns only — time (s), flow rate (uL/min)
def Dynamic_Flow(file_path):
    GPIO.setmode(GPIO.BCM)
    # Setup power pin
    GPIO.setup(19, GPIO.OUT)
    GPIO.output(19, GPIO.HIGH)
    # Setup PWM pin
    GPIO.setup(18, GPIO.OUT)
    # Read file
    df = pd.read_csv(file_path)
    values = np.array(df)
    # Initialize and start pump
    Pump = GPIO.PWM(18, 1)
    Pump.start(95)
    for i in range(len(values) - 1):
        dt = round((values[i + 1][0]) - (values[i][0]), 4)
        Q = round(values[i][1], 1)
        f = Q_to_f(Q)
        if f > 0.01:
            Pump.start(95)
            Pump.ChangeFrequency(f)
        else:
            Pump.stop()
        time.sleep(dt)
    # Stop pump and clean up
    Pump.stop()
    GPIO.output(19, GPIO.LOW)
    GPIO.cleanup()
    print("Dynamic flow complete")
