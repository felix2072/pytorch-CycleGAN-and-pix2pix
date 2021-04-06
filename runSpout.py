from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from util import util
import time

from Library.Spout import Spout

import numpy
import numpy as np
import cv2
from PIL import Image


def print_fps(_frame_counter, _start_time, _seconds_to_wait):
    _frame_counter += 1
    if (time.time() - _start_time) > _seconds_to_wait:
        print("Average FPS: ", _frame_counter / (time.time() - _start_time))
        _frame_counter = 0
        _start_time = time.time()
    return _frame_counter, _start_time


def main():
    # create spout object
    spout = Spout(silent=False)
    # create receiver
    spout.createReceiver('vvvvideo')
    # create sender
    spout.createSender('output')

    opt = TestOptions().parse()  # get test options
    # hard-code some parameters for test
    opt.num_threads = 0  # test code only supports num_threads = 0
    opt.batch_size = 1  # test code only supports batch_size = 1
    opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
    opt.no_flip = True  # no flip; comment this line if results on flipped images are needed.
    opt.display_id = -1  # no visdom display; the test code saves the results to a HTML file.
    model = create_model(opt)  # create a model given opt.model and other options
    model.setup(opt)  # regular setup: load and print networks; create schedulers
    dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
    pix2pix_image = np.zeros((256, 256, 3), np.uint8)

    start_time = time.time()
    seconds_to_wait = 1
    frame_counter = 0

    while True:

        # check on close window
        spout.check()
        # receive data
        frame = spout.receive()

        if len(frame) > 10:
            #pil_image = Image.frombytes('RGBA', (model_image_size, model_image_size), frame, 'raw').convert('RGB')
            pil_image = Image.fromarray(frame)

            # learntest
            # model.update_learning_rate()

            for i, data in enumerate(dataset):
                if i >= opt.num_test:  # only apply our model to opt.num_test images.
                    break
                model.set_input(data, pil_image)  # unpack data from data loader

                # learntest
                # model.optimize_parameters()

                model.test()  # run inference

                visuals = model.get_current_visuals()  # get image results
                for label, im_data in visuals.items():
                    im = util.tensor2im(im_data)
                    open_cv_image = numpy.array(im)
                    #open_cv_image = open_cv_image[:, :, ::-1].copy()
                    pix2pix_image = open_cv_image
        # dim = (256,256)
        # blank_image = cv2.resize(blank_image, dim, interpolation = cv2.INTER_AREA)

        # send data
        spout.send(pix2pix_image)

        #cv2.imshow("image", pix2pix_image)
        #cv2.waitKey(1)

        counter_and_time = print_fps(frame_counter, start_time, seconds_to_wait)
        frame_counter = counter_and_time[0]
        start_time = counter_and_time[1]


if __name__ == "__main__":
    main()