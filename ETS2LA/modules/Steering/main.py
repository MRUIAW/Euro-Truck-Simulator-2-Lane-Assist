import numpy as np
from ETS2LA.plugins.runner import PluginRunner
import ETS2LA.backend.settings as settings
import cv2
import time
import logging

runner:PluginRunner = None

SMOOTH_TIME = 0.1 # seconds
OFFSET = 0
SENSITIVITY = 1
MAX_ANGLE = 1

class SteeringValue:
    def __init__(self, value:float, timestamp:float):
        self.value = value
        self.timestamp = timestamp
        
    def IsOlderThan(self, timestamp:float):
        return self.timestamp < timestamp

steeringValues = []

def Initialize():
    pass

def CalculateSteeringAngle():
    global steeringValues
    
    # Calculate the average value
    average = np.mean([x.value for x in steeringValues])
    
    # Calculate the angle
    angle = average * SENSITIVITY + OFFSET
    angle = np.clip(angle, -MAX_ANGLE, MAX_ANGLE)
    
    return angle

def DrawSteeringLine(ShowImage, value, angle):
    output_img = np.zeros((ShowImage.LAST_HEIGHT, ShowImage.LAST_WIDTH, 3), np.uint8)
    
    w = output_img.shape[1]
    h = output_img.shape[0]
    
    currentDesired = value * (1/MAX_ANGLE)
    actualSteering = angle

    divider = 5
    # First draw a gray line to indicate the background
    cv2.line(output_img, (int(w/divider), int(h - h/10)), (int(w/divider*(divider-1)), int(h - h/10)), (100, 100, 100), 6, cv2.LINE_AA)
    # Then draw a light green line to indicate the actual steering
    cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + actualSteering * (w/2 - w/divider)), int(h - h/10)), (0, 255, 100), 6, cv2.LINE_AA)
    # Then draw a light red line to indicate the desired steering
    cv2.line(output_img, (int(w/2), int(h - h/10)), (int(w/2 + currentDesired * (w/2 - w/divider)), int(h - h/10)), (0, 100, 255), 2, cv2.LINE_AA)

    ShowImage.overlays["SteeringLine"] = output_img

def run(value:float = None, sendToGame:bool = True, drawLine:bool = True):
    # Add the newest value to the list
    if value is not None:
        steeringValues.append(SteeringValue(value, time.time()))
    else:
        steeringValues.append(SteeringValue(0, time.time())) # Slowly return to 0 naturally
        
    SDK = None
    if sendToGame:
        # Check if the SDK module is available
        try:
            SDK = runner.modules.SDKController
        except:
            logging.warning("SDK module not available, please add it to the plugin.json file or disable the sendToGame parameter.")
            return "SDK module not available, please add it to the plugin.json file or disable the sendToGame parameter."
    
    # Remove all values that are older than SMOOTH_TIME
    while steeringValues[0].IsOlderThan(time.time() - SMOOTH_TIME):
        steeringValues.pop(0)
        
    # Calculate the steering angle
    angle = CalculateSteeringAngle()
    
    # Send the angle to the game
    if sendToGame and SDK is not None:
        SDK.steering = angle
        
    # Draw the steering line
    if drawLine:
        try: 
            SI = runner.modules.ShowImage
        except:
            logging.warning("DefaultSteering: ShowImage module not available, please add it to the plugin.json file or disable the drawLine parameter.")
            return "ShowImage module not available, please add it to the plugin.json file or disable the drawLine parameter."
        DrawSteeringLine(SI, value, angle)
    
    return angle
    