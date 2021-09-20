FROM python:3.8
WORKDIR /patent/
COPY requirements.txt /patent/
RUN pip install -r ./requirements.txt
COPY trained-results/390/390/MedT.pth /patent/
COPY Amazon_label.py segmentation_pipeline.py test_segment.py /patent/
COPY mask.py utils.py test_ex.py resize_segment.py image_to_json.py /patent/
COPY README.md /patent/
