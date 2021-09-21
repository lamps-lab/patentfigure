# PatentFigureSegmentation
This project involves segmenting figures and labels in patent figures using Transformer method. 
The following steps were carried out in order to perform the segmentation:

- We used Amazon Rekognition tool to obtain bounding box coordinates for the figure labels

- We used the coordinates obtained in step 1 to wipe off the figure labels

- Then, we used Transformer method to segment the patent drawings and their corresponding labels.

# Running the Pipeline
1.  Clone this repository and create a python virtual environment and activate it.
2. run: pip install -r requirements.txt
3. To wipe out the labels and process the images for the transformer, create a directory and inside the directory, create anotrher directory and name it **img**.
4. From the root directory, run the command below:
      - python3 processing.py <image_path> --amazonDirectory <amazon_filepath> --processingDirectory </img_path/created/in/step1>

5. Next step is to run the transformer on the processed images. run the command below:
    - python3 test_ex.py --loaddirec "MedT.pth" --val_dataset "processed/images/directory" --direc 'path for results to be saved' --batch_size 1 --modelname "MedT" --imgsize 128 --gray "no"

6. Finally, to segment the images, run the command below:
    - python3 output.py <image_path> --amazonDirectory <amazon_filepath> --TransformerDirectory <path/where/you/saved/transformer/result> --jsonDirectory <path/to/save/json/file> --outputDirectory <path/to/save/segmented/images>

## Example
- We have included few images and their corresponding amazon bounding box information in the **test** folder to test the pipeline.  

# Docker Build
- A Dockerfile is provided with the Python 3.8 library. This will create a working directory called **patent** with all the 
project dependencies installed.

- Build container: docker build -t <name-of-image> . e.g. kehindeajayi01/patentfigure:patent, the dot after your docker image implies your current directory.

- Run the container interactively, mount this project dir to /patent/: docker run -it --name <patent> patentfigure:patent

