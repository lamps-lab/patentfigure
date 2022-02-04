import cv2
import numpy as np
import argparse
#import matplotlib.pyplot as plt
import json
import os
#from scipy.spatial import distance
import glob
from skimage.transform import resize
from scipy.spatial import distance
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
    parser.add_argument("--jsonFilename", help = "Name of output json file")
    
    return parser

"""This function gets the amazon directories to ensure proper alignment with figure files, loads 
the json file for the current figure file.
"""    
def get_amazonFiles(index):
    
    parser = get_args()
    args = parser.parse_args()
    amazon_dir = args.amazonDirectory
    amazon_files = os.listdir(amazon_dir)
    # sort the amazon filenames
    amazon_files.sort()
    current_ama = amazon_files[index]
    amazon_fpath = os.path.join(amazon_dir, current_ama)
    try:
        # check if the amazon file in not empty
        if os.stat(amazon_fpath).st_size != 0:
            label_path = open(amazon_fpath, 'r', encoding = 'utf-8')
            label_info = json.load(label_path)
        
            return label_info
    except Exception as error:
        print(error)

"""This function sorts the figure files to properly align with the amazon files"""
def get_imageFiles():
    parser = get_args()
    args = parser.parse_args()
    img_dir = args.file_path
    img_paths = os.listdir(img_dir)
    # sort the amazon filenames
    img_paths.sort() 
    return img_paths

"""This function takes in the label info and returns label
bounding box and label name
"""
def extract_label_bboxes(index):
    bounding_boxes = {}
    label_name = {}
    label_info = get_amazonFiles(index)
    
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
    img_dir = args.file_path
    img_paths =  get_imageFiles()   # list of figure files
    bbox, _ = extract_label_bboxes(index)
    
    label_conv_points = []
    # get the current figure file
    current_img = img_paths[index]
    #img_path = os.path.join(img_dir, current_img)
    
    try:
        img = cv2.imread(os.path.join(img_dir, current_img))
    
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
    return label_conv_points, current_img


"""The function below helps to calculate the distance of the labels 
which will be used to find the distance between the images and the labels
"""
def calc_label_center(index):
    label_cent = []
    label_coord, _= label_points(index)
    try:
        
        # case for a single image
        if len(label_coord) == 1:
            left, width, top, height = label_coord[0]
            # Obtain the center coordinates by adding the top to the height / 2, and adding left to width / 2
            ptX, ptY = (width / 2 + left), (height / 2 + top)
            # save it in the label_cent list
            label_cent.append((ptX, ptY))
        
        else:   
            # case for image with subfigures
            for coord in label_coord:
                left, width, top, height = coord
                # Obtain the center coordinates by adding the top to the height / 2, and adding left to width / 2
   
                ptX, ptY = (width / 2 + left), (height / 2 + top)
                # save it in the label_cent list
                label_cent.append((ptX, ptY))
    except Exception as error:
        print(error)
    
    return label_cent

"""This function calculates the distance between the image and the labels"""
# # find the distance between the label coordinates and the image coordinates
def AmazonDist_label_image(image_mid, label_cent):
    D = {}
   
    try:
        
        if len(label_cent) == 1:
            # calculate the distance between the label and image
            dist = round(distance.euclidean(label_cent[0], image_mid), 2)
            D[0] = dist
        else:  
            # distance for image with subfigures   
            # loop through the label coordinates and unpack the coordinates
            for ind1, lab in enumerate(label_cent):
            
                # calculate the distance between the label and image
                dist = round(distance.euclidean(lab, image_mid), 2)
                D[ind1] = dist      
    except Exception as error:
        print(error)
    return D


""" 
This function loads the image and wipe out the labels 
using label coordinates from Amazon Rekognition tool
"""
def figure_only(index):
        
    # get patent id
    parser = get_args()
    args = parser.parse_args()
    output_dir = args.outputDirectory  # directory to save the segmented figures
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
        
        #   cv2.imwrite(os.path.join(output_dir, img_path), image)
       else:  
            
           # case for image with subfigures
           for label in label_coord:
               # unpack the coordinates
               left, width, top, height = label
               # set the pixels in those location to white to wipe out the labels
               image[(top - 1) : (top + height + 1), (left - 1): (left + width + 1)] = (255, 255, 255)
            
        #   cv2.imwrite(os.path.join(output_dir, img_path), image)
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
#rel_paths = os.listdir(img_paths)
rel_paths = range(50)  # just for testing

#This runs the processing in parallel across the cpu cores
if __name__ == "__main__":
    #indices = list(range(len(rel_paths)))
    indices = list(rel_paths)  # just for testing
    p = mp.cpu_count()   # count the number of cpus
    process = Pool(p)
    result = process.map(preprocessing, indices)
    process.close()
    process.join()

finish = time.perf_counter()

print("Finished in {} seconds".format(round(finish - start), 2))