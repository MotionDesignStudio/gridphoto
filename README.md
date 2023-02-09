# gridphoto
## This makes tiles from a larger image.

] USAGE [ 

./gridPhotoV1.py -h
```
usage: gridPhotoV1.py [-h] [-g GRAPHIC] [-c COLUMNS] [-r ROWS] [-q QUALITY] [-d DIRECTORY] [-s SAVE] [-j JASONR] [-e EFFECTS]

optional arguments:
  -h, --help            show this help message and exit
  -g GRAPHIC, --Graphic GRAPHIC
                        Image
  -c COLUMNS, --Columns COLUMNS
                        Enter number of columns
  -r ROWS, --Rows ROWS  Enter number of rows
  -q QUALITY, --Quality QUALITY
                        0 - 100 only for JPEG, TIFF, WebP
  -d DIRECTORY, --Directory DIRECTORY
                        Save to Directory
  -s SAVE, --Save SAVE  Rebuilding ONLY image name
  -j JASONR, --JasonR JASONR
                        Provides a JSON file for rebuild image
  -e EFFECTS, --Effects EFFECTS
                        Randomized Tiling Choices: 2, 3 or 4
```

] EXAMPLE [

Each with produce tiles and a .json file used to rebuild the image.
```
./gridPhotoV1.py -g testImages/box.gif -r 65 -c 65
```
	- g  image location | -r height of tiles | – c width of tiles

Specify A Output Directory :
```
./gridPhotoV1.py -g testImages/box.gif -r 65 -c 65 -d tmp
```
    -d output directory will be created and must not exist before hand.

Rebuilding Images From Specific Directory :
```
./gridPhotoV1.py -j tmp/box.gif.json -q 90 -d tmp  -s buidImage.jpg
```
	-j mandatory source .json file | -q quality [0 – 100] not all file format support | -s output image name

Randomized Rebuilding of image :
```
./gridPhotoV1.py -j tmp/box.gif.json -q 90 -d tmp -e 4  -s buidImage.jpg
```
	-e built in randomize placement of tiles during rebuild