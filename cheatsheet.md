flickr scraper

git clone
---------------------------------------
git clone https://github.com/ultralytics/flickr_scraper


set flickr key in flickr_scraper.py
---------------------------------------
key = '0bf634316f4cc89c06b9c181fa50e3b5'  # Flickr API key https://www.flickr.com/services/apps/create/apply
secret = '06b99dbd62fd5552'


get 100 images with the tag people
---------------------------------------
python flickr_scraper.py --search 'people' --n 100 --download



imagemagick

bash install
---------------------------------------
apt install imagemagick

content of folder: from png to jpg
----------------------------------------
mogrify -format jpg *.png


one file: resize
----------------------------------------
convert [file].jpg -resize 256x256 [file_fuu_ba].jpg


content of folder: crop and resize
----------------------------------------
mogrify -set option:distort:viewport \
    "%[fx:min(w,h)]x%[fx:min(w,h)]+%[fx:max((w-h)/2,0)]+%[fx:max((h-w)/2,0)]" \
    -filter point -distort SRT 0  +repage -resize 256x256 *.jpg

content of folder: strech
----------------------------------------
mogrify -geometry 256x256! *.jpg


content of folder: slice
----------------------------------------
mogrify -crop 256x256 -gravity East *.png 

cyclegan and pix2pix

python -m visdom.server
PS E:\work\ML\pytorch-CycleGAN-and-pix2pix> python train.py --dataroot ./datasets/people2vase --name invert_people2vase --model cycle_gan --n_epochs 2000 --save_epoch_freq 5 --continue_train --epoch_count 200
PS E:\work\ML\pytorch-CycleGAN-and-pix2pix> python test.py --dataroot ./datasets/people2chair --name people2chair --model cycle_gan

python test.py --dataroot .\datasets\chair_pix2pix\test\ --name chair_pix2pix --model test --netG unet_256 --direction BtoA --dataset_mode single --norm batch --num_test 1
python test.py --dataroot .\datasets\chair_pix2pix\C\ --name chair_pix2pix --model pix2pix --direction BtoA

SPADE
---------------------------------------
test
python test.py --name coco_pretrained --dataset_mode coco --dataroot .\datasets\coco_stuff\
python test.py --name CamVid --dataset_mode custom --no_instance --label_nc 32 --preprocess_mode scale_width --label_dir datasets/CamVid/val_label --image_dir datasets\CamVid\val_img --load_size 512 --aspect_ratio 1.3333 --crop_size 512 --ngf 48
python train.py --name CamVid --dataset_mode custom --no_instance --label_nc 32 --preprocess_mode scale_width --label_dir datasets/CamVid/train_label --image_dir datasets/CamVid/train_img/ --load_size 512 --aspect_ratio 1.3333 --crop_size 512 --ngf 48 --ndf 48 --batchSize 1 --niter 50 --niter_decay 50 --tf_log 

'''

#not working onnx export
import torch.onnx
def save_network(net, label, epoch, opt):
    save_filename = '%s_net_%s.pth' % (epoch, label)
    save_path = os.path.join(opt.checkpoints_dir, opt.name, save_filename)
    torch.save(net.cpu().state_dict(), save_path)
    if len(opt.gpu_ids) and torch.cuda.is_available():
        net.cuda()
        save_filename = '%s_net_%s.onnx' % (epoch, label)
        save_path = os.path.join(opt.checkpoints_dir, opt.name, save_filename)
        inputs = torch.randn(768, 32, 3, 3)
        torch.onnx.export(net.cuda(), inputs.cuda(), save_path)

'''

conda -> python3.6 env
---------------------------------------
conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
conda install -c conda-forge dominate
