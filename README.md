# Charlie-DB

This project implements a YOLO-based detection model for "Where's Waldo?" books. It provides three datasets with different annotations and/or image sizes, the original images and labels used to create those datasets and some utility scripts.

You can also find a full report of our work in french in the file [Projet_Charlie.pdf](Projet_Charlie.pdf).

## Project Structure

```
Charlie-DB/
│
├── dataset/ : Dataset with full book images
├── dataset-imagettes/ : Dataset with imagettes (full cropped images)
├── dataset-imagettes_only_head/ : Dataset with imagettes re-annotated with only the heads of the characters
├── scripts/ : Python scripts
├── original-images/ : All the full images
├── original-labels/ : All the full images labels
├── requirements.txt : Python dependencies
├── Charlie.ipynb : A Jupyter Notebook we used to train YOLO on Google Colab.
└── README.md
```

Note : The images' name format is :

\<book number>-\<page number>-\<type>

And for imagettes it's :

\<book number>-\<page number>-\<type>-\<imagette id>

\<type> refers to :

- 0 : full image
- 1 or 2 : halves of a full image
- 3 : cropped part of a full image

## Characters we've chosen to detect

- Waldo
- Odlaw
- Wenda
- Wizard Whitebeard

## How to use the scripts

**<span>split_dataset.py</span>**
Script used to split the original images into a dataset with train, validation and test sets.
Parameters can be changed in the file directly.

**<span>imagettes.py</span>**
Script used to make "imagettes" which are small cropped images of a certain size from original images.
```
python imagettes.py [<images_folder> <labels_folder> <output_dir_images> <output_dir_labels> <imagettes_width> <imagettes_height> <reset_imagettes>]
```

**<span>full_image_predict.py</span>**
Script that uses the trained model (trained on imagettes of size box_size) in order to predict positions of characters in several full images contained in image_folder, with a confidence threshold value.
```
python full_image_predict.py <model_path> <image_folder> <box_size> [<confidence_threshold>]
```

**<span>add_annotations.py</span>**
Script used for quick re-annotations of the already annotated images.
Parameters can be changed in the file directly.

**<span>visualize_annotations.py</span>**
Script that computes the annotated boxes of several images in order to see these boxes clearly.
```
python visualize_annotations.py <images_folder> <labels_folder> <output_folder>
```


## Sources for the images

The project includes datasets from various sources:

- [Hey-Waldo](https://github.com/vc1492a/Hey-Waldo)
- [HereIsWally](https://github.com/tadejmagajna/HereIsWally/tree/master)
- [Brad Kenstler](https://hackernoon.com/wheres-waldo-terminator-edition-8b3bd0805741)
- [Kurtis Brandt](https://universe.roboflow.com/kurtis-brandt/wally-dset-v2)
- [Random acts of Amazon subreddit](https://www.reddit.com/r/Random_Acts_Of_Amazon/search/?q=waldo)
- Scans of the books that we made ourselves.

## Authors

- [Timothée Klein](https://github.com/pekatour)
- [Cyrian Ragot](https://github.com/cyrianR)
- [Yannis Rosseel](https://github.com/yrosseel21)
- [Baptiste Arrix-Pouget](https://github.com/arrix46)

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) for details.
