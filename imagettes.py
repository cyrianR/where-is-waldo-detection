import os
import shutil
import cv2

##############################################
## VARIABLES TO SET

# if set to True, erase imagettes before creating new ones
# it should be set to False only when there is strictly new data in source folders
reset_imagettes = True

# imagettes size (in pixels)
largeur_imagettes = 300
hauteur_imagettes = 300

# source images folder
image_folder = "./original-images"
# source labels folder (yolo .txt format) from labelstudio
label_folder = "./original-labels"

# output folders
output_dir_images = "./imagettes-OCV"
output_dir_labels = "./imagettes-labels-OCV"
#################################################

# clean imagettes if reset_imagettes set to True
if reset_imagettes and os.path.exists(output_dir_images):
    shutil.rmtree(output_dir_images)
if reset_imagettes and os.path.exists(output_dir_labels):
    shutil.rmtree(output_dir_labels)

os.makedirs(output_dir_images, exist_ok=True)
os.makedirs(output_dir_labels, exist_ok=True)

list_images = os.listdir(image_folder)
list_labels = os.listdir(label_folder)
nb_images = len(list_images)

for i in range(nb_images):
    image_path = os.path.join(image_folder, list_images[i])
    img = cv2.imread(image_path)
    height, width, _ = img.shape

    label_path = os.path.join(label_folder, list_labels[i])
    label = open(label_path, "r")
    lines = label.readlines()
    label.close()

    for l in range(len(lines)) :
        lines[l] = lines[l][0:-2]
        line = lines[l].split(" ")
        x_c = round(float(line[1])*width)
        y_c = round(float(line[2])*height)
        width_box = round(float(line[3])*width)
        height_box = round(float(line[4])*height)

        if x_c - largeur_imagettes//2 < 0:
            x_top_left_corner = 0
            x_bottom_right_corner =  largeur_imagettes
            ratio_centre_x = x_c/largeur_imagettes
        elif x_c + largeur_imagettes//2 > width:
            x_top_left_corner = width-largeur_imagettes
            x_bottom_right_corner =  width
            ratio_centre_x = 1.0 - (width-x_c)/largeur_imagettes
        else:
            x_top_left_corner = x_c - largeur_imagettes//2
            x_bottom_right_corner = x_c + largeur_imagettes//2
            ratio_centre_x = 0.5

        if y_c - hauteur_imagettes//2 < 0:
            y_top_left_corner = 0
            y_bottom_right_corner =  hauteur_imagettes
            ratio_centre_y = y_c/hauteur_imagettes
        elif y_c + largeur_imagettes//2 > height:
            y_top_left_corner = height-hauteur_imagettes
            y_bottom_right_corner =  height
            ratio_centre_y = 1.0 - (height-y_c)/hauteur_imagettes
        else:
            y_top_left_corner = y_c - hauteur_imagettes//2
            y_bottom_right_corner = y_c + hauteur_imagettes//2
            ratio_centre_y = 0.5

        imagette = img[y_top_left_corner:y_bottom_right_corner, x_top_left_corner:x_bottom_right_corner, :]
        imagette_path = os.path.join(output_dir_images, list_images[i][0:-4]+"-"+str(l)+".jpg")
        cv2.imwrite(imagette_path, imagette)

        label_string = line[0] + " " + str(ratio_centre_x) + " " + str(ratio_centre_y) + " " + str(width_box/largeur_imagettes) + " " + str(height_box/hauteur_imagettes)
        imagette_label_path = os.path.join(output_dir_labels, list_images[i][0:-4]+"-"+str(l)+".txt")
        file = open(imagette_label_path, "w")
        file.write(label_string)
        file.close()

