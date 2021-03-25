
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from util import util

import cv2
import numpy
from PIL import Image
import numpy as np
import pyrealsense2 as rs
import time

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()


# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

#config.enable_stream(rs.stream.color, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

width = 512
height = 512

# Start streaming
pipeline.start(config)
max_lowThreshold = 100
window_name = 'Edge Map'
title_trackbar = 'Min Threshold:'
ratio = 3
kernel_size = 3

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
    blank_image = np.zeros((height, width, 3), np.uint8)
    print("start while loop")

    start_time = time.time()
    x = 5  # displays the frame rate every 1 second
    counter = 0
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        #blank_image[5:10 , 5:10] = (255, 0, 0)  # [x.1,x.2 , y.1,y.2] (B, G, R)

        black_image = np.zeros((height, width, 3), np.uint8)
        center_coordinates = (int(height/2), int(width/2))
        radius = int(height/2)
        color = (255, 255, 255)
        thickness = int(height/4)
        mask = cv2.circle(black_image, center_coordinates, radius, color, thickness)
        #mask = cv2.resize(mask,(height,width),interpolation=cv2.INTER_AREA)

        background_color = np.zeros((height, width, 3), np.uint8)
        background_color[0:height, 0:width] = (132, 132, 132)

        background_color = cv2.add(mask,background_color)

        object_color = np.zeros((height, width, 3), np.uint8)
        object_color[0:height, 0:width] = (76, 76, 76)

        mask = cv2.bitwise_not(mask)
        object_color = cv2.add(mask,object_color)

        backAndForeground = cv2.multiply(object_color,background_color,scale = 0.003922)

        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.resize(color_image, (height, width), interpolation=cv2.INTER_AREA)

        edges = auto_canny(color_image)
        edges = cv2.merge((edges,edges,edges))
        mask = cv2.bitwise_not(mask)
        edges = cv2.multiply(mask,edges)

        image = cv2.add(edges,backAndForeground)
        edges = cv2.bitwise_not(edges)
        image = cv2.multiply(edges,image,scale = 0.003922)

        pil_image = Image.fromarray(image)

        for i, data in enumerate(dataset):
            if i >= opt.num_test:  # only apply our model to opt.num_test images.
                break
            model.set_input(data, pil_image)  # unpack data from data loader

            model.test()           # run inference

            visuals = model.get_current_visuals()  # get image results
            for label, im_data in visuals.items():
                im = util.tensor2im(im_data)
                open_cv_image = numpy.array(im)
                open_cv_image = open_cv_image[:, :, ::-1].copy()
                #blank_image = cv2.addWeighted(blank_image,0.5,open_cv_image,0.5,0.003922)
                blank_image = open_cv_image
        showimage = cv2.resize(blank_image,(256,256), interpolation=cv2.INTER_AREA)
        cv2.imshow("pix2pix", blank_image)
        cv2.imshow("image", image)
        cv2.waitKey(1)

        counter += 1
        if (time.time() - start_time) > x:
            print("FPS: ", counter / (time.time() - start_time))
            counter = 0
            start_time = time.time()
