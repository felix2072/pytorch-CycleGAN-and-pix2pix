import socket
from options.test_options import TestOptions
from data import create_dataset
from models import create_model
import time
from util import util


UDP_IP = "127.0.0.1"
OUT_PORT = 5004
IN_PORT = 5005
buf = 1024
timeout = 3


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

    while True:
        print ("-------------------------")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        time.sleep(0.03)
        info = "need file"
        print(info)

        sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
        time.sleep(0.04)
        info = "end"
        print(info)
        sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, IN_PORT))
        while True:
            data, addr = sock.recvfrom(1024)
            if data.decode("utf-8") == "image saved":
                print("load base image")
                break

        dataset = create_dataset(opt)  # create a dataset given opt.dataset_mode and other options
        #print("dataset :%s was created" % dataset)

        for i, data in enumerate(dataset):
            if i >= opt.num_test:  # only apply our model to opt.num_test images.
                break
            model.set_input(data)  # unpack data from data loader
            model.test(i)           # run inference
            visuals = model.get_current_visuals()  # get image results
            for label, im_data in visuals.items():
                im = util.tensor2im(im_data)
                save_path = './datasets/{}/test_6result/fake{}.jpg'.format(opt.name,i)
                util.save_image(im, save_path, aspect_ratio=opt.aspect_ratio)

        info = "fake is ready"
        print(info)
        sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
        time.sleep(0.04)
        info = "end"
        print(info)
        sock.sendto(info.encode(), (UDP_IP, OUT_PORT))
        sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, IN_PORT))

        while True:
            print("wait for VL to load image")
            data, addr = sock.recvfrom(1024)
            if data.decode("utf-8") == "got fake":
                print("fake image")
                break
