
import cv2
import zmq
import numpy
from PIL import Image
import numpy as np

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

blank_image = np.zeros((256,256,3), np.uint8)

while True:

    # ZMQ Subscribe convert incoming bytes to PIL and then to CVImage
    frame = socketSubscribe.recv()
    if len(frame) > 10:
        pil_image = Image.frombytes('RGBA', (256,256), frame, 'raw').convert('RGB')
        open_cv_image = numpy.array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        blank_image = open_cv_image
        cv2.imshow("Subscribe: image",open_cv_image)

    # ZMQ Publish
    if len(frame) > 10:
        socketPublish.send(blank_image)

    cv2.waitKey(1)

