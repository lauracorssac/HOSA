#!/bin/bash

if [ $# -eq 0 ]; then
  DATA_DIR=$(pwd)
else
  DATA_DIR="$1"
fi

# Install required packages
sudo apt-get install -y python3;
sudo apt-get install -y python3-pip;
sudo pip3 install -r requirements.txt

sudo apt-get update;
sudo apt install libtiff5
sudo apt-get install libopenjp2-7
sudo apt-get install libatlas-base-dev

sudo pip3 install https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.1.0/tensorflow-2.1.0-cp37-none-linux_armv6l.whl --no-cache-dir

# Get TF Lite model and labels
curl -O http://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip -d ${DATA_DIR}
rm coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip

# Get a labels file with corrected indices, delete the other one
(cd ${DATA_DIR} && curl -O  https://dl.google.com/coral/canned_models/coco_labels.txt)
rm ${DATA_DIR}/labelmap.txt

# Get version compiled for Edge TPU
(cd ${DATA_DIR} && curl -O  https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite)

echo -e "Files downloaded to ${DATA_DIR}"
