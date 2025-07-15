import cv2, os
from ultralytics import solutions

def get_counter():
    region_points = [(100, 0), (100, 1078)]
    model = "./model/yolo11n.pt"
    counter = solutions.ObjectCounter(
        show=False,
        region=region_points,
        model=model,
        show_conf=True,
        show_labels=True,
        show_in=True,
        show_out=True,
        verbose=False,
        classes=[0]
    )
    return counter

