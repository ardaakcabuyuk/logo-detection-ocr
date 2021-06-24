import os
from PIL import Image
import cv2
import matplotlib.pyplot as plt
import pathlib
import sys
sys.path.append("..")
from ocr_tool.ocr import OCR


# define helper functions
def imShow(path):
  image = cv2.imread(path)
  height, width = image.shape[:2]
  resized_image = cv2.resize(image,(3*width, 3*height), interpolation = cv2.INTER_CUBIC)

  fig = plt.gcf()
  fig.set_size_inches(18, 10)
  plt.axis("off")
  plt.imshow(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
  plt.show()

def predict_image(image_name):
  os.system('cd darknet; ./darknet detector test build/darknet/x64/data/obj.data cfg/yolo-obj.cfg backup/yolo-obj_final.weights ' + str(pathlib.Path().absolute()) + '/images/' + image_name + ' -dont_show')

def get_logo_boxes(image_name):
  boxes = []
  image_raw = image_name.split(".")[0]

  with open(str(pathlib.Path().absolute()) + '/images/' + image_raw + ".txt", 'r') as f:
    rects = f.readlines()
    for line in rects:
      line = line[:-1]
      box_list = line.split(',')
      for i in range(len(box_list)):
        box_list[i] = int(box_list[i])

      box_width = box_list[2] - box_list[0]
      box_height = box_list[3] - box_list[1]

      threshold = .05
      box_list[0] -= int(box_width * threshold)
      box_list[1] -= int(box_height * threshold)
      box_list[2] += int(box_width * threshold)
      box_list[3] += int(box_height * threshold)

      for i in range(len(box_list)):
        if box_list[i] < 0:
          box_list[i] = 0

      box_tup = tuple(box_list)
      boxes.append(box_tup)
    os.system('rm ' + str(pathlib.Path().absolute()) + '/images/*.txt')
    return boxes

def crop_logos(image_name, boxes):
  print(str(pathlib.Path().absolute()) + '/images/' + image_name)
  img = Image.open(str(pathlib.Path().absolute()) + '/images/' + image_name)
  image_raw = image_name.split(".")[0]

  for box_no, box in enumerate(boxes):
    cropped_img = img.crop(box)
    cropped_img = cropped_img.convert('RGB')
    cropped_img.save(str(pathlib.Path().absolute()) + '/logos/' + image_raw + '_logo_{}.jpg'.format(box_no + 1))
    print('logo saved at' + str(pathlib.Path().absolute()) + '/logos/' + image_raw + '_logo_{}.jpg'.format(box_no + 1))

class Detector():
    def __init__(self, image_name):
        self.image_name = image_name

    def detect(self):
        predict_image(self.image_name)
        boxes = get_logo_boxes(self.image_name)
        if len(boxes) != 0:
            crop_logos(self.image_name, boxes)

class Recognizer():
    def __init__(self, image_name):
        self.image_name = image_name

    def recognize(self):
        image_raw = self.image_name.split(".")[0]
        logo_count = 0
        logo_names = open(str(pathlib.Path().absolute()) + '/logos/' + image_raw + '_logos.txt', 'w+')
        while True:
            try:
                logo = str(pathlib.Path().absolute()) + '/logos/' + image_raw + '_logo_{}.jpg'.format(logo_count + 1)
                ocr = OCR(logo)
                logo_name = ocr.extract()
                print('logo: ' + logo_name)
                logo_names.write(logo_name + '\n')
                logo_count += 1
            except:
                break
