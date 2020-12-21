from pathlib import Path
import shutil
import json
import os
from argparse import ArgumentParser

def bdd2coco(from_file, save_to, size=10, path_to_images=None, copy_images=True, labels_filename="labels", make_zip=False):
  annotations, categories, images = [], [], []
  ann_list, cat_list, img_list = [], [], []

  # Create temporary dict
  img_temp = {}
  cat_temp = {}

  cat_id = 0
  for idx, annotation in enumerate(json.load(open(from_file))):
    if idx >= size:
      break
    
    if annotation['name'] not in img_temp:
      img_temp[annotation['name']] = annotation['name'].split('.')[0]
      images.append({'file_name' : annotation['name'], 'id' : annotation['name'].split('.')[0]})
    
    if annotation['labels'] is not None:
      for label in annotation['labels']:
        box2d = label['box2d']
        bbox = [box2d['x1'], box2d['y1'], box2d['x2'] - box2d['x1'], box2d['y2'] - box2d['y1']]

        if label['category'] not in cat_temp:
          cat_temp[label['category']] = cat_id
          categories.append({'id' : cat_id, 'name' : label['category']})
          cat_id += 1
        
        box_annotation = {}
        box_annotation['bbox'] = bbox
        box_annotation['category_id'] = cat_temp[label['category']]
        box_annotation['image_id'] = img_temp[annotation['name']]
        annotations.append(box_annotation)

  coco = {'annotations' : annotations, 'images' : images, 'categories' : categories}

  if Path(save_to).exists() and Path(save_to).is_dir():
    shutil.rmtree(save_to)

  Path(save_to).mkdir(parents=True, exist_ok=True)
  Path(save_to + '/labels').mkdir(parents=True, exist_ok=True)

  with open(save_to + '/labels/' + labels_filename + '.json', 'w+') as outfile:
    json.dump(coco, outfile)

  data = json.load(open(save_to + '/labels/' + labels_filename + '.json'))

  if copy_images:
    Path(save_to + '/images').mkdir(parents=True, exist_ok=True)
    if path_to_images is None:
      path_to_images = Path(Path(from_file).parent.parent.parent/'images/100k/train/')
    for d in data['images']:
      shutil.copy('/content/bdd100k/images/100k/train/' + d['file_name'], save_to + '/images')
  archive_name = save_to.split('/')[-1]
  
  if make_zip:
    os.system("zip -r " + archive_name + ".zip "  + save_to)

def make_parser():
    parser = ArgumentParser(description="MongoDB to PostgreSQL migrator")
    
    parser.add_argument('--from-file', '-from_file', type=str, required=True,
                        help='BDD JSON source')
    parser.add_argument('--save-to', '-save_to', type=str, required=True,
                        help='Folder where images and labels will be stored after conversion')
    parser.add_argument('--size', '-size', type=str, required=True,
                        help='Number of images to work on')
    parser.add_argument('--path_to_images', '-pghost', type=str, required=False,
                        help='Path to BDD images')
    parser.add_argument('--copy-images', '-copy_images', type=bool, required=False,
                        help='Copy images from BDD source to save_to location')
    parser.add_argument('--labels-filename', '-labels_filename', type=str, required=False,
                        help='New .json labels file name')
    parser.add_argument('--make-zip', '-make_zip', type=str, required=False,
                        help='Create a zip archive with labels and images')
    return parser

if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()
    
    bdd2coco(args.from_file, args.save_to, args.path_to_images, args.copy_images, args.labels_filename, args.make_zip)

    