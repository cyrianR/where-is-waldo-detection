import cv2
import os
import shutil
import sys
from ultralytics import YOLO
from visualize_annotations import visualize_annotations


def full_image_predict(model, image_path, box_size, confidence_threshold=0.5):
    cut_dir = "./image_cut"
    if os.path.exists(cut_dir):
        shutil.rmtree(cut_dir)
    os.makedirs(cut_dir, exist_ok=True)
    img = cv2.imread(image_path)
    height, width, _ = img.shape

    y = 0
    reach_end_y = False
    while not(reach_end_y) :
        if y >= height-box_size :
            y = height-box_size
            reach_end_y = True
        x = 0
        reach_end_x = False
        while not(reach_end_x) :
            if x >= width-box_size :
                x = width - box_size
                reach_end_x = True
            imagette = img[y:y+box_size, x:x+box_size, :]
            cv2.imwrite(cut_dir+"/"+str(y)+"-"+str(x)+".jpg", imagette)
            x = int(x + box_size/2)
        y = int(y + box_size/2)


    predictions = model.predict(source=cut_dir, save=False, imgsz= 320, conf=confidence_threshold, verbose=False)
    all_boxes = []
    for imagette in predictions:
        boxes = imagette.boxes
        nom_image = os.path.basename(imagette.path)
        nom_image, _ = os.path.splitext(nom_image)
        y_offset = int(nom_image.split("-")[0])
        x_offset = int(nom_image.split("-")[1])
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = box.conf[0].item()
            class_id = int(box.cls[0].item())


            # find the overlapping boxes
            ind_overlapping_boxes = []

            for i in range(len(all_boxes)):
                coordinates,_,_ = all_boxes[i]
                x1_box_i, y1_box_i, x2_box_i, y2_box_i = coordinates

                # intersection coordinates
                x_left   = max(x1+x_offset, x1_box_i)
                y_top    = max(y1+y_offset, y1_box_i)
                x_right  = min(x2+x_offset, x2_box_i)
                y_bottom = min(y2+y_offset, y2_box_i)

                # overlapping ?
                if x_right >= x_left and y_bottom >= y_top:
                    ind_overlapping_boxes.append(i)

            if len(ind_overlapping_boxes) == 0:
                all_boxes.append(((x1+x_offset,y1+y_offset,x2+x_offset,y2+y_offset),confidence,class_id))

            for j in range(len(ind_overlapping_boxes)):
                _,confidence_box_i,_ = all_boxes[ind_overlapping_boxes[j]]
                if confidence > confidence_box_i:
                    all_boxes[ind_overlapping_boxes[j]] = ((x1+x_offset,y1+y_offset,x2+x_offset,y2+y_offset),confidence,class_id)
      

    labels = []
    for i in range(len(all_boxes)):
        coordinates,_,class_id = all_boxes[i]
        x1, y1, x2, y2 = coordinates
        labels.append(f"{class_id} {(x1+x2)/(2*width)} {(y1+y2)/(2*height)} {(x2-x1)/width} {(y2-y1)/height}")

    if os.path.exists(cut_dir):
        shutil.rmtree(cut_dir)

    output_folder="full_image_output"
    labels_folder="full_image_labels"
    image_folder="full_image"

    if os.path.exists(image_folder):
        shutil.rmtree(image_folder)
    os.makedirs(image_folder, exist_ok=True)
    cv2.imwrite(os.path.join(image_folder,os.path.basename(image_path)), img)

    if os.path.exists(labels_folder):
        shutil.rmtree(labels_folder)
    os.makedirs(labels_folder, exist_ok=True)

    labels_full_path = os.path.join(labels_folder,"test_labels.txt")
    with open(labels_full_path,"w") as file:
        file.write("\n".join(labels))

    # Make the visualization
    visualize_annotations(image_folder, labels_folder, output_folder, False)

    shutil.rmtree(labels_folder)
    shutil.rmtree(image_folder)

def main():
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Usage: python full_image_predict.py <model_path> <image_folder> <box_size> [<confidence_threshold>]")
        sys.exit(1)

    model_path = sys.argv[1]
    image_folder = sys.argv[2]
    box_size = int(sys.argv[3])
    confidence_threshold = float(sys.argv[4]) if len(sys.argv) == 5 else 0.5

    # Load the model
    model = YOLO(model_path)

    # Predict on the full image
    for file_name in os.listdir(image_folder):
        print(f"Predicting on {file_name}")
        full_image_predict(model, os.path.join(image_folder, file_name), box_size, confidence_threshold)

    print("""Prediction completed. Check the "full_image_output" folder for results.""")

if __name__ == "__main__":
    main()