
import os
import shutil
import random
from collections import defaultdict
import sys

##############################################
## VARIABLES TO SET

# if set to True, erase datasets before creating new ones
# it should be True when remove_after_copy is set to False, to prevent datasets from containing duplicate labelised boxes
# it should be set to False only when there is strictly new data in source folders
reset_dataset = True

# splitting datasets percentages (sum has to be 100)
train_perc = 80
valid_perc = 10
test_perc = 10

# first id for naming files
id_start = 0

# if set to True, removes all source images and labels files from image_folder and label_folder
remove_after_copy = False

# source images folder
image_folder = "./original-images"
# source labels folder (yolo .txt format) from labelstudio
label_folder = "./original-labels"

# output folders
output_dir_txt = "./all_labels"
output_dir_jpeg = "./all_images"
output_dir_dataset = "./dataset"
#################################################


# check errors
if (train_perc + valid_perc + test_perc != 100):
    print("ERROR : percentages don't sum up to 100")
    sys.exit()

# clean datasets if reset_dataset set to True
if reset_dataset and os.path.exists(output_dir_dataset):
    shutil.rmtree(output_dir_dataset)

os.makedirs(output_dir_txt, exist_ok=True)
os.makedirs(output_dir_jpeg, exist_ok=True)
os.makedirs(output_dir_dataset, exist_ok=True)

# cleaning original images and labels by renaming all files with unique id
jpeg_names = {os.path.splitext(f) for f in os.listdir(image_folder) if f.endswith((".jpg", ".jpeg", ".JPG"))}
txt_names = {os.path.splitext(f)[0] for f in os.listdir(label_folder) if f.endswith(".txt")}
for jpeg_name, jpeg_ext in jpeg_names:
    not_found = True
    for txt_name in txt_names:
        if jpeg_name in txt_name.split("-", 1)[1]:
            not_found = False
            matching_txt_name = txt_name
    if not_found:
        print("ERREUR : fichier de labelisation .txt non trouvé pour le fichier jpeg '" +  jpeg_name + jpeg_ext + "'")
    else:
        shutil.copyfile(label_folder + "/" + matching_txt_name + ".txt", output_dir_txt + "/" + "id" + str(id_start) + ".txt")
        shutil.copyfile(image_folder + "/" + jpeg_name + jpeg_ext, output_dir_jpeg + "/" + "id" + str(id_start) + ".jpg")
        if remove_after_copy:
            os.remove(label_folder + "/" + matching_txt_name + ".txt")
            os.remove(image_folder + "/" + jpeg_name + ".jpg")
        id_start += 1


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

# get lines in label files and split them randomly according to the datasets percentages 
train_dict = defaultdict(list)
valid_dict = defaultdict(list)
test_dict = defaultdict(list)
for file_fullname in os.listdir(output_dir_txt):
    file_path = os.path.join(output_dir_txt, file_fullname)
    if os.path.isfile(file_path):
        with open(file_path, "r") as file:
            file_name, file_ext = os.path.splitext(file_fullname)
            for line in file:
                r = random.randint(1,100)
                if (r <= train_perc):
                    train_dict[file_name].append(line)
                elif (train_perc < r <= train_perc + valid_perc):
                    valid_dict[file_name].append(line)
                else:
                    test_dict[file_name].append(line)

# write label files and copy images in corresponding datasets acccording to previously computed splitting, and compute some statistics
train_count = [0,0,0,0]
valid_count = [0,0,0,0]
test_count = [0,0,0,0]

for file_name in train_dict:
    file_path_label = os.path.join(train_labels_dir, file_name + ".txt")
    file_path_image = os.path.join(train_images_dir, file_name + ".jpg")
    with open(file_path_label, 'w') as file:
        for line in train_dict[file_name]:
            print(line, file=file)
            label = int(line.split(' ')[0])
            train_count[label] += 1
    shutil.copyfile(output_dir_jpeg + "/" + file_name + ".jpg", file_path_image)

for file_name in valid_dict:
    file_path_label = os.path.join(valid_labels_dir, file_name + ".txt")
    file_path_image = os.path.join(valid_images_dir, file_name + ".jpg")
    with open(file_path_label, 'w') as file:
        for line in valid_dict[file_name]:
            print(line, file=file)
            label = int(line.split(' ')[0])
            valid_count[label] += 1
    shutil.copyfile(output_dir_jpeg + "/" + file_name + ".jpg", file_path_image)

for file_name in test_dict:
    file_path_label = os.path.join(test_labels_dir, file_name + ".txt")
    file_path_image = os.path.join(test_images_dir, file_name + ".jpg")
    with open(file_path_label, 'w') as file:
        for line in test_dict[file_name]:
            print(line, file=file)
            label = int(line.split(' ')[0])
            test_count[label] += 1
    shutil.copyfile(output_dir_jpeg + "/" + file_name + ".jpg", file_path_image)

# print resulting splitting statistics
print("")
print("Resulting statistics (total of labels by dataset):")
print("-----------------------------------------------------------")
i = 0
res = "TRAIN : "
for label_count in train_count:
    res += str(i) + ":" + str(label_count) + " "
    i += 1
print(res)

i = 0
res = "VALIDATION : "
for label_count in valid_count:
    res += str(i) + ":" + str(label_count) + " "
    i += 1
print(res)

i = 0
res = "TEST : "
for label_count in test_count:
    res += str(i) + ":" + str(label_count) + " "
    i += 1
print(res)
