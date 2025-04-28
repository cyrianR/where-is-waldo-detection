import os
import PIL.Image
import numpy as np

list_images = os.listdir('original-images')
list_labels = os.listdir('original-labels')
nb_images = len(list_images)

largeur_imagettes = 300
hauteur_imagettes = 300

for i in range(nb_images):
    img = PIL.Image.open('original-images/'+list_images[i])
    width, height = img.size
    img = np.array(img)

    label = open('original-labels/'+list_labels[i])
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
        imagette_jpg = PIL.Image.fromarray(imagette)
        imagette_jpg.save("imagettes/"+list_images[i][0:-4]+"-"+str(l)+".jpg")

        label_string = line[0] + " " + str(ratio_centre_x) + " " + str(ratio_centre_y) + " " + str(width_box/largeur_imagettes) + " " + str(height_box/hauteur_imagettes)
        file = open("imagettes-labels/"+list_images[i][0:-4]+"-"+str(l)+".txt", "w")
        file.write(label_string)
        file.close()

