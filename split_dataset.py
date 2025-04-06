
import os
import shutil
import random
from collections import defaultdict
import sys

##############################################
## VARIABLES TO SET

# if set to True, erase datasets before creating new ones
# it should be set to False only when there is strictly new data in source folders
reset_dataset = True

# splitting datasets percentages (sum has to be 100)
train_perc = 80
valid_perc = 10
test_perc = 10

# source images folder
image_folder = "./original-images"
# source labels folder (yolo .txt format) from labelstudio
label_folder = "./original-labels"

# output folders
output_dir_dataset = "./dataset"
#################################################

# clean datasets if reset_dataset set to True
if reset_dataset and os.path.exists(output_dir_dataset):
    shutil.rmtree(output_dir_dataset)

os.makedirs(output_dir_dataset, exist_ok=True)

# resulting separable images names
full_images = []
double_images = {}
uncomplete_images = []

# transform all JPEG images with .jpg extension
for file_name in os.listdir(image_folder):
    if file_name.lower().endswith(".jpeg") or file_name.endswith(".JPG"):
        base_name, _ = os.path.splitext(file_name)
        new_file_name = base_name + ".jpg"
        os.rename(os.path.join(image_folder, file_name), os.path.join(image_folder, new_file_name))

# iterate over all jpeg files in the image_folder directory
jpeg_files = {os.path.splitext(f) for f in os.listdir(image_folder) if f.lower().endswith((".jpg"))}
for jpeg_name, jpeg_ext in jpeg_files:
    parts = jpeg_name.split("-")
    if len(parts) == 3:
        book_num, picture_num, page_num = parts
        if book_num == "7" and page_num != "0":
            uncomplete_images.append(jpeg_name)
        else:
            if page_num == "0":
                full_images.append(jpeg_name)
            else:
                key = book_num + picture_num
                if key not in double_images:
                    double_images[key] = []
                double_images[key].append(jpeg_name)
    else:
        print(f"Unexpected format for file: {jpeg_name}")

# splitting data in training, validation and test datasets
train_images_dir = output_dir_dataset + "/train/images"
train_labels_dir = output_dir_dataset + "/train/labels"
valid_images_dir = output_dir_dataset + "/valid/images"
valid_labels_dir = output_dir_dataset + "/valid/labels"
test_images_dir = output_dir_dataset + "/test/images"
test_labels_dir = output_dir_dataset + "/test/labels"

os.makedirs(train_images_dir, exist_ok=True)
os.makedirs(train_labels_dir, exist_ok=True)
os.makedirs(valid_images_dir, exist_ok=True)
os.makedirs(valid_labels_dir, exist_ok=True)
os.makedirs(test_images_dir, exist_ok=True)
os.makedirs(test_labels_dir, exist_ok=True)

# add uncomplete images to the training set
for f in uncomplete_images:
    shutil.copyfile(image_folder + "/" + f + ".jpg", train_images_dir + "/" + f + ".jpg")
    shutil.copyfile(label_folder + "/" + f + ".txt", train_labels_dir + "/" + f + ".txt")

# add full and double images to the datasets according to the percentages
# compute number of images in each dataset
n_images_full = len(full_images)
n_images_double = len(double_images)
n_train_full = int(n_images_full * train_perc / 100)
n_valid_full = int(n_images_full * valid_perc / 100)
n_test_full = n_images_full - n_train_full - n_valid_full
n_train_double = int(n_images_double * train_perc / 100)
n_valid_double = int(n_images_double * valid_perc / 100)
n_test_double = n_images_double - n_train_double - n_valid_double
# shuffle images
random.shuffle(full_images)
keys_double = list(double_images.keys())
random.shuffle(keys_double)
# add images to the datasets
for i in range(n_train_full):
    f = full_images[i]
    shutil.copyfile(image_folder + "/" + f + ".jpg", train_images_dir + "/" + f + ".jpg")
    shutil.copyfile(label_folder + "/" + f + ".txt", train_labels_dir + "/" + f + ".txt")
for i in range(n_train_full, n_train_full + n_valid_full):
    f = full_images[i]
    shutil.copyfile(image_folder + "/" + f + ".jpg", valid_images_dir + "/" + f + ".jpg")
    shutil.copyfile(label_folder + "/" + f + ".txt", valid_labels_dir + "/" + f + ".txt")
for i in range(n_train_full + n_valid_full, n_images_full):
    f = full_images[i]
    shutil.copyfile(image_folder + "/" + f + ".jpg", test_images_dir + "/" + f + ".jpg")
    shutil.copyfile(label_folder + "/" + f + ".txt", test_labels_dir + "/" + f + ".txt")
for i in range(n_train_double):
    key = keys_double[i]
    for f in double_images[key]:
        shutil.copyfile(image_folder + "/" + f + ".jpg", train_images_dir + "/" + f + ".jpg")
        shutil.copyfile(label_folder + "/" + f + ".txt", train_labels_dir + "/" + f + ".txt")
for i in range(n_train_double, n_train_double + n_valid_double):
    key = keys_double[i]
    for f in double_images[key]:
        shutil.copyfile(image_folder + "/" + f + ".jpg", valid_images_dir + "/" + f + ".jpg")
        shutil.copyfile(label_folder + "/" + f + ".txt", valid_labels_dir + "/" + f + ".txt")
for i in range(n_train_double + n_valid_double, n_images_double):
    key = keys_double[i]
    for f in double_images[key]:
        shutil.copyfile(image_folder + "/" + f + ".jpg", test_images_dir + "/" + f + ".jpg")
        shutil.copyfile(label_folder + "/" + f + ".txt", test_labels_dir + "/" + f + ".txt")

# number of files in the directories
num_train_images = len([f for f in os.listdir(train_images_dir) if os.path.isfile(os.path.join(train_images_dir, f))])
num_valid_images = len([f for f in os.listdir(valid_images_dir) if os.path.isfile(os.path.join(valid_images_dir, f))])
num_test_images = len([f for f in os.listdir(test_images_dir) if os.path.isfile(os.path.join(test_images_dir, f))])

# print resulting splitting statistics
print("")
print("--------------------- RESULTS ---------------------")
print("Total number of different Waldo pictures in each dataset :")
print("Pictures in training dataset : " + str(n_train_full + n_train_double + len(uncomplete_images)))
print("Pictures in validation dataset : " + str(n_valid_full + n_valid_double))
print("Pictures in test dataset : " + str(n_test_full + n_test_double))
print("")
print("Total number of images in each dataset :")
print("Images in training dataset : " + str(num_train_images))
print("Images in validation dataset : " + str(num_valid_images))
print("Images in test dataset : " + str(num_test_images))
print("")
print("Total number of images in all dataset :" + str(num_train_images + num_valid_images + num_test_images))
print("---------------------------------------------------")
print("")