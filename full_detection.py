import cv2  # OpenCV library
import numpy as np
import tensorflow as tf
import time
from picamera2 import Picamera2
import sys
sys.path.append('/usr/lib/python3/dist-packages/libcamera') #add libcamera directory to the list of paths where Python looks for modules

#SSD MobileNet model path
model_path = '/home/user/your/path/detect.tflite'

#load the TFLite model
interpreter = tf.lite.Interpreter(model_path=model_path)  #create the TFLite interpreter and load the model
interpreter.allocate_tensors()  #allocate memory for the tensors needed, both input and output

#log file path
log_file = '/home/user/your/path/detection_log.txt'

#label file path
labels_path = '/home/user/your/path/labelmap.txt'

#load the labels into a list
with open(labels_path, 'r') as f: #read ('r') the file
    labels = [line.strip() for line in
              f.readlines()] #insert the labels from the file into the variable as a list of strings
    #line.strip() removes unwanted character (such as "\n", spaces and tabs) from each label

#function for detection
def detect_objects(frame): #get the input/output details from the TFLite model
    input_details = interpreter.get_input_details() #such as tensor dimensions and type (ex. uint8)
    output_details = interpreter.get_output_details() #such as detected object and confidence scores

    #convert image to BGR if it has 4 channels
    if frame.shape[-1] == 4: #access last element of the shape tuple (height, width, number of channels)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR) #from BGRA (blue, green, red, alpha) to BGR (blue, green, red)

    #prepare the image for the model
    input_tensor = cv2.resize(frame, (300, 300)) #resize the captured image to 300x300 pixels (as requested from the model, which is pre-trained with 300x300 images)
    input_tensor = np.expand_dims(input_tensor, axis=0) #add a dimension (representing the batch size, requested from the model) in the 0th position
    #np.expand_dims automatically adds a '1' in the new dimension
    input_tensor = input_tensor.astype(np.uint8)  #astype(np.uint8) converts the image to uint8, data type required from the model

    #set the input tensor
    interpreter.set_tensor(input_details[0]['index'], input_tensor)  #load the input tensor into the model
    #input_details[0]['index'] represents the position where we need to allocate input_tensor using SSD MobileNet
    #input_tensor is the processed image data that will be analyzed by the model

    #perform the inference
    interpreter.invoke()

    #get results (output)
    boxes = interpreter.get_tensor(output_details[0]['index'])  #get bounding boxes coordinates
    classes = interpreter.get_tensor(
        output_details[1]['index'])  #get detected object classes (classes are represented by numbers not words)
    scores = interpreter.get_tensor(output_details[2]['index'])  #get the confidence scores

    return boxes, classes, scores  #return the function results


#function for frame processing
def process_frame(frame):
    detection_results = detect_objects(frame)  #analyze the frame and store the results

    boxes = detection_results[0]  #bounding boxes coordinates in the format [ymin, xmin, ymax, xmax]
    classes = detection_results[1]  #detected object classes
    scores = detection_results[2]  #confidence scores
    height, width = frame.shape[:2]  #height and width of the frame
    #OpenCV uses the format (width, height, channels), so we exclude the last element

    #write the results in a log file
    with open(log_file, 'a') as f:  #if log_file already exists data will be added; if not a file will be created;
        #'a' stands for 'append', so new data will be added at the end of the file with no overwriting
        for i in range(len(scores[0])):  #iterates for each object detection score
            #len(scores[0]) represents the amount of objects detected
            score = scores[0][i]  #confidence score of the i-th object in scores[0]
            class_id = int(classes[0][i])  #class of the i-th object in classes[0]
            #casting the class_id from float (used by the model) to an integer, since python doesn't support float indexing
            if score > 0.5:  #filter for minimum confidence. Detections with score less than 0.5 will not be trusted
                if class_id < len(
                        labels):  #if class_id is less than len(labels) it means it corresponds to a valid label
                    label = labels[class_id]  #assign the correct label
                else:
                    label = f"Unknown ({class_id})"  #if class_id is not less than len(labels) we assign an "Unknown" label since it's not a valid class index
                #get bounding box coordinates
                ymin = boxes[0][i][0]  #1st element of the array
                xmin = boxes[0][i][1]  #2nd element of the array
                ymax = boxes[0][i][2]  #3rd element of the array
                xmax = boxes[0][i][3]  #4th element of the array
                #boxes[0] represents the first and only detection batch
                #boxes[0][i] represents the i-th bounding box in the detection batch

                #convert normalized coordinates (0-1) to pixel distances
                #casting from float to integer
                ymin = int(ymin * height)  #distance from the top of the frame
                xmin = int(xmin * width)  #distance from the left of the frame
                ymax = int(ymax * height)  #distance from the bottom of the frame
                xmax = int(xmax * width)  #distance from the right of the frame
                # height and width represent the frame dimensions in pixels

                #determine object's position in the frame
                #calculate center point of the object
                center_x = (xmin + xmax) // 2  #mean between xmin and xmax
                center_y = (ymin + ymax) // 2  #mean between ymin and ymax

                #divide the frame into thirds
                width_third = width // 3  #divide frame width in 3 equal parts
                height_third = height // 3  #divide frame height in 3 equal parts

                #determine horizontal position based on center_x
                if center_x < width_third:
                    horizontal_position = "left"
                elif center_x > 2 * width_third:
                    horizontal_position = "right"
                else:
                    horizontal_position = "center"

                #determine vertical position based on center_y
                if center_y < height_third:
                    vertical_position = "top"
                elif center_y > 2 * height_third:
                    vertical_position = "bottom"
                else:
                    vertical_position = "center"

                #create the combined position
                if vertical_position == "center" and horizontal_position == "center":
                    position = "center"
                else:
                    position = f"{vertical_position} {horizontal_position}"

                #write in the log file
                f.write(
                    f"Detected {label} with confidence {score:.2f} in position: {position}\n")  #write in the log_file what object has been detected with what confidence in what position
                #the .2f ensures that the confidence score is written using only 2 decimal places

        interval = 5  #interval between detections in seconds
        time.sleep(interval)


picam2 = Picamera2() #create instance of Picamera2 to manage the camera
picam2.start_preview() #start camera preview
picam2.start() #capture frames from camera
def get_frame():
    return picam2.capture_array() #capture and return a single frame as array

print(f"Logging results to {log_file}")

while True:
    frame = picam2.capture_array("main") #capture a frame from the main stream continuously
    process_frame(frame)  #process captured frame (see line 61)

picam2.stop() #stop camera
