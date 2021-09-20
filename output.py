import cv2
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
import os
import time
from skimage.io import imread, imshow, concatenate_images
from skimage.transform import resize
from PIL import Image,ImageDraw
import time
#from skimage.io import imread_collection
import argparse
import glob
from processing import *
from processing import *
import multiprocessing as mp
from multiprocessing import Pool, Process
import time

start = time.perf_counter()

"""This function gets the figure only and the transformer results and draw
a bounding box on the figure only to segment the subfigures
"""
def resize_boundingbox(index):
    print('Image is going to processed : ', index)
    parser = get_args()
    args = parser.parse_args()
    # original images
    img_dir = args.file_path
    img_only, rel_path = figure_only(index)
#    img_path = os.path.join(img_dir, rel_path)
    
    output_dir = args.outputDirectory
    # Transformer prediction images
    transformer_pred_dir = args.TransformerDirectory
    transf_img_rel_paths = os.listdir(transformer_pred_dir)
    transf_pred_path = os.path.join(transformer_pred_dir, rel_path)
    all_coordinates = []
    filename = os.path.join(output_dir, rel_path)    
    # Read the original and prediction images
    try: 
        
        ROI_number = 0
 #       img_orig = cv2.imread(img_path)
        img = img_only.copy()
        pred_orig = cv2.imread(transf_pred_path)
        preds = pred_orig.copy()
    
        """
        get the height and width of the original image: this will be used for converting the resized image 
        back to the original dimension 
        """
        orx = img.shape[1]
        ory = img.shape[0]
        scalex = orx / 128
        scaley = ory / 128
       
        # Added code by me
        gray = cv2.cvtColor(preds, cv2.COLOR_BGR2GRAY)
        canny_get_edge = cv2.Canny(gray, 40, 250)
        # Perform a little bit of morphology:
        # Set kernel (structuring element) size:
        kernelSize = (3, 3)
        # Set operation iterations:
        opIterations = 1
        # Get the structuring element:
        morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
        # Perform Dilate:
        morphology = cv2.morphologyEx(canny_get_edge, cv2.MORPH_CLOSE, morphKernel, None, None, opIterations, cv2.BORDER_REFLECT101) # preds
        contours, hierarchy = cv2.findContours(morphology, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
        im = img_only.copy()  
        
        all_coordinates=[]
        for c in contours:
            rect = cv2.boundingRect(c)
            if rect[2] < 5 or rect[3] < 5: continue
            cv2.contourArea(c)
            x, y, w, h = rect
            x = int(x*scalex)
            y = int(y*scaley)
            w = int(w* scalex)
            h = int(h * scaley)
           # cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
            ROI = im[y:y + h, x:x + w]
            #cv2.imwrite('ROI_{}_{}.png'.format(i, ROI_number), ROI)
            cv2.imwrite(filename[:-4] + "_{}.png".format(ROI_number), ROI)
            ROI_number = ROI_number + 1
            coordinates=(x, y, w, h)
            all_coordinates.append(coordinates)
    
    except Exception as error:
        print(error)
#        print(filename)    
#    return all_coordinates
    print('**************************** Resized the bounding Box ******************************* ')


"""This function fine tune the amazon rekognition results of the labels"""
def finetune_label(label_name):
    prefixes = ("FIG", "figure", "Figure", "fig", "FIGURE", "Fig")
    prefixes2 = ("FIG.", "figure.", "Figure.", "fig.", "FIGURE.", "Fig.")
    suffix = "."
    new_label_name = {}
    try:
        
        if len(label_name) == 1:
            for k, v in label_name.items():
                new_label_name[k] = v
        else:
        
            keys = list(label_name.keys())
            val = list(label_name.values())
            left = 0
            right = 1
            while right < len(keys) and left < len(keys):
                # First value starts with "FIG" and ends with a number
                if (val[left].startswith(prefixes) or val[left].startswith(prefixes2)) and val[left].endswith(tuple("0123456789")):
                    new_label_name[keys[left]] = val[left]
                    left += 1
                # Second starts with a "FIG" and ends with a number
                elif (val[right].startswith(prefixes)or val[right].startswith(prefixes2)) and val[right].endswith(tuple("0123456789")):
                    new_label_name[keys[right]] = val[right]
                    right += 1
                # first starts with a number and second starts with a "FIG" and ends with a number
                elif val[left].startswith(tuple("0123456789")) and val[right].startswith(prefixes) and val[right].endswith(suffix):
                    name = val[right] + val[left]
                    new_label_name[keys[left]] = name
                    left += 1
                    right += 1
                # first starts with a number and second starts with a "FIG"
                elif val[left].startswith(tuple("0123456789")) and val[right].startswith(prefixes):
                    name = val[right] + " " + val[left]
                    new_label_name[keys[left]] = name
                    left += 1
                    right += 1
                # first and second start with a number
                elif val[left].startswith(tuple("0123456789")) and val[right].startswith(tuple("0123456789")):
                    right += 1
                # first starts with a "FIG" and second starts with a number
                elif val[left].startswith(prefixes) and val[right].startswith(tuple("0123456789")):
                    left += 1
                    right += 1
                
                else:
                    right += 1
    except Exception as error:
        print(error)
    return new_label_name
            
"""Function to generate the final json file with all the metadata"""
def patent_json(index):
    json_name = {}
    sub_list = []

    # get patent id
    parser = get_args()
    args = parser.parse_args()
    img_paths = args.file_path
    try:
        _, img_path = figure_only(index)
        _, label_name = extract_label_bboxes(index)

        # call the function to format the label_name
        new_label_name = finetune_label(label_name)
        # case for figure with subfigures
        json_name['patent_id'] = os.path.splitext(img_path)[0]   # [:19]
        json_name["Figure_file"] = img_path
        json_name["n_subfigures"] = len(new_label_name)
        resize_boundingbox(index)
        # get the figure number . e.g. Fig.2
        for key, val in new_label_name.items():
            sub_file = {}
            num = ""
            for c in val:
                if c.isdigit():
                    num += c
            
            sub_file["subfigure_id"] = int(num) if num.isdigit() else (num + ".")
            sub_file["subfigure_file"] = (img_path[:-4] + "_" + num + '.png') if num.isdigit() else (img_path[:-4] + "_" + "." + '.png')
            sub_file["subfigure_label"] = val
            sub_list.append(sub_file)
        
        json_name['subfigurefile'] = sub_list
    except Exception as error:
        print(error)
    return json_name

#def output_json():
    parser = get_args()
    args = parser.parse_args()
    json_output = args.jsonDirectory
    amazon_paths = args.amazonDirectory
    rel_paths = os.listdir(amazon_paths)
    try:
        with open(os.path.join(json_output, 'design2019.json'), 'w', encoding='utf-8') as fp:
            for i in range(len(rel_paths)):
                sample = patent_json(i)
                json.dump(sample, fp, ensure_ascii=False)
                fp.write("\n")
            fp.close()
            print("Done!")
    except Exception as error:
        print(error)
    return f"Total segmented images: {len(rel_paths)}"

#results = output_json()
#print(results)
parser = get_args()
args = parser.parse_args()
json_output = args.jsonDirectory
amazon_paths = args.amazonDirectory
rel_paths = os.listdir(amazon_paths)
indices = list(range(len(rel_paths)))
if __name__ == "__main__":
    fp = open(os.path.join(json_output, 'design2019.json'), 'w', encoding='utf-8',)
    p = mp.cpu_count()
    process = Pool(p)
    sample = process.map(patent_json, indices)
    json.dump(sample, fp, ensure_ascii=False,)
    fp.write('\n')
    process.close()
    process.join()



#if __name__ == "__main__":
#    processes = []
#    num_cpu = mp.cpu_count()
#    for _ in range(num_cpu):
#        p = Process(target=output_json)
#        p.start()
#        processes.append(p)

#    for process in processes:
#        process.join()
#results = output_json()
#print(results)
finish = time.perf_counter()
print("Finished in {} seconds".format(finish-start))
