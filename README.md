# PatentFigureSegmentation
This project involves segmenting figures and labels in patent figures using Transformer method. 
The following steps were carried out in order to perform the segmentation:

- We used Amazon Rekognition tool to obtain bounding box coordinates for the figure labels

- We used the coordinates obtained in step 1 to wipe off the figure labels

- Then, we used Transformer method to segment the patent drawings and their corresponding labels.

# Docker Build
- A Dockerfile is provided with the Python 3.8 library. This will create a working directory called **patent** with all the 
project dependencies installed.

- Build container: docker build -t <name-of-image> . e.g. kehindeajayi01/patentfigure:patent, the dot after your docker image implies your current directory.

- Run the container interactively, mount this project dir to /patent/: docker run -it --name <patent> patentfigure:patent

