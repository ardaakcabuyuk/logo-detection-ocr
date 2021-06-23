import opendatasets as od
import os
import shutil
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import random
from PIL import Image

def download_dataset():
  dataset_url = 'https://www.kaggle.com/lyly99/logodet3k'
  od.download(dataset_url)

def prepare_transfer_learning_data(dataset_root):
  #create & write label file
  with open('darknet/build/darknet/x64/data/obj.names', mode='w+') as f:
    f.write('Logo')

  #rename image names
  for d in os.listdir(dataset_root):
    for logo in os.listdir(os.path.join(dataset_root, d)):
      for file in os.listdir(os.path.join(dataset_root, d, logo)):
        os.rename(os.path.join(dataset_root, d, logo, file), os.path.join(dataset_root, d, logo) + '/' + logo + '_' + file)

  #copy images to yolo's dataset directory
  if not os.path.exists('darknet/build/darknet/x64/data/obj'):
    os.makedirs('darknet/build/darknet/x64/data/obj')

  for r, d, f in os.walk(dataset_root):
    for file in tqdm(f):
        if file.endswith('.jpg'):
            shutil.copyfile(os.path.join(r, file), 'darknet/build/darknet/x64/data/obj/' + file)

  #read image information (labels) from xml
  done = 0
  for d in os.listdir(dataset_root):
    for logo in os.listdir(os.path.join(dataset_root, d)):
      for file in os.listdir(os.path.join(dataset_root, d, logo)):
          if file.endswith('.xml'):
            tree = ET.parse(os.path.join(dataset_root, d, logo, file))
            tree_root = tree.getroot()
            tags = [(i.tag, i.text) for i in tree_root.iter()]
            box_info = []
            for i, tag in enumerate(tags):
              if tag[0] == 'xmin':
                box_info.append(tags[i:i+4])

              if tag[0] == 'width':
                width = int(tag[1])

              if tag[0] == 'height':
                height = int(tag[1])

            open('darknet/build/darknet/x64/data/obj/' + file[:-4] + '.txt', 'w').close()

            with open('darknet/build/darknet/x64/data/obj/' + file[:-4] + '.txt', 'w+') as txt:
              for box in box_info:
                xmin = int(box[0][1])
                ymin = int(box[1][1])
                xmax = int(box[2][1])
                ymax = int(box[3][1])

                box_width_relative = (xmax - xmin) / width
                box_height_relative = (ymax - ymin) / height
                box_center_x_relative = ((xmax + xmin) / 2) / width
                box_center_y_relative = ((ymax + ymin) / 2) / height

                txt.write(' '.join(['0', str(box_center_x_relative), str(box_center_y_relative), str(box_width_relative), str(box_height_relative)]))
                txt.write('\n')

            done += 1
            print('done {} logos'.format(done))

  #train & validation & test split
  train = open('darknet/build/darknet/x64/data/train.txt', 'w+')
  test = open('darknet/build/darknet/x64/data/test.txt', 'w+')
  val = open('darknet/build/darknet/x64/data/val.txt', 'w+')
  total_set = []

  for r, d, f in os.walk(dataset_root):
    for file in f:
        if file.endswith('.jpg'):
          total_set.append(file)

  random.shuffle(total_set)

  train_size = (len(total_set) * 80) // 100
  val_size = (len(total_set) * 10) // 100
  test_size = (len(total_set) * 10) // 100

  train_set = total_set[:train_size]
  val_set = total_set[train_size : train_size + val_size]
  test_set = total_set[train_size + val_size:]

  for file in train_set:
    train.write('build/darknet/x64/data/obj/' + file + '\n')

  for file in val_set:
    val.write('build/darknet/x64/data/obj/' + file + '\n')

  for file in test_set:
    test.write('build/darknet/x64/data/obj/' + file + '\n')

def main():
  dataset_root = 'logodet3k/LogoDet-3K'
  download_dataset()
  prepare_transfer_learning_data(dataset_root)

if __name__ == __main__:
  main()
