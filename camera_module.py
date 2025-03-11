import cv2

def camera_select(source:str):
    if source == "webcamera":
        return cv2.VideoCapture(0)
    
    elif source == "picamera":
        from picamera2 import Picamera2
        # Initialize Pi Camera
        picam2 = Picamera2()
        picam2.preview_configuration.main.size = (300, 300)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.configure("preview")
        picam2.start()

        return picam2

        
        



if __name__ == "__main__":
    cam1 = Camera()