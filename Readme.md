# Project description

This script will help you to balance your amount of data (images) for training your neural network.
For using this script, you should create BalancedData class object, with to required attributes:
    For clearly describe of how the script works, let's imagine that we have folder like: /user/pictures_folder and
    into this folder we have 3 subfolders: cars, ships and airplanes, where cars folder has 100 pictures, ships has
    400 pictures and airplanes has 800 pictures.

    1) mode - describe the type of normalize, it might be "min", "mean" and "max". "min" - for basic amount of data
    will be take 100 and in another folder all odd data will be deleted. "mean" - for basic amount of data will be
    take mean number of images (100 + 400 + 800)/3 ~ 433 of pictures per class, if the number of pictures in class was
    lower then the mean number then lack of images will be created. "max" - the same logic as "min"

    2) root_folder_path - path to the root folder, in our example it is "/user/pictures_folder"


# Requirements

1) python 3.5 or higher
2) scikit-image 0.13 or higher