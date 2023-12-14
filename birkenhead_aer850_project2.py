# -*- coding: utf-8 -*-
"""Birkenhead_AER850_Project2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YtKuAlm6opn3VNhoj_X-F0KqzhsE9Ady
"""

from google.colab import drive
drive.mount('/content/drive')

pip install ultralytics

import os
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:128'

"""Part 1"""

#This code has been copied into Google Colab. It was run in Spyder and contains the cv2.imshow() fucntion which cannot be used in Google Colab

import cv2
import numpy as np

# Read input image
img_path = '/Users/emilybirkenhead/Documents/4th Yr/AER850 - Intro t oMachine Learning/Project 3/Files/motherboard_image.JPEG'
img = cv2.imread(img_path)

# Verify that the image was loaded correctly
if img is None:
    print("Error: Image cannot be loaded. Please check the path.")
else:
    # Convert the original image to greyscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to the greyscale image to smooth out noise, allowing thresholding to occur
    blurred_img = cv2.GaussianBlur(img_gray, (7, 7), 0)

    # Apply  thresholding to the blurred image to obtain a binary image.
    binary_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours in the binary image. These contours represent the potential edges of objects.
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty mask with the same dimensions as the grayscale image.
    mask = np.zeros_like(img_gray)

    # Define a minimum area for the contours. Contours smaller than this area will be ignored.
    # This step helps in filtering out noise and small objects that are not of interest.
    min_contour_area = 1050

    # Go through each contour in the detected contours list
    for contour in contours:
        # Calculate the area of the contour
        area = cv2.contourArea(contour)
        # If the area is greater than the minimum area threshold, draw it on the mask
        if area > min_contour_area:
            cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

    # Display the binary image post thresholding
    cv2.imshow('Binary Threshold', binary_img)

    # Display the original image with the detected contours drawn over it
    contour_display_img = img.copy()
    cv2.drawContours(contour_display_img, contours, -1, (0, 255, 0), 2)
    cv2.imshow('Contours', contour_display_img)

    # Display the mask image
    cv2.imshow('Mask', mask)

    # Convert the mask to a three-channel image so it can be combined with the original color image
    mask_3channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Apply the mask to the original image using bitwise AND operation
    # This step isolates the detected objects and places them on a black background
    result = cv2.bitwise_and(img, mask_3channel)
    cv2.imshow('Final Extracted Image', result)

    # Display the original unaltered image
    cv2.imshow('Original', img)

    # Wait for any key to be pressed and then close all opened windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()

"""Part 2 - Train"""

import cv2
import numpy as np
from ultralytics import YOLO


#_____________________________________________________________________#
#Training


# Path to dataset configuration file
datas = '/content/drive/MyDrive/AER850 Project 3/data/data.yaml'

# Ppretrained YOLOv8 nano model
model = YOLO('yolov8n.pt')

# Train the model with specified hyperparameters
results = model.train(data=datas,
                      epochs=150,  # below 200
                      batch=4,
                      imgsz=928,  # 900 or higher
                      name='yolov8n_pcb_components')

"""Part 3 - Evaluation

"""

#_____________________________________________________________________#
# Evaluation

from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt #matplotlib was required as cv2.imshow() would not work in Google Colab


model = YOLO('/content/runs/detect/yolov8n_pcb_components3/weights/best.pt')

# Path to the images in the Evaluation folder
evaluation_images = [
    '/content/drive/MyDrive/AER850 Project 3/data/evaluation/ardmega.jpg',
    '/content/drive/MyDrive/AER850 Project 3/data/evaluation/arduno.jpg',
    '/content/drive/MyDrive/AER850 Project 3/data/evaluation/rasppi.jpg'
]

font_scale = 0.5

for image_path in evaluation_images:
    # Predict and get the results
    result = model.predict(image_path)

    # Load the image using OpenCV for visualization
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for matplotlib

    # Process and draw bounding boxes
    for r in result:
        boxes = r.boxes
        names = r.names

        for box_tensor in boxes:
            # Extract xyxy bounding box coordinates and other information
            x1, y1, x2, y2 = box_tensor.xyxy[0].cpu().numpy()
            conf = box_tensor.conf.cpu().numpy()[0]
            class_id = int(box_tensor.cls.cpu().numpy())

            # Draw bounding box
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

            # Put class label and confidence
            label = f"{names[class_id]}: {conf:.2f}"
            cv2.putText(image, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 255, 0), 2)

            # Print out the information
            print(f"Detected: {names[class_id]} - confidence: {conf:.2f}")

    # Display the image with bounding boxes using matplotlib
    plt.imshow(image)
    plt.axis('off')
    plt.show()