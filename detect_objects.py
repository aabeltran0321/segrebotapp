import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import Picamera2

# Load TFLite model
interpreter = tflite.Interpreter(model_path="lite-model_ssd_mobilenet_v1_1_metadata_2.tflite")
interpreter.allocate_tensors()

# Get model input details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load label map
with open("coco_labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Initialize Pi Camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (300, 300)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

print("Running Object Detection...")

while True:
    frame = picam2.capture_array()
    img_resized = cv2.resize(frame, (300, 300))  # Resize for model input
    input_data = np.expand_dims(img_resized, axis=0).astype(np.uint8)

    # Run model inference
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    # Get detection results
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]  # Bounding box coordinates
    classes = interpreter.get_tensor(output_details[1]['index'])[0]  # Class index
    scores = interpreter.get_tensor(output_details[2]['index'])[0]  # Confidence scores

    for i in range(len(scores)):
        if scores[i] > 0.5:  # Only show detections with >50% confidence
            label = labels[int(classes[i])]
            print(f"Detected: {label} ({scores[i]*100:.2f}%)")

    # Display image (optional)
    cv2.imshow("Object Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):  # Press 'q' to exit
        break

cv2.destroyAllWindows()
