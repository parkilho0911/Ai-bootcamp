# Couldn't find a valid YOLO version tag.
# Replace XX with the correct version.
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
source = 'http://images.cocodataset.org/val2017/000000039769.jpg'
model.predict(source=source, save=True)