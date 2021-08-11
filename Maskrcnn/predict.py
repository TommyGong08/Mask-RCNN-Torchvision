import os
import numpy as np
import torch
from PIL import Image

import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

import sys
sys.path.append("./detection")
from engine import train_one_epoch, evaluate
import utils
import transforms as T
import cv2
import cv2_util

import random
import time
import datetime


def random_color():
    b = random.randint(0,255)
    g = random.randint(0,255)
    r = random.randint(0,255)
    return (b, g, r)


def toTensor(img):
    assert type(img) == np.ndarray, 'the img type is {}, but ndarry expected'.format(type(img))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = torch.from_numpy(img.transpose((2, 0, 1)))
    return img.float().div(255)  # 255也可以改为256


def PredictImg(image, model, device):
    # print(image.shape)
    # img, _ = dataset_test[0]
    img = cv2.imread(image)
    print(img.shape)
    result = img.copy()
    dst = img.copy()
    img = toTensor(img)
    print(img.shape)
    names = {'0': 'background', '1': 'train'}
    # put the model in evaluati
    # on mode

    prediction = model([img.to(device)])

    boxes = prediction[0]['boxes']
    labels = prediction[0]['labels']
    scores = prediction[0]['scores']
    masks = prediction[0]['masks']

    m_bOK = False
    for idx in range(boxes.shape[0]):
        if scores[idx] >= 0.8:
            m_bOK = True
            # color = random_color()
            color = 0, 255, 0
            mask = masks[idx, 0].mul(255).byte().cpu().numpy()
            thresh = mask
            contours, hierarchy = cv2_util.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
            )
            cv2.drawContours(dst, contours, -1, color, -1)

            x1, y1, x2, y2 = int(boxes[idx][0]), int(boxes[idx][1]), int(boxes[idx][2]), int(boxes[idx][3])
            name = names.get(str(labels[idx].item()))
            cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness=2)
            cv2.putText(result, text=name, org=(x1, y1+10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                fontScale=0.6, thickness=2, lineType=cv2.LINE_AA, color=(0, 0, 0))

            dst1 = cv2.addWeighted(result, 0.5, dst, 0.5, 0)
            print(dst1.shape)
    if m_bOK:
        cv2.imwrite("result_img/result2.png", dst1)
        cv2.imshow('result', dst1)
        cv2.waitKey()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    num_classes = 2
    print("####")
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=False, num_classes=num_classes)
    model.to(device)
    model.eval()
    save = torch.load('./model/train_seg_model.pth')
    model.load_state_dict(save['model'])
    start_time = time.time()
    PredictImg('2.jpg', model, device)
    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    print('Training time {}'.format(total_time_str))
    print(total_time)
