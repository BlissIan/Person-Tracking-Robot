import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame_inv = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame_inv, 1) #Flip frame

    h, w, channels = frame.shape #Change shape of frame

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    # Draw landmarks if hands are detected
    if results.multi_hand_landmarks: #if hand detected
        for hand_landmarks in results.multi_hand_landmarks: #loop thorugh results
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS) #Draw points on hand with lines connecting
            for id, lm in enumerate(hand_landmarks.landmark):
                #print(id, lm.x, lm.y, lm.z) #This prints the index and normalized coordinates of each point.
                cx, cy = int(lm.x * w), int(lm.y * h) #Get convert lm.x and lm.y to my coordinate system
                print(f"Landmark {id}: ({cx}, {cy})") #print x and y of each id in hand
                if id in [4, 8, 12, 16, 20]:  # fingertips
                    cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
                #Could use logic if finger tips are below (y value fingertip less than knuckle ) knuckles then do somthing 
    
    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
