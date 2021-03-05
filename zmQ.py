
import cv2
import zmq
import numpy
from PIL import Image
import numpy as np

context = zmq.Context.instance()

# ZMQ Subscribe
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5555")
subscriber.setsockopt_string(zmq.SUBSCRIBE, "img")

# ZMQ publish
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://*:5556")

blank_image = np.zeros((256,256,3), np.uint8)

def subscriber_thread():
    global blank_image
    # ZMQ Subscribe convert incoming bytes to PIL and then to CVImage
    frame = subscriber.recv()
    if len(frame) > 10:
        pil_image = Image.frombytes('RGBA', (256,256), frame, 'raw').convert('RGB')
        open_cv_image = numpy.array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        blank_image = open_cv_image
        cv2.imshow("Subscribe: image",blank_image)


def publisher_thread():
    global blank_image
    publisher.send(blank_image)


def main():
    subscriber_thread()
    publisher_thread()
    cv2.waitKey(1)

if __name__ == '__main__':
    while True:
        main()
