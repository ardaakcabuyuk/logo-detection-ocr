from google.colab.patches import cv2_imshow
import cv2
import numpy as np
import tesserocr as tr
from PIL import Image
import matplotlib.pyplot as plt
import keras_ocr
from spellchecker import SpellChecker

def draw_line_boxes(image_name, show=False):
  cv_img = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)
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
    cv2_imshow(cv_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

  return boxes

def crop_lines_from_image(image_name, line_boxes, threshold=.05):
  img = Image.open(image_name)
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

def main():
  image_name = 'Capture.png'
  line_boxes = draw_line_boxes(image_name)
  crop_lines_from_image(image_name, line_boxes)
  prediction_groups = predict_words(len(line_boxes))
  text = get_image_text(prediction_groups)
  print(text)

if __name__ == '__main__':
  main()
