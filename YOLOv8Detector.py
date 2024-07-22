from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image

class YOLOv8Detector:
    def __init__(self, model_path='yolov8s.pt'):
        self.model = YOLO(model_path)

    def predict_image_path(self, image_path, verbose=False):
        """Predict objects in an image given its path."""
        results = self.model.predict(image_path, verbose=verbose)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                print(f"Bounding Box: [{x1}, {y1}, {x2}, {y2}]")
                conf = box.conf[0]
                print(f"Confidence: {conf}")
                cls_id = box.cls[0]
                cls_name = self.model.names[int(cls_id)]
                print(f"Class Name: {cls_name}")
        results[0].save()  # Save the annotated image to the 'runs/detect/predict/' directory

    def predict_opencv_image(self, opencv_image, verbose=False):
        """Predict objects in an image loaded by OpenCV."""
        # Convert the OpenCV image (numpy array) to PIL image for YOLOv8
        pil_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(pil_image)

        # Make predictions
        results = self.model.predict(opencv_image, verbose=verbose)
        detected_objects = []

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                # print(f"Bounding Box: [{x1}, {y1}, {x2}, {y2}]")
                conf = box.conf[0]
                # print(f"Confidence: {conf}")
                cls_id = box.cls[0]
                cls_name = self.model.names[int(cls_id)]
                # print(f"Class Name: {cls_name}")
                detected_objects.append(cls_name)
                print(f"===>Detected:{detected_objects}<===")

        return detected_objects

        # Optionally, you can also visualize the results on the OpenCV image
        # results[0].plot() would give you the annotated image, but since we're working directly with OpenCV images,
        # we need to manually draw the boxes and labels if needed.