def predict(image_name):
  !./darknet detector test build/darknet/x64/data/obj.data cfg/yolo-obj.cfg backup/yolo-obj_last.weights image_name -dont_show
  imShow('predictions.jpg')

def get_logo_boxes(image_name):
  boxes = []
  image_raw = image_name.split(".")[0]

  with open(image_raw + ".txt", 'r') as f:
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

    return boxes

def crop_logos(image_name, boxes):
  img = Image.open(image_name)

  for box_no, box in enumerate(boxes):
    cropped_img = img.crop(box)
    cropped_img.save(image_raw + 'box{}.jpg'.format(box_no + 1))
    print('logo saved at', image_raw + '_box_{}.jpg'.format(box_no + 1))

def main():
  image_name = 'cvp.jpg'
  predict(image_name)
  boxes = get_logo_boxes(image_name)
  crop_logos(image_name, boxes)
