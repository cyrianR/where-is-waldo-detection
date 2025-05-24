import os
import sys
import yaml
import shutil
import cv2

# UTILISATION :
# python visualize_annotations.py <images_folder> <labels_folder> <output_folder>
# Met dans le dossier output_folder les images annotées avec les boîtes englobantes dessinées.

def create_classes_file(data_yaml_path, classes_file_path):
    with open(data_yaml_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    with open(classes_file_path, 'w') as classes_file:
        for class_name in data.get('names', []):
            classes_file.write(f"{class_name}\n")

def visualize_bounding_boxes(folder_path, classes_file_path, save_path):
    with open(classes_file_path) as class_names_file:
        classes = [line.strip() for line in class_names_file.readlines()]

    class_names = {idx: name for idx, name in enumerate(classes)}

    # Associer une couleur unique à chaque classe
    colors = {
        0: (57, 255, 20),   # Vert 
        1: (0, 0, 255),     # Rouge 
        2: (0, 140, 255),   # Orange 
        3: (255, 0, 255)    # Rose 
    }
    os.makedirs(save_path, exist_ok=True)

    all_files = os.listdir(folder_path)
    annotations, images = [], []

    for file in all_files:
        if file.endswith('.txt'):
            annotations.append(file)
        elif file.endswith(('.jpg', '.jpeg', '.png')):
            images.append(file)

    if len(images) > len(annotations):
        raise ValueError("Certaines images n'ont pas d'annotations.")
    elif len(images) < len(annotations):
        raise ValueError("Il y a plus d'annotations que d'images.")

    images.sort()
    annotations.sort()

    for image, annotation in zip(images, annotations):
        img = cv2.imread(os.path.join(folder_path, image))
        height, width, _ = img.shape
        with open(os.path.join(folder_path, annotation)) as f:
            content = [line.strip() for line in f.readlines()]
        for annot in content:
            annot = annot.split()
            class_idx = int(annot[0])
            x, y, w, h = map(float, annot[1:])
            xmin = int((x * width) - (w * width) / 2.0)
            ymin = int((y * height) - (h * height) / 2.0)
            xmax = int((x * width) + (w * width) / 2.0)
            ymax = int((y * height) + (h * height) / 2.0)
            color = colors[class_idx]
            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, 2)
            cv2.putText(img, class_names[class_idx], (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 4,cv2.LINE_AA)
        cv2.imwrite(os.path.join(save_path, image), img)

def visualize_annotations(images_folder, labels_folder, output_folder, data_yaml_path="data.yaml"):
    input_folder = "input"
    classes_file_path = "classes.names"

    if not os.path.exists(data_yaml_path):
        raise FileNotFoundError(f"{data_yaml_path} not found.")
    
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

    os.makedirs(output_folder, exist_ok=True)

    # create input folder and copy files
    os.makedirs(input_folder, exist_ok=True)
    for file_name in os.listdir(images_folder):
        shutil.copy(os.path.join(images_folder, file_name), input_folder)
    for file_name in os.listdir(labels_folder):
        shutil.copy(os.path.join(labels_folder, file_name), input_folder)

    # classes.names file
    create_classes_file(data_yaml_path, classes_file_path)

    # call visualize_bounding_boxes
    visualize_bounding_boxes(input_folder, classes_file_path, output_folder)

    # clean what was created
    if os.path.exists(classes_file_path):
        os.remove(classes_file_path)

    if os.path.exists(input_folder):
        shutil.rmtree(input_folder)

def main():
    if len(sys.argv) != 4:
        print("Usage: python visualize_annotations.py <images_folder> <labels_folder> <output_folder>")
        sys.exit(1)

    images_folder = sys.argv[1]
    labels_folder = sys.argv[2]
    output_folder = sys.argv[3]

    try:
        visualize_annotations(images_folder, labels_folder, output_folder)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()