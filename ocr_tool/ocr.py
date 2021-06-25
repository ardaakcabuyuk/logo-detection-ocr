import cv2
import numpy as np
import tesserocr as tr
from PIL import Image
import matplotlib.pyplot as plt
import keras_ocr
from spellchecker import SpellChecker
import sys
import os
import pathlib

def draw_line_boxes(image_path, show=False):
  cv_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
  pil_img = Image.fromarray(cv2.cvtColor(cv_img,cv2.COLOR_BGR2RGB))

  api = tr.PyTessBaseAPI()
  try:
    api.SetImage(pil_img)
    boxes = api.GetComponentImages(tr.RIL.TEXTLINE,True)
    text = api.GetUTF8Text()

    for (im,box,_,_) in boxes:
      x,y,w,h = box['x'],box['y'],box['w'],box['h']
      cv2.rectangle(cv_img, (x,y), (x+w,y+h), color=(0,0,255))
  finally:
    api.End()

  if show:
    cv2.imshow(cv_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

  return boxes

def crop_lines_from_image(image_path, line_boxes, threshold=.05):
  img = Image.open(image_path)
  img = img.convert('RGB')

  for box_no, (_,box,_,_) in enumerate(line_boxes):
    cropped_img = img.crop((box['x'] - box['w'] * threshold, box['y'] - box['h'] * threshold,
                            box['x'] + box['w'] + box['w'] * threshold, box['y'] + box['h'] + box['h'] * threshold))
    cropped_img.save('line_box_{}.jpg'.format(box_no + 1))

def predict_words(line_box_count, plot=False):
  pipeline = keras_ocr.pipeline.Pipeline()

  images = [
    keras_ocr.tools.read("line_box_" + str(url+1) + ".jpg") for url in range(line_box_count)
  ]

  prediction_groups = pipeline.recognize(images)

  if plot:
    fig, axs = plt.subplots(nrows=len(images), figsize=(20, 20))
    for ax, image, predictions in zip(axs, images, prediction_groups):
        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)

  return prediction_groups

def get_key_text(prediction_groups):
  sorted_groups = []
  all_words = []
  spell = SpellChecker()

  for group in prediction_groups:
    group.sort(key=lambda group: group[1][0][0])
    sorted_groups.append(group)
    words = []
    for word, _ in group:
      misspelled = spell.unknown([word])

      for mis in misspelled:
          word = spell.correction(mis)

      words.append(word)
    all_words.append(','.join(words))
  return ','.join(all_words)

def predict_key_words(image_path ,plot=False):
  pipeline = keras_ocr.pipeline.Pipeline()

  images = [
      keras_ocr.tools.read(url) for url in [
          image_path
      ]
  ]

  prediction_groups = pipeline.recognize(images)

  if plot:
    fig, axs = plt.subplots(nrows=len(images), figsize=(20, 20))
    for ax, image, predictions in zip(axs, images, prediction_groups):
        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)

  return prediction_groups

#todo save in txt?
def get_image_text(prediction_groups):
  sorted_groups = []
  all_words = []
  spell = SpellChecker()

  for group in prediction_groups:
    group.sort(key=lambda group: group[1][0][0])
    sorted_groups.append(group)
    words = []
    for word, _ in group:
      misspelled = spell.unknown([word])

      for mis in misspelled:
          word = spell.correction(mis)

      words.append(word)
    all_words.append(' '.join(words))
  return '\n'.join(all_words)

class OCR():
    def __init__(self, image_path):
        self.image_path = image_path

    def extract(self):
        line_boxes = draw_line_boxes(self.image_path)
        crop_lines_from_image(self.image_path, line_boxes)
        prediction_groups = predict_words(len(line_boxes))
        text = get_image_text(prediction_groups)
        self.clear_workspace()
        return text

    def clear_workspace(self):
        os.system('rm line_box*')

    def extract_key_words(self):
        prediction_groups = predict_key_words(self.image_path)
        text = get_key_text(prediction_groups)
        return text
