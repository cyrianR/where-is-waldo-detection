import cv2
import os
import yaml

### USAGE
# python add_annotations.py
# This script allows you to annotate images with bounding boxes and save the annotations in YOLO format.
# You can switch between classes using the number keys (0-9) and save the annotations by pressing 's'.
# To exit the tool, press 'q'.

# Charger les classes depuis data.yaml
def load_classes(data_yaml_path):
    with open(data_yaml_path, 'r') as file:
        data = yaml.safe_load(file)
    return data['names']

# Charger les annotations existantes depuis un fichier
def load_annotations(label_file):
    annotations = []
    if os.path.exists(label_file):
        with open(label_file, 'r') as file:
            for line in file:
                parts = line.strip().split()
                class_id = int(parts[0])
                x_center, y_center, bbox_width, bbox_height = map(float, parts[1:])
                annotations.append((class_id, x_center, y_center, bbox_width, bbox_height))
    return annotations

# Sauvegarder les annotations dans un fichier
def save_annotations(label_file, annotations):
    with open(label_file, 'w') as file:
        for annotation in annotations:
            file.write(f"{annotation[0]} {annotation[1]} {annotation[2]} {annotation[3]} {annotation[4]}\n")

# Variables globales
drawing = False
start_point = (0, 0)
end_point = (0, 0)
new_annotations = []
current_class = 0

# Fonction de callback pour dessiner les boîtes
def draw_rectangle(event, x, y, flags, param):
    global drawing, start_point, end_point, new_annotations, current_class

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        x_min = min(start_point[0], end_point[0])
        y_min = min(start_point[1], end_point[1])
        x_max = max(start_point[0], end_point[0])
        y_max = max(start_point[1], end_point[1])

        # Ajouter l'annotation (normalisée)
        bbox_width = (x_max - x_min) / image_width
        bbox_height = (y_max - y_min) / image_height
        x_center = (x_min + x_max) / 2 / image_width
        y_center = (y_min + y_max) / 2 / image_height
        new_annotations.append((current_class, x_center, y_center, bbox_width, bbox_height))
        print(f"Annotation ajoutée : Classe {current_class}, x_center={x_center}, y_center={y_center}, width={bbox_width}, height={bbox_height}")

# Ajuster la taille de l'image pour qu'elle rentre dans l'écran
def resize_to_fit_screen(image, max_width=1280, max_height=720):
    height, width = image.shape[:2]
    if width > max_width or height > max_height:
        scaling_factor = min(max_width / width, max_height / height)
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)
        return cv2.resize(image, (new_width, new_height)), scaling_factor
    return image, 1.0

# Chemins des dossiers et fichiers
images_folder = "c:\\Users\\timot\\Downloads\\Charlie-DB\\original-images"
labels_folder = "c:\\Users\\timot\\Downloads\\Charlie-DB\\original-labels"
data_yaml_path = "c:\\Users\\timot\\Downloads\\Charlie-DB\\data.yaml"

# Charger les classes
classes = load_classes(data_yaml_path)

# Créer le dossier des labels s'il n'existe pas
os.makedirs(labels_folder, exist_ok=True)

# Parcourir les images
for image_file in os.listdir(images_folder):
    if image_file.endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(images_folder, image_file)
        label_file = os.path.join(labels_folder, os.path.splitext(image_file)[0] + '.txt')

        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Erreur lors du chargement de l'image : {image_path}")
            continue

        # Charger les annotations existantes
        existing_annotations = load_annotations(label_file)

        # Ajuster la taille de l'image pour qu'elle rentre dans l'écran
        image, scaling_factor = resize_to_fit_screen(image)
        image_height, image_width = image.shape[:2]

        # Réinitialiser les nouvelles annotations
        new_annotations = []

        # Afficher l'image et configurer la fenêtre
        cv2.namedWindow("Annotation Tool")
        cv2.setMouseCallback("Annotation Tool", draw_rectangle)

        while True:
            temp_image = image.copy()

            # Dessiner la boîte en cours
            if drawing:
                cv2.rectangle(temp_image, start_point, end_point, (255, 0, 0), 2)

            # Dessiner les nouvelles annotations
            for annotation in new_annotations:
                x_center, y_center, bbox_width, bbox_height = annotation[1:]
                x_min = int((x_center - bbox_width / 2) * image_width)
                y_min = int((y_center - bbox_height / 2) * image_height)
                x_max = int((x_center + bbox_width / 2) * image_width)
                y_max = int((y_center + bbox_height / 2) * image_height)
                cv2.rectangle(temp_image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(temp_image, classes[annotation[0]], (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Annotation Tool", temp_image)
            key = cv2.waitKey(1) & 0xFF

            # Changer de classe avec les touches numériques
            if ord('0') <= key <= ord(str(len(classes) - 1)):
                current_class = key - ord('0')
                print(f"Classe actuelle : {classes[current_class]}")

            # Sauvegarder et passer à l'image suivante (touche 's')
            elif key == ord('s'):
                # Combiner les annotations existantes et nouvelles
                all_annotations = existing_annotations + new_annotations
                save_annotations(label_file, all_annotations)
                print(f"Annotations sauvegardées dans {label_file}")
                break

            # Quitter l'outil (touche 'q')
            elif key == ord('q'):
                # Sauvegarder avant de quitter
                all_annotations = existing_annotations + new_annotations
                save_annotations(label_file, all_annotations)
                print(f"Annotations sauvegardées dans {label_file}")
                print("Quitter l'outil.")
                exit()

        cv2.destroyAllWindows()