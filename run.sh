source activate ./env
python ./yolov5/detect.py --weights ./yolov5/best.pt --img 416 --conf 0.82 --source truck.jpg --save-crop