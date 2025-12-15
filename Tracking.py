import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from collections import defaultdict
from ultralytics.utils.plotting import Annotator
import math
from multiprocessing import Process, Queue
import mediapipe as mp


def Track(queue, frame_queue):


    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1
    )

    mp_drawing = mp.solutions.drawing_utils
    track_history = defaultdict(lambda: [])
    
    model_pre = YOLO("yolov8n.pt")# model option 1
    model_pre.export(format = 'onnx', imgsz =320, opset=12)

    model = YOLO("yolov8n.onnx")

    names = model.names
    
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while cap.isOpened():
        success, frame_flipped = cap.read()
        if success:
            
            frame = cv2.flip(frame_flipped, 1) #flip horizontal
            #frame = cv2.flip(frame_flipped,0) #Flip virtical

            #Get size of frame
            frame_height, frame_width, channels = frame.shape

            #Create point at Center of frame
            Center_Frame = (frame_width // 2 , frame_height // 2)

            #Get Center frame cordinates
            Center_Frame_X = int(Center_Frame[0])
            Center_Frame_Y = int(Center_Frame[1])

            results = model.track(frame, persist=True, tracker="bytetrack.yaml", classes = 0, verbose=False)
                
            # Extract bounding box coordinates (x, z, w, h) from resluts
            boxes = results[0].boxes.xywh
            # Extract class ids (e.g., 0 for 'person', 1 for 'bicycle', etc.) for each detected object
            clss = results[0].boxes.cls.tolist()
            #Extract track ids for each detected object (unique IDs assigned to each detected object)
            ids = results[0].boxes.id

            if ids is None:
                track_ids = []
                queue.put('No_Target')
            else:
                #track_ids = ids.int().cpu().tolist()
                track_ids = ids.int().tolist()
                #.tolist changes it to a python list

            # Initialize annotator for drawing boxes and lables on the framw
            annotator = Annotator(frame, line_width = 2, example = str(names))

            #Draw circle in middle of frame
            cv2.circle(frame, Center_Frame, 1 , (235, 219, 11), 5, -1)

            #Loop through all detected and tracked objects
            for box, track_id, cls in zip(boxes, track_ids, clss):
                
                #Center coordinates and box size
                x, y, w, h = box

                #Convert from center coordinates (x,y,w,h) to top-left/ bottom - right
                x1, y1, x2, y2 = (x - w / 2, y-h / 2, x + w / 2, y+ h / 2)

                if cls == 0:  #only show person class
                    #Create lable text with class name and track ID
                    label = str(names[cls]) + " : " + str(track_id)

                    #Draw bounding box and label on the frame
                    annotator.box_label([x1, y1, x2, y2], label, (218, 100, 255))
                    if track_id == min(track_ids):
                            #Retrieve this track's previous bounding box center positions (for drawing motion trails)
                            track = track_history[track_id]
                            
                            # Add current position to history
                            track.append((float(box[0]), float(box[1])))
                        
                            #average 3 points to get more stable results
                            if len(track) > 3:
                                track.pop(0)
                            
                                points_average_x = (track[0][0]+track[1][0]+track[2][0])/ len(track)
                                points_average_y = (track[0][1]+track[1][1]+track[2][1]) / len(track)
                            else:
                                points_average_x = track[-1][0]
                                points_average_y = track[-1][1]

                            points_average_x = round(points_average_x,3)
                            points_average_y = round(points_average_y,3)
                            
                            cv2.circle(frame, (int(points_average_x), int(points_average_y)), 5, (235, 219, 11), -1) #averaged point for smooter tracking but more delay
                            #non averaged values
            
                            #averaged values
                            x_vector = (int(points_average_x) - Center_Frame_X)
                            y_vector = (int(points_average_y)- Center_Frame_Y)

                            vectors = f"[X:{x_vector:.1f}, Y:{y_vector:.1f}]"
                            
                            #Get angle between objects
                            angle_rad = math.atan2(y_vector, x_vector)
                            angle_deg = np.rad2deg(angle_rad) + 180
                            angle_str = f"{angle_deg:.2f}"

                            #print(f"X: = {x_vector}, Y: = {y_vector}, indenifier = {track_id}")

                            #Draw arrow to center point / where drone needs to go
                            cv2.arrowedLine(frame, Center_Frame, (int(points_average_x), int(points_average_y)), (235, 219, 11), 2, 8 , 0, 0.1 )
                            
                            #Calculate arrow center averaged
                            arrow_center_X = (int(points_average_x) + Center_Frame_X ) // 2
                            arrow_center_Y = (int(points_average_y) + Center_Frame_Y ) // 2

                            #FInd the center of the line
                            (text_width, text_height), baseline = cv2.getTextSize(vectors, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                                                                                    0.7,2)
                            text_x = arrow_center_X - text_width // 2
                            text_y = arrow_center_Y - 10

                            #Print distance on line
                            cv2.putText(frame, angle_str, (text_x, text_y),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (235, 219, 11), 2, cv2.LINE_AA )
                            # Convert BGR to RGB
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                            # Process frame with MediaPipe Hands
                            results = hands.process(rgb_frame)

                            # Draw landmarks if hands are detected
                            if results.multi_hand_landmarks: #if hand detected
                                height, width, channels = frame.shape #Change shape of frame
                                for hand_landmarks in results.multi_hand_landmarks: #loop thorugh results
                                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                                              mp_drawing.DrawingSpec(color=(121,22,76), thickness = 2, circle_radius=4),
                                                              mp_drawing.DrawingSpec(color=(250,44,250), thickness = 2, circle_radius=2),) #Draw points on hand with lines connecting
                                    
                                    #Get coordinate of wrist 
                                    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                                    wrist_x, wrist_y = int(wrist.x * width), int(wrist.y * height)

                                    # Get coordinates of thumb tip
                                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                                    thumb_x_tip, thumb_y_tip = int(thumb_tip.x * width), int(thumb_tip.y * height)

                                    #Get coordinate of thumb_mid
                                    thumb_mid = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
                                    thumb_x_mid, thumb_y_mid = int(thumb_mid.x * width), int(thumb_mid.y * height)

                                    #Get coordinate of index_tip
                                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                                    
                                    
                                    index_x, index_y = int(index_tip.x * width), int(index_tip.y * height)

                                    # logic for detecting tumbs up
                                    if (thumb_y_tip < thumb_y_mid) and (thumb_y_tip < index_y):
                                        cv2.circle(frame, (thumb_x_tip, thumb_y_tip), 8, (0, 255, 0), -1)
                                        cv2.circle(frame, (thumb_x_mid, thumb_y_mid), 8, (0, 255, 0), -1)
                                        queue.put([x_vector, y_vector, round(angle_deg, 2), 1]) 
                                    elif (thumb_y_tip > thumb_y_mid) and (thumb_y_tip > index_y):
                                        cv2.circle(frame, (thumb_x_tip, thumb_y_tip), 8, (0, 0, 255), -1)
                                        cv2.circle(frame, (thumb_x_mid, thumb_y_mid), 8, (0, 0, 255), -1)
                                        queue.put([x_vector, y_vector, round(angle_deg, 2), 2])
                                    
                                    else:
                                        cv2.circle(frame, (thumb_x_tip, thumb_y_tip), 8, (255, 0, 0), -1)
                                        cv2.circle(frame, (thumb_x_mid, thumb_y_mid), 8, (255, 0, 0), -1)
                                        queue.put([x_vector, y_vector, round(angle_deg, 2), 0])

                                    cv2.circle(frame, (index_x, index_y), 8, (255, 255, 100), -1)

                                    #print(f"Thumb_tip: ({thumb_x_tip}, {thumb_y_tip}), Thumb_base: ({thumb_x_mid}, {thumb_y_mid})")
                                   
                            else: 
                                queue.put([x_vector, y_vector, round(angle_deg, 2), 0])             
                else:
                    #Skip other object types
                    queue.put('No_Target')
                    pass
        else:
        #Skip other object types
            queue.put('No_Target')
        #Display the annoted video fram in window
        #cv2.imshow("Yolov8 Detection", frame)

        #Send to webserver
        # Encode frame
        ret, jpeg = cv2.imencode(
            ".jpg", frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 30]
        )

        if ret and frame_queue is not None:
            if frame_queue.full():
                frame_queue.get()  # drop old frame
            frame_queue.put(jpeg.tobytes())

        if cv2.waitKey(1) & 0xFF == ord("l"):
            break
    cap.release()
    cv2.destroyAllWindows()
