
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from util import util

import cv2
import zmq
import numpy
from PIL import Image
import numpy as np
import time

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

model_image_size = 512

if __name__ == '__main__':
    opt = TestOptions().parse()  # get test options
    # hard-code some parameters for test
    opt.num_threads = 0   # test code only supports num_threads = 0
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
    opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.
    model = create_model(opt)      # create a model given opt.model and other options
    model.setup(opt)               # regular setup: load and print networks; create schedulers
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    blank_image = np.zeros((model_image_size, model_image_size, 3), np.uint8)

    while True:
        # ZMQ Subscribe convert incoming bytes to PIL and then to CVImage
        frame = socketSubscribe.recv()
        if len(frame) > 10:
            pil_image = Image.frombytes('RGBA', (model_image_size, model_image_size), frame, 'raw').convert('RGB')

            # learntest
            #model.update_learning_rate()

            for i, data in enumerate(dataset):
                if i >= opt.num_test:  # only apply our model to opt.num_test images.
                    break
                model.set_input(data, pil_image)  # unpack data from data loader

                # learntest
                #model.optimize_parameters()

                model.test()           # run inference

                visuals = model.get_current_visuals()  # get image results
                for label, im_data in visuals.items():
                    im = util.tensor2im(im_data)
                    open_cv_image = numpy.array(im)
                    open_cv_image = open_cv_image[:, :, ::-1].copy()
                    blank_image = open_cv_image
        #dim = (256,256)
        #blank_image = cv2.resize(blank_image, dim, interpolation = cv2.INTER_AREA)
        socketPublish.send(blank_image)
        cv2.imshow("image", blank_image)
        cv2.waitKey(1)