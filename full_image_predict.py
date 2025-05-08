import cv2
import os
import shutil


def full_image_predict(model,image_path,box_size):
    cut_dir = "./image_cut"
    shutil.rmtree(cut_dir)
    os.makedirs(cut_dir)
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


    predictions = model.predict(source=cut_dir, save=True)
    all_boxes = []
    for imagette in predictions:
        boxes = imagette.boxes
        nom_image = imagette.path[0:-4].split("/")[-1]
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

            if len(ind_overlapping_boxes) == 0 and confidence > 0.8:
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
    
    with open("test_labels.txt","w") as file:
            file.write("\n".join(labels))

        





    
    

        