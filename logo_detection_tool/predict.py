import os
from PIL import Image
import sys
import cv2
import matplotlib.pyplot as plt
import pathlib

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
  os.system('cd ..; cd darknet; ./darknet detector test build/darknet/x64/data/obj.data cfg/yolo-obj.cfg backup/yolo-obj_final.weights ' + os.path.dirname(pathlib.Path().absolute()) + '/images/' + image_name + ' -dont_show')

def get_logo_boxes(image_name):
  boxes = []
  image_raw = image_name.split(".")[0]

  with open(os.path.dirname(pathlib.Path().absolute()) + '/images/' + image_raw + ".txt", 'r') as f:
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
    os.system('rm ' + os.path.dirname(pathlib.Path().absolute()) + '/images/*.txt')
    return boxes

def crop_logos(image_name, boxes):
  print(os.path.dirname(pathlib.Path().absolute()) + '/images/' + image_name)
  img = Image.open(os.path.dirname(pathlib.Path().absolute()) + '/images/' + image_name)
  image_raw = image_name.split(".")[0]

  for box_no, box in enumerate(boxes):
    cropped_img = img.crop(box)
    cropped_img = cropped_img.convert('RGB')
    cropped_img.save(os.path.dirname(pathlib.Path().absolute()) + '/logos/' + image_raw + '_box_{}.jpg'.format(box_no + 1))
    print('logo saved at', os.path.dirname(pathlib.Path().absolute()) + '/logos/' + image_raw + '_box_{}.jpg'.format(box_no + 1))

class Detector():
    def __init__(self, image_name):
        self.image_name = image_name

    def predict(self):
        predict_image(self.image_name)
        boxes = get_logo_boxes(self.image_name)
        crop_logos(self.image_name, boxes)
