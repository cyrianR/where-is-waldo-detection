import os
import shutil
import cv2
import sys

##############################################
# VARIABLES TO SET

# if set to True, erase imagettes before creating new ones
# it should be set to False only when there is strictly new data in source folders
reset_imagettes = True

# imagettes size (in pixels)
largeur_imagettes = 300
hauteur_imagettes = 300

# source images and labels folder
images_folder = "./original-images"
labels_folder = "./original-labels_2"

# output folders
output_dir_images = "./imagettes"
output_dir_labels = "./imagettes-labels"
#################################################

# clean imagettes if reset_imagettes set to True
if reset_imagettes and os.path.exists(output_dir_images):
    shutil.rmtree(output_dir_images)
if reset_imagettes and os.path.exists(output_dir_labels):
    shutil.rmtree(output_dir_labels)

os.makedirs(output_dir_images, exist_ok=True)
os.makedirs(output_dir_labels, exist_ok=True)

list_images = sorted(os.listdir(images_folder))
list_labels = sorted(os.listdir(labels_folder))
nb_images = len(list_images)

for i in range(nb_images):
    image_path = os.path.join(images_folder, list_images[i])
    img = cv2.imread(image_path)
    height, width, _ = img.shape

    label_path = os.path.join(labels_folder, list_labels[i])
    label = open(label_path, "r")
    lines = label.readlines()
    label.close()

    for l in range(len(lines)):
        # Remove \n at the end of each line
        lines[l] = lines[l][0:-2]

    for l in range(len(lines)):
        line = lines[l].split(" ")
        x_c = round(float(line[1])*width)
        y_c = round(float(line[2])*height)
        width_box = round(float(line[3])*width)
        height_box = round(float(line[4])*height)

        if width_box > largeur_imagettes or height_box > hauteur_imagettes:
            print("Error: box size is bigger than imagette size")
            sys.exit(1)

        # Defining the area for the imagette
        if x_c - largeur_imagettes//2 < 0:
            x_top_left_corner = 0
            x_bottom_right_corner = largeur_imagettes
            ratio_centre_x = x_c/largeur_imagettes
        elif x_c + largeur_imagettes//2 > width:
            x_top_left_corner = width-largeur_imagettes
            x_bottom_right_corner = width
            ratio_centre_x = 1.0 - (width-x_c)/largeur_imagettes
        else:
            x_top_left_corner = x_c - largeur_imagettes//2
            x_bottom_right_corner = x_c + largeur_imagettes//2
            ratio_centre_x = 0.5

        if y_c - hauteur_imagettes//2 < 0:
            y_top_left_corner = 0
            y_bottom_right_corner = hauteur_imagettes
            ratio_centre_y = y_c/hauteur_imagettes
        elif y_c + largeur_imagettes//2 > height:
            y_top_left_corner = height-hauteur_imagettes
            y_bottom_right_corner = height
            ratio_centre_y = 1.0 - (height-y_c)/hauteur_imagettes
        else:
            y_top_left_corner = y_c - hauteur_imagettes//2
            y_bottom_right_corner = y_c + hauteur_imagettes//2
            ratio_centre_y = 0.5

        # Check for overlapping labels and change the imagette location if necessary
        
        list_exclude = []
        nb_seen = [0]*len(lines)
        stop = False
        while not stop:
            stop = True
            overlapping_labels = []
            for l2 in range(len(lines)):
                other_line = lines[l2]
                other_line = other_line.split(" ")
                other_x_c = round(float(other_line[1]) * width)
                other_y_c = round(float(other_line[2]) * height)
                other_width_box = round(float(other_line[3]) * width)
                other_height_box = round(float(other_line[4]) * height)

                # Check if the other label's box is fully inside the cropped region
                if (
                    other_x_c - other_width_box // 2 >= x_top_left_corner and
                    other_x_c + other_width_box // 2 <= x_bottom_right_corner and
                    other_y_c - other_height_box // 2 >= y_top_left_corner and
                    other_y_c + other_height_box // 2 <= y_bottom_right_corner
                ):
                    # Calculate the relative position and size of the overlapping box
                    relative_x_c = (other_x_c - x_top_left_corner) / \
                        largeur_imagettes
                    relative_y_c = (other_y_c - y_top_left_corner) / \
                        hauteur_imagettes
                    relative_width = other_width_box / largeur_imagettes
                    relative_height = other_height_box / hauteur_imagettes
                    overlapping_labels.append(
                        f"{other_line[0]} {relative_x_c} {relative_y_c} {relative_width} {relative_height}")
                    
                # Check if the other label's box is partially inside the cropped region
                elif (
                    other_x_c + other_width_box // 2 > x_top_left_corner and
                    other_x_c - other_width_box // 2 < x_bottom_right_corner and
                    other_y_c + other_height_box // 2 > y_top_left_corner and
                    other_y_c - other_height_box // 2 < y_bottom_right_corner
                ):
                    stop = False
                    nb_seen[l2] += 1

                    if nb_seen[l2] > 2 and l2 not in list_exclude:
                        # Infinite loop detected
                        # Try to exclude the label instead and hope for the best
                        list_exclude.append(l2)

                    if nb_seen[l2] > 5 and l2 in list_exclude:
                        print('Infinite loop detected and not resolved :( Try another imagette size ?')
                        sys.exit(1)

                    if l2 not in list_exclude:
                        # Update the imagette area to include the other label's box
                        if other_x_c - other_width_box // 2 < x_top_left_corner:
                            x_top_left_corner = other_x_c - other_width_box // 2
                            x_bottom_right_corner = x_top_left_corner + largeur_imagettes
                        elif other_x_c + other_width_box // 2 > x_bottom_right_corner:
                            x_bottom_right_corner = other_x_c + other_width_box // 2
                            x_top_left_corner = x_bottom_right_corner - largeur_imagettes
                        if other_y_c - other_height_box // 2 < y_top_left_corner:
                            y_top_left_corner = other_y_c - other_height_box // 2
                            y_bottom_right_corner = y_top_left_corner + hauteur_imagettes
                        elif other_y_c + other_height_box // 2 > y_bottom_right_corner:
                            y_bottom_right_corner = other_y_c + other_height_box // 2
                            y_top_left_corner = y_bottom_right_corner - hauteur_imagettes
                    else:
                        # Update the imagette area to exclude the other label's box
                        if other_x_c - other_width_box // 2 < x_top_left_corner:
                            x_top_left_corner = other_x_c + other_width_box // 2
                            x_bottom_right_corner = x_top_left_corner + largeur_imagettes
                        elif other_x_c + other_width_box // 2 > x_bottom_right_corner:
                            x_bottom_right_corner = other_x_c - other_width_box // 2
                            x_top_left_corner = x_bottom_right_corner - largeur_imagettes
                        if other_y_c - other_height_box // 2 < y_top_left_corner:
                            y_top_left_corner = other_y_c + other_height_box // 2
                            y_bottom_right_corner = y_top_left_corner + hauteur_imagettes
                        elif other_y_c + other_height_box // 2 > y_bottom_right_corner:
                            y_bottom_right_corner = other_y_c - other_height_box // 2
                            y_top_left_corner = y_bottom_right_corner - hauteur_imagettes
                    
        # save imagette
        imagette = img[y_top_left_corner:y_bottom_right_corner,
                       x_top_left_corner:x_bottom_right_corner, :]
        imagette_path = os.path.join(
            output_dir_images, list_images[i][0:-4]+"-"+str(l)+".jpg")
        cv2.imwrite(imagette_path, imagette)

        imagette_label_path = os.path.join(
            output_dir_labels, list_images[i][0:-4]+"-"+str(l)+".txt")
        with open(imagette_label_path, "w") as file:
            file.write("\n".join(overlapping_labels))