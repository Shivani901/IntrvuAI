import cv2
import numpy as np
import tensorflow as tf # Using tensorflow.keras
import os

# Get the directory of the current script (interview_platform)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (newproject1)
BASE_PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

# Define the subdirectory where model and cascade files are located
FILES_SUBDIRECTORY = "newproject1"

# Construct absolute paths for model and cascade files
model_path = os.path.join(BASE_PROJECT_DIR, FILES_SUBDIRECTORY, "model (1).h5") 
haar_cascade_path = os.path.join(BASE_PROJECT_DIR, FILES_SUBDIRECTORY, "haarcascade_frontalface_default.xml")

model = None
face_cascade = None
error_message = None # To store a general error message for model/cascade loading

# Load Keras model
if os.path.exists(model_path):
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"Emotion detection model loaded successfully from {model_path}.")
    except Exception as e:
        error_message = f"Error loading Keras model from {model_path}: {e}"
        print(error_message)
else:
    error_message = f"Model file not found: {model_path}. Please ensure it is correctly placed."
    print(error_message)

# Load Haar cascade for face detection
if os.path.exists(haar_cascade_path):
    face_cascade = cv2.CascadeClassifier(haar_cascade_path)
    if face_cascade.empty():
        # Update error_message only if it's not already set by model loading failure
        current_cascade_error = f"Error loading Haar cascade from {haar_cascade_path}. File might be corrupted or invalid."
        if not error_message: error_message = current_cascade_error
        print(current_cascade_error)
        face_cascade = None # Ensure it's None if loading failed
    else:
        print(f"Haar cascade for face detection loaded successfully from {haar_cascade_path}.")
else:
    current_cascade_error = f"Haar cascade file not found: {haar_cascade_path}. Please ensure it is correctly placed."
    if not error_message: error_message = current_cascade_error
    print(current_cascade_error)


labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0

def detect_emotion_from_frame(frame_bgr):
    global model, face_cascade, error_message # Allow modification of global error_message for persistent errors

    if model is None:
        return error_message or "Emotion model not loaded."
    if face_cascade is None:
        return error_message or "Face cascade for detection not loaded."

    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    
    # Performance tip: Adjust minNeighbors and scaleFactor if detection is slow or inaccurate
    # For faster but potentially less accurate detection, increase scaleFactor (e.g., 1.2 or 1.3)
    # and decrease minNeighbors (e.g., 3 or 4).
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    detected_emotion = "No face detected" 

    if len(faces) > 0:
        # Get the largest face
        main_face = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)[0]
        (p, q, r, s) = main_face
        
        face_roi_gray = gray[q:q+s, p:p+r]
        face_roi_resized = cv2.resize(face_roi_gray, (48, 48))
        img_features = extract_features(face_roi_resized)
        
        try:
            pred = model.predict(img_features)
            prediction_label_index = pred.argmax()
            detected_emotion = labels.get(prediction_label_index, "Unknown emotion")
        except Exception as e:
            print(f"Error during model prediction: {e}")
            detected_emotion = "Prediction error"
            # Potentially re-initialize model or log more detailed error if this happens frequently
    
    return detected_emotion

# Example usage (for local testing of this script, not used by Django directly)
if __name__ == '__main__':
    # This part will only run if you execute "python emotion_detector.py" directly
    # It requires a webcam.
    if model is not None and face_cascade is not None:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open webcam")
            exit()
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            
            emotion = detect_emotion_from_frame(frame)
            cv2.putText(frame, f"Emotion: {emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Live Emotion Detection', frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    else:
        print("Cannot run local test: Model or face cascade not loaded.")
        if error_message:
            print(f"Reason: {error_message}") 