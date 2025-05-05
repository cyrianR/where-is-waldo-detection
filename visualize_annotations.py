import os
import sys
import yaml
import subprocess
import shutil

# UTILISATION :
# python visualize_annotations.py <images_folder> <labels_folder> <output_folder>
# Met dans le dossier output_folder les images annotées avec les boîtes englobantes dessinées.

def create_classes_file(data_yaml_path, classes_file_path):
    with open(data_yaml_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    with open(classes_file_path, 'w') as classes_file:
        for class_name in data.get('names', []):
            classes_file.write(f"{class_name}\n")

def main():
    if len(sys.argv) != 4:
        print("Usage: python visualize_annotations.py <images_folder> <labels_folder> <output_folder>")
        sys.exit(1)

    images_folder = sys.argv[1]
    labels_folder = sys.argv[2]
    output_folder = sys.argv[3]

    data_yaml_path = "data.yaml"
    classes_file_path = "classes.names"
    input_folder = "input"

    if not os.path.exists(data_yaml_path):
        print(f"Error: {data_yaml_path} not found.")
        sys.exit(1)

    # Step 1: Create input folder and copy files
    os.makedirs(input_folder, exist_ok=True)
    for file_name in os.listdir(images_folder):
        shutil.copy(os.path.join(images_folder, file_name), input_folder)
    for file_name in os.listdir(labels_folder):
        shutil.copy(os.path.join(labels_folder, file_name), input_folder)

    # Step 2: Create classes.names file
    create_classes_file(data_yaml_path, classes_file_path)

    # Step 3: Call vis_bbox.py
    vis_bbox_command = [
        "python", "vis_bbox.py",
        "--folder_path", input_folder,
        "--classes", classes_file_path,
        "--save_path", output_folder
    ]
    subprocess.run(vis_bbox_command)

    # Step 4: Remove classes.names file
    if os.path.exists(classes_file_path):
        os.remove(classes_file_path)

    # Step 5: Delete input folder
    if os.path.exists(input_folder):
        shutil.rmtree(input_folder)

if __name__ == "__main__":
    main()