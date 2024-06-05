from ETS2LA.plugins.runner import PluginRunner  
import ETS2LA.backend.variables as variables
import ETS2LA.backend.settings as settings
import ETS2LA.backend.controls as controls
import time
import cv2

runner:PluginRunner = None
YOLO_FPS = 2 # How many times per second the YOLO model should run

class Vehicle:
    raycasts: list
    screenPoints: list
    vehicleType: str
    def __init__(self, raycasts, screenPoints, vehicleType):
        self.raycasts = raycasts
        self.screenPoints = screenPoints
        self.vehicleType = vehicleType

def SendCrashReport(): # REMOVE THIS LATER
    return

def Initialize():
    global ShowImage
    global TruckSimAPI
    global ScreenCapture
    global Raycast
    global capture_y, capture_x, capture_width, capture_height, model, MODEL_PATH, frame, temp

    import pyautogui
    import bettercam
    import torch
    import numpy as np
    import os
    import pathlib
    import pyautogui

    ShowImage = runner.modules.ShowImage
    TruckSimAPI = runner.modules.TruckSimAPI
    ScreenCapture = runner.modules.ScreenCapture
    Raycast = runner.modules.Raycasting

    MODEL_NAME = "5-25-24_1.pt"
    MODEL_PATH = os.path.dirname(__file__) + f"/models/{MODEL_NAME}"

    temp = pathlib.PosixPath
    pathlib.PosixPath = pathlib.WindowsPath

    model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH, _verbose=False)
    model.conf = 0.75

    capture_x = 2000
    capture_y = 0
    lowerHeight = 300 # Helps with coding
    lowerWidth = 3500 # Helps with coding
    capture_width = pyautogui.size()[0] - lowerWidth
    capture_height = pyautogui.size()[1] - lowerHeight

    cv2.namedWindow('Vehicle Detection', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Vehicle Detection', int(capture_width/3), int(capture_height/3))
    cv2.setWindowProperty('Vehicle Detection', cv2.WND_PROP_TOPMOST, 1)

def get_text_size(text="NONE", text_width=100, max_text_height=100):
    fontscale = 1
    textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
    width_current_text, height_current_text = textsize
    max_count_current_text = 3
    while width_current_text != text_width or height_current_text > max_text_height:
        fontscale *= min(text_width / textsize[0], max_text_height / textsize[1])
        textsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontscale, 1)
        max_count_current_text -= 1
        if max_count_current_text <= 0:
            break
    thickness = round(fontscale * 2)
    if thickness <= 0:
        thickness = 1
    return text, fontscale, thickness, textsize[0], textsize[1]

def place_results_text(text="NONE", x1=100, y1=100, x2=200, y2=200, width_scale=1, height_scale=1, color=(255, 255, 255)):
    text, fontscale, thickness, width, height = get_text_size(text, round((x2-x1)*width_scale), round((y2-y1)*height_scale))
    line_thickness = round((x2 - x1) / 50)
    cv2.rectangle(frame, (x1, round(y1 - height * 2)), (x2, y2), color, line_thickness)
    cv2.rectangle(frame, (x1, round(y1 - height * 2)), (x2, y1 + line_thickness), color, -1)
    cv2.putText(frame, text, (x1 + round((x2 - x1) / 2 - width / 2), y1  - round(height * 0.5)), cv2.FONT_HERSHEY_SIMPLEX, fontscale, (255, 255, 255), thickness, cv2.LINE_AA)

boxes = None
cur_yolo_fps = 0
frame = None
yolo_frame = None
def detection_thread():
    global boxes, cur_yolo_fps
    while True:
        if type(yolo_frame) is None:
            time.sleep(1/YOLO_FPS)
            continue
        startTime = time.time()
        # Run YOLO model
        try: results = model(yolo_frame)
        except: time.sleep(1/YOLO_FPS); continue # Model is not ready
        boxes = results.pandas().xyxy[0]
        #print(boxes)
        timeToSleep = 1/YOLO_FPS - (time.time() - startTime)
        if timeToSleep > 0:
            time.sleep(timeToSleep)
        cur_yolo_fps = round(1 / (time.time() - startTime), 1)
    
import threading
threading.Thread(target=detection_thread, daemon=True).start()

trackers = []
def create_trackers(boxes, frame):
    global trackers
    try:
        trackers = []
        for _, box in boxes.iterrows():
            x, y, w, h = int(box['xmin']), int(box['ymin']), int(box['xmax'] - box['xmin']), int(box['ymax'] - box['ymin'])
            tracker = cv2.legacy.TrackerMOSSE_create()
            tracker.init(frame, (x, y, w, h))
            trackers.append(tracker)
    except Exception as e:
        pass

# Use openCV to track the boxes
last_boxes = None
def track_cars(last_track, boxes, frame):
    global last_boxes, trackers
    
    if type(boxes) is type(None):
        return None
    
    if type(last_boxes) is type(None):
        last_boxes = boxes
        create_trackers(boxes, frame)
        
    if not last_boxes.equals(boxes):
        last_boxes = boxes
        create_trackers(boxes, frame)
        
    if type(trackers) is None:
        return None
    
    # Update the trackers and return the yolo data with updated boxes
    updated_boxes = boxes.copy()
    count = 0
    for tracker, box in zip(trackers, boxes.iterrows()):
        try:
            success, pos = tracker.update(frame)
            if not success:
                print(f"Tracking failed for {box[0]['name']} with confidence {box[0]['confidence']}")
                continue
            x, y, w, h = int(pos[0]), int(pos[1]), int(pos[2]), int(pos[3])
            updated_boxes.loc[box[0], 'xmin'] = x
            updated_boxes.loc[box[0], 'ymin'] = y
            updated_boxes.loc[box[0], 'xmax'] = x + w
            updated_boxes.loc[box[0], 'ymax'] = y + h
            count += 1
        except:
            pass

    return updated_boxes
    
    
    

fps = 0
start_time = time.time()
def plugin():
    global frame, yolo_frame, fps, start_time, model, capture_x, capture_y, capture_width, capture_height
    
    # capture_y:capture_y + capture_height, capture_x:capture_x + capture_width
    ScreenCapture.monitor_x1 = capture_x
    ScreenCapture.monitor_y1 = capture_y
    ScreenCapture.monitor_x2 = capture_x + capture_width
    ScreenCapture.monitor_y2 = capture_y + capture_height
    
    data = {}
    data["api"] = TruckSimAPI.run()
    inputTime = time.time()
    data["frame"] = ScreenCapture.run(imgtype="cropped")
    inputTime = time.time() - inputTime

    frame = data["frame"]
    if frame is None: 
        return None
    
    #yolo_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    yolo_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    trackTime = time.time()
    tracked_boxes = track_cars(last_boxes, boxes, yolo_frame)
    trackTime = time.time() - trackTime

    carPoints = []
    vehicles = []
    visualTime = time.time()
    if type(tracked_boxes) != None:
        try:
            for _, box in tracked_boxes.iterrows():
                label = box['name']
                score = box['confidence']
                x, y, w, h = int(box['xmin']), int(box['ymin']), int(box['xmax'] - box['xmin']), int(box['ymax'] - box['ymin'])
                # Add the offset to the x and y coordinates
                xr = x + capture_x
                yr = y + capture_y
                
                if label in ['car']:
                    bottomLeftPoint = (xr, yr + h)
                    bottomRightPoint = (xr + w, yr + h)
                    
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "car"))
                    cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
                    #place_results_text(f"{label} {round(score, 2)} {round(w, 1)}", x1=x, y1=y, x2=x+w, y2=y+h, width_scale=0.9, height_scale=0.75, color=(0, 0, 255))
                if label in ['truck']:
                    bottomLeftPoint = (xr, yr + h)
                    bottomRightPoint = (xr + w, yr + h)
                    
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "truck"))
                    cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
                    #place_results_text(f"{label} {round(score, 2)} {round(w, 1)}", x1=x, y1=y, x2=x+w, y2=y+h, width_scale=0.9, height_scale=0.75, color=(255, 0, 0))
                if label in ['bus']:
                    bottomLeftPoint = (xr, yr + h)
                    bottomRightPoint = (xr + w, yr + h)
                    
                    carPoints.append((bottomLeftPoint, bottomRightPoint, "bus"))
                    cv2.line(frame, (x, y + h), (x + w, y + h), (0, 0, 255), 2)
                    #place_results_text(f"{label} {round(score, 2)} {round(w, 1)}", x1=x, y1=y, x2=x+w, y2=y+h, width_scale=0.9, height_scale=0.75, color=(0, 255, 0))
            for line in carPoints:
                raycasts = []
                screenPoints = []
                for point in line:
                    if type(point) == str: # Skip the vehicle type
                        continue
                    raycastStart = time.time()
                    raycast = Raycast.run(x=point[0], y=point[1])
                    raycasts.append(raycast)
                    screenPoints.append(point)
                vehicles.append(Vehicle(raycasts, screenPoints, line[2]))
        except:
            pass
    visualTime = time.time() - visualTime

    fps = round(1 / (time.time() - start_time))
    start_time = time.time()

    cv2.putText(frame, f"FPS: {fps}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)   
    cv2.putText(frame, f"YOLO FPS: {cur_yolo_fps}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)      
    cv2.putText(frame, f"Tracking Time: {round(trackTime*1000, 2)}ms ({len(trackers)} objects)", (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Visual Time: {round(visualTime*1000, 2)}ms", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, f"Input Time: {round(inputTime*1000, 2)}ms", (20, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Vehicle Detection', frame)
    cv2.waitKey(1)
    
    # {
    #   "vehicles": [
    #       Vehicle: [
    #           raycasts: Raycasting.RaycastResponse[]
    #           vehicleType: str
    #       ]
    #   ]  
    # }
    
    return None, {
        "vehicles": vehicles,
    }