# Import packages
import os
import cv2
import numpy as np
from threading import Thread
import importlib.util
import time

pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter


class VideoStream:
    """Camera object that controls video streaming from the Picamera"""

    def __init__(self, resolution=(640, 480)):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
        # Start the thread that reads frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # Return the most recent frame
        return self.frame

    def stop(self):
        # Indicate that the camera and thread should be stopped
        self.stopped = True


# Define and parse input arguments
MODEL_NAME = 'tflite_model'
GRAPH_NAME = 'detect.tflite'
LABELMAP_NAME = 'labelmap.txt'
min_conf_threshold = 0.5
resW, resH = '1280x720'.split('x')
imW, imH = int(resW), int(resH)

CWD_PATH = os.getcwd()

# Path to .tflite file, which contains the model that is used for object detection
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, GRAPH_NAME)

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, MODEL_NAME, LABELMAP_NAME)

# Load the label map
with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del (labels[0])


class ObjectDetectionModel:

    def __init__(self):
        # Load the Tensorflow Lite model.
        self.interpreter = Interpreter(model_path=PATH_TO_CKPT)

        self.interpreter.allocate_tensors()

    def run(self, q=None):
        # Initialize video stream
        # Get model details
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]

        floating_model = (input_details[0]['dtype'] == np.float32)

        input_mean = 127.5
        input_std = 127.5
        self.videostream = VideoStream(resolution=(imW, imH)).start()
        # for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
        while True:

            # Grab frame from video stream
            frame1 = self.videostream.read()

            # Acquire frame and resize to expected shape [1xHxWx3]
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            self.interpreter.set_tensor(input_details[0]['index'], input_data)
            self.interpreter.invoke()

            # Retrieve detection results
            classes = self.interpreter.get_tensor(output_details[1]['index'])[0]  # Class index of detected objects
            scores = self.interpreter.get_tensor(output_details[2]['index'])[0]  # Confidence of detected objects

            # Loop over all detections and draw detection box if confidence is above minimum threshold
            display_str = []
            for i in range(len(scores)):
                if (scores[i] > min_conf_threshold) and (scores[i] <= 1.0):
                    # Draw label
                    object_name = labels[int(classes[i])]  # Look up object name from "labels" array using class index
                    if object_name in ('bus', 'truck', 'car'):
                        label = 'car'
                        display_str.append(label)
                    elif object_name in ('bicycle', 'motorcycle'):
                        label = 'motorbike'
                        display_str.append(label)
                    elif object_name == 'person':
                        label = 'human-handsdown'
                        display_str.append(label)

            if q:
                q.queue.clear()
                q.put(display_str)
            time.sleep(1)

    def cleanup(self):
        if self.videostream:
            self.videostream.stop()


if __name__ == '__main__':
    obj = ObjectDetectionModel()
    obj.run()
