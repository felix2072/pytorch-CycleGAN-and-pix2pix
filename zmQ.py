
import cv2
import zmq
import numpy
from PIL import Image
import numpy as np
import time


def printFPS(_counter ,_start_time , _x):
    _counter += 1
    if (time.time() - _start_time) > _x:
        print("FPS: ", _counter / (time.time() - _start_time))
        _counter = 0
        _start_time = time.time()
    return _counter, _start_time

# ZMQ
context = zmq.Context()
contextPublish = zmq.Context()

# ZMQ Subscribe
socketSubscribe = context.socket(zmq.SUB)
socketSubscribe.connect("tcp://localhost:5555")
socketSubscribe.setsockopt_string(zmq.SUBSCRIBE, "img")

# ZMQ publish
socketPublish = contextPublish.socket(zmq.PUB)
socketPublish.bind("tcp://*:5556")

model_image_size = 1024

blank_image = np.zeros((model_image_size, model_image_size, 3), np.uint8)

start_time = time.time()
x = 5  # displays the frame rate every 1 second
counter = 0
while True:

    # ZMQ Subscribe convert incoming bytes to PIL and then to CVImage
    frame = socketSubscribe.recv()

    if len(frame) > 10:
        pil_image = Image.frombytes('RGBA', (model_image_size, model_image_size), frame, 'raw').convert('RGB')
        open_cv_image = numpy.array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        blank_image = open_cv_image
        cv2.imshow("Subscribe: image",open_cv_image)

        socketPublish.send(blank_image)

    cv2.waitKey(1)
    temp = printFPS(counter,start_time,x)
    counter = temp[0]
    start_time = temp[1]
