import cv2
import numpy as np
import argparse
import matplotlib.pyplot as plt
import json
import os
from scipy.spatial import distance
import glob
from skimage.transform import resize
import multiprocessing as mp
from multiprocessing import Pool
import time

start = time.perf_counter()
"""
This function defines the command-line arguments
"""

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help = "Figures input directory")
    parser.add_argument("--amazonDirectory", help = "Amazon label bounding boxes")
    parser.add_argument("--outputDirectory", help = "directory to save the segmented images")
    parser.add_argument("--jsonDirectory", help = "directory to save the json output")
    parser.add_argument("--TransformerDirectory", help = "directory to store the output of the Transformer model")
    parser.add_argument("--processingDirectory", help = "directory to store the output of resizing the images")
    
    return parser

"""This function takes a single amazon file and search for its corresponding
figure. If the image is found, it returns the image relative path and its
amazon label information.
"""    
def match_files(index):
    
    parser = get_args()
    args = parser.parse_args()
    img_dir = args.file_path
    amazon_dir = args.amazonDirectory
    img_paths = os.listdir(img_dir)
    amazon_files = os.listdir(amazon_dir)
    current_ama = amazon_files[index]
    amazon_fpath = os.path.join(amazon_dir, current_ama)
    try:

        img_to_search = current_ama[7:-4] + 'png'
        if img_to_search in img_paths and os.stat(amazon_fpath).st_size != 0:
            label_path = open(amazon_fpath, 'r', encoding = 'utf-8')
            label_info = json.load(label_path)
        
            return img_to_search, label_info
    except Exception as error:
        print(error)

"""This function takes in the label info and returns label
bounding box and label name
"""

def extract_label_bboxes(index):
    bounding_boxes = {}
    label_name = {}
    img_rel_path,label_info = match_files(index)
    
    try:
        
        if type(label_info) is dict and "TextDetections" in label_info.keys():
            contents = label_info['TextDetections']
            for i, j in enumerate(contents):
                if j['Type'] == 'LINE' and j["Confidence"] >= 75:
                    bbox = j['Geometry']['BoundingBox']
                    label = j['DetectedText']
                    bounding_boxes[i] = bbox
                    label_name[i] = label
        else:
            for i, j in enumerate(label_info):
                if j['Type'] == 'LINE' and j["Confidence"] >= 75:
                    bbox = j['Geometry']['BoundingBox']
                    label = j['DetectedText']
                    bounding_boxes[i] = bbox
                    label_name[i] = label
    except Exception as error:
        print(error)
    
    return bounding_boxes, label_name

    
"""
This function takes in the index of the figure label, extracts the dimensions
of the label coordinates, and converts it back to the original unit.
We import extract_label_bboxes from Amazon_label
"""
def label_points(index):
    parser = get_args()
    args = parser.parse_args()
    img_dirs = args.file_path
    bbox, _ = extract_label_bboxes(index)
    label_conv_points = []
    img_path, _ = match_files(index)
    try:
        img = cv2.imread(os.path.join(img_dirs, img_path))
    
        for k, v in bbox.items():
            if img is not None:
                h, w = img.shape[:2]
                width, height = v['Width'], v['Height']
                left, top = v['Left'], v['Top']
    
                # convert back the amazon coordinates to the original coordinates
                width = int(width * w)
                height = int(height * h)
                left = int(left * w)
                top = int(top * h)
                label_conv_points.append((left, width, top, height))
            else:
                break    
    except Exception as error:
        print(error)
    return label_conv_points, img_path


""" 
This function loads the image and wipe out the labels 
using label coordinates from Amazon Rekognition tool
"""
def figure_only(index):
        
    # get patent id
    parser = get_args()
    args = parser.parse_args()
    #amazon_paths = args.amazonDirectory  # Amazon label results
    output_dir = args.outputDirectory  # directory to save the segmented figures
   # img_paths = get_files()  # All the figures paths
    label_coord, img_path = label_points(index)
    img_dir = args.file_path   # figures directories  
    image = cv2.imread(os.path.join(img_dir, img_path))
    try:    
       # case for a single image
       if len(label_coord) == 1:
           # unpack the coordinates
           left, width, top, height = label_coord[0]
           # set the pixels in those location to white to wipe out the labels
           image[(top - 1) : (top + height + 1), (left - 1): (left + width + 1)] = (255, 255, 255)
        
#           cv2.imwrite(os.path.join(output_dir, img_path), image)
       else:  
            
           # case for image with subfigures
           for label in label_coord:
               # unpack the coordinates
               left, width, top, height = label
               # set the pixels in those location to white to wipe out the labels
               image[(top - 1) : (top + height + 1), (left - 1): (left + width + 1)] = (255, 255, 255)
            
#           cv2.imwrite(os.path.join(output_dir, img_path), image)
    except Exception as error:
        print(error)

    return image, img_path


"""This function takes the figure without labels and resize it so we can apply the
transformer model on it."""
def preprocessing(index):
    parser = get_args()
    args = parser.parse_args()
    process_dir = args.processingDirectory
    try:

        img, img_path = figure_only(index)
        image = original = img.copy()
    
        #### Saving input images #################
        original_res= resize(image, (128, 128, 3), mode='constant', preserve_range=True)
        cv2.imwrite(os.path.join(process_dir, img_path), original_res)
    except Exception as error:
        print(error)
    #return original_res, img_path

parser = get_args()
args = parser.parse_args()
img_paths = args.file_path
rel_paths = os.listdir(img_paths)

if __name__ == "__main__":
    indices = list(range(len(rel_paths)))
    p = mp.cpu_count()   # count the number of cpus
    process = Pool(p)
    result = process.map(preprocessing, indices)
    process.close()
    process.join()

finish = time.perf_counter()

print("Finished in {} seconds".format(round(finish - start), 2))