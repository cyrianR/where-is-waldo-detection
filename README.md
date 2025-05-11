# Charlie-DB

This project implements a YOLO-based detection model for "Where's Waldo?" books. It provides two datasets, the original images used and some scripts used for the project.

## Project Structure

```
Charlie-DB/
│
├── dataset/ : Dataset with full book images
├── dataset-imagettes/ : Dataset with imagettes (full cropped images)
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

## Sources for the images

The project includes datasets from various sources:

- [Hey-Waldo](https://github.com/vc1492a/Hey-Waldo)
- [HereIsWally](https://github.com/tadejmagajna/HereIsWally/tree/master)
- [Brad Kenstler](https://hackernoon.com/wheres-waldo-terminator-edition-8b3bd0805741)
- [Kurtis Brandt](https://universe.roboflow.com/kurtis-brandt/wally-dset-v2)
- [Random acts of Amazon subreddit](https://www.reddit.com/r/Random_Acts_Of_Amazon/search/?q=waldo)
- Scans of the books that we made ourselves.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) for details.
