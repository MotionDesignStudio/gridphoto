#!/usr/bin/env python3
#from random import random
from PIL import Image
import argparse
import pathlib
import os
import random

# Init parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument( "-g", "--Graphic", help = "Image" )
parser.add_argument( "-c", "--Columns", help = "Enter number of columns", type= int )
parser.add_argument( "-r", "--Rows", help = "Enter number of rows", type= int )
parser.add_argument( "-q", "--Quality", help = "0 - 100 only for JPEG, TIFF, WebP", type= int )
parser.add_argument( "-d", "--Directory", help = "Save to Directory" )
parser.add_argument( "-s", "--Save", help = "Rebuilding ONLY image name" )
parser.add_argument( "-j", "--JasonR", help = "Provides a JSON file for rebuild image" )
parser.add_argument( "-e", "--Effects", help = "Randomized Tiling Choices: 2, 3 or 4" )

# Read arguments from command line
args = parser.parse_args()

class GridPhoto:
    def __init__(self, imgObject, columns, rows ): 
        self.imgObject = imgObject
        self.imgWidth = imgObject.width
        self.imgHeight = imgObject.height
        self.columns = columns
        self.rows = rows
        self.alertMessageColumns = ""
        self.alertMessageRows = ""
        self.alertWidth()
        self.alertHeight()
        self.rebuildDictionary={ "info": {} }
        self.testDic ={"info": {} }
        self.fileExtension = pathlib.Path(self.imgObject.filename).suffix
        self.makeListForCropImages()
        
                
        self.makeImages()
    
    def alertWidth(self):
        # Check if the number of columns are not equally divisible
        # will test for true if remainder not zero
        if ( self.imgWidth % self.columns ):
            self.alertMessageColumns = f"File : {self.imgObject.filename} columns not divisble evenly. Remainder : {self.imgWidth % self.columns} No Action needed."

    def alertHeight(self):
        # Check if the number of rows are not equally divisible
        # will test for true if remainder not zero
        if ( self.imgHeight % self.rows ):
            self.alertMessageRows = f"File : {self.imgObject.filename} rows not divisble evenly. Remainder : {self.imgHeight % self.rows} No Action needed."

    def makeListForCropImages(self):
        self.rebuildDictionary[ "info" ]["width"] = self.imgObject.width
        self.rebuildDictionary[ "info" ]["height"] = self.imgObject.height
        self.rebuildDictionary[ "info" ]["mainTileWidth"] = self.columns
        self.rebuildDictionary[ "info" ]["mainTileHeight"] = self.rows

        rowPosition = 0
        # Crop images
        # Filename for the dictionary
        filenameforDictionary=""
        xAxisIterator = self.columns
        yAxisIterator = self.rows
        # create empty array to store x and y positions
        croppingList = []
        filenameList = []
        incrementX = 0
        incrementY = 0
        #loop over and build list
        for y in range (0, self.imgHeight, yAxisIterator ):
            
            incrementY += yAxisIterator
            if incrementY > self.imgHeight:
                incrementY = self.imgHeight
            for i in range (0, self.imgWidth, xAxisIterator ):
                incrementX += xAxisIterator

                # If x position overshoots the max width set to the max image width
                if incrementX > self.imgWidth:
                    incrementX = self.imgWidth

                #  Adding Width and Height to help with rebuilding using special effects    
                W = incrementX - i
                H = incrementY - y

                croppingList.append( ( i, y, incrementX, incrementY ) )
                filenameforDictionary = "%s_%s_%s_%s_%s_%s%s" % ( i, y, incrementX, incrementY, W, H, self.fileExtension )
                filenameList.append( filenameforDictionary )            
                #ex: 0_0_65_50_65_50.png
           
            # This is row position for the images in the dictionary 
            self.rebuildDictionary[ rowPosition ] = filenameList.copy()
            rowPosition += 1
            # Clear important variables for each row
            croppingList.clear()
            filenameList.clear()
            incrementX = 0
        
        # Add information for the two tiles that could cause issues when doing a randomization of positions
        removedExt = os.path.splitext( self.rebuildDictionary[0][-1] )[0].split( "_") 
        self.rebuildDictionary[ "info" ]["lastTileWidth"] = int (removedExt[4])

        removedExt=  os.path.splitext( self.rebuildDictionary[rowPosition - 1][-1]  )[0].split( "_") 
        self.rebuildDictionary[ "info" ]["lastBottomRithTileHeight"] = int ( removedExt[5] )
        
        # This will feel strange because I use range as a counter 
        # that uses this number for the dictionary values later when rebuilding the image
        # range terminate before the last number
        self.rebuildDictionary[ "info" ]["numOfRows"] = rowPosition 


    def makeImages(self):
        savedToDirectory = ""
        # Failsafe if the directory already exists.
        if args.Directory:
            savedToDirectory = args.Directory +"/"
            try:
                os.mkdir( savedToDirectory )
            except OSError as error:
                print ( error )


        for row in range ( self.rebuildDictionary["info"]["numOfRows"] ) :

            for file in self.rebuildDictionary[ row ]:
                top, left, right, bottom, *extra  = file.split( "_")
                self.imgObject.crop(  ( int (top) , int(left), int(right), int(bottom) ) ).save( savedToDirectory + file , quality=args.Quality if args.Quality else 75 )

        # create json object from dictionary
        import json

        # A possible bug might be here with the saving paths 
        # with open( "%s.json" % (savedToDirectory + self.imgObject.filename), "w") as fp:
        with open( "%s.json" % ( savedToDirectory +  os.path.basename( args.Graphic ) ), "w") as fp:
           json.dump( self.rebuildDictionary, fp, indent = 4)



            
# Function only for rebuilding a image from an external JSON file
def rebuildImage(JSONFile):

    savedToDirectory=""
    if args.Directory:
        savedToDirectory = args.Directory +"/"

    print ( "Rebuilding Image")
    import json
    with open(JSONFile, "r") as fp:
        rebuildDictionary = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()} )
    
    # Set original dimensions of the image 
    originalImgWidth = rebuildDictionary["info"]["width"]
    originalImgHeight= rebuildDictionary["info"]["height"]

    # This needs to be expanded to include other file formats not supporting RGBA
    setModeDepth = "RGBA"

    # Failsafe if the user provides no filename to be saved
    try:
        if pathlib.Path( args.Save ).suffix.find("jpg"):
            setModeDepth = "RGB"
    except TypeError as error:
        print ( error )
        print (  "If you are rebuilding an image you need to add an output name using ex. -s IMAGE_NAME.EXT" )

    newImage = Image.new( setModeDepth, ( originalImgWidth, originalImgHeight ))


    randomRow = [ *range ( rebuildDictionary["info"]["numOfRows"] ) ]
    randomColumns = [ *range (    len ( rebuildDictionary[ 0 ] )      ) ]
    # Randomize Row Only create a random list the length of the sum of row and shuffle
    # This needs to modify behavior for Y since it is extracted from the image
    if args.Effects == "2" or args.Effects == "4":
        print ( "Randomized Rows" )
        
        random.shuffle ( randomRow ) 
        
        #print ( randomRow )
        yp = 0
        xp = 0
        for row in randomRow:
            #print ( "YP :: %s" % yp )
            #print ( rebuildDictionary[ row ] )
            for image in rebuildDictionary[ row ]:
                pass
                #print ( image )
            
            removedExt = os.path.splitext( rebuildDictionary[ row ][0] )[0].split( "_")
            #print ( "RRRR ::: %s " % rebuildDictionary[ row ][0] )
            #print ( "removedExt ::: %s " % removedExt )
            yp += int ( removedExt[5] )

    # Randomizing X positions aka Columns
    if args.Effects == "3" or args.Effects == "4":
        print ( "Randomizing Columns")
        
        random.shuffle ( randomColumns ) 
        for row in randomRow:
            for image in randomColumns:
                pass
                #print ( "Random :: %s  Image :: %s " % (image, rebuildDictionary[ row ][ image ] ) )

            #print ( rebuildDictionary[ row ] )
            #for image in rebuildDictionary[ row ]:
             #   print ( image )




    yPosition = 0
    xPosition = 0

    for row in randomRow:    
        
        for image in randomColumns:

            removedExt = os.path.splitext(    rebuildDictionary[ row ][ image ]    )[0].split( "_")
            newImage.paste( Image.open(  savedToDirectory + rebuildDictionary[ row ][ image ]  ), ( xPosition, int ( yPosition ) ) )
            xPosition += int ( removedExt[4] )
            
        xPosition = 0
        removedExt = os.path.splitext( rebuildDictionary[ row ][0] )[0].split( "_")
        yPosition += int ( removedExt[5] )


        


    # Original way of placing images using the corodinates embeded within the name
    """
    for i in range ( rebuildDictionary["info"]["numOfRows"] ) :
        for image in  rebuildDictionary[ i ]:
            newImage.paste( Image.open( image ), ( int ( image.split( "_")[0] ), int ( image.split( "_")[1] ) ) )
    """
    

    # Failsafe for ...
    try:
        newImage.save( args.Save, quality=args.Quality if args.Quality else 75 )
        # Debuging Only
        #Image.open( args.Save ).show()
    except ValueError as error:
        print ( error )
    
    

def effects( JSONFile ):
    print ( "Applying Special Effects" )
    import json
    with open(JSONFile, "r") as fp:
        rebuildDictionary = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()} )
    

if args.Graphic and args.Rows and args.Columns:
    # Init the PIL Image and assign it a value
    # error check needs to occur to avoid no file or not an image files
    im = Image.open( args.Graphic)
    mainImage = GridPhoto( im, args.Columns, args.Rows )
else:
    print ( "The following parameters -g, -c and -r are needed to create [ Tiles and a JSON rebuild file ] for a image." )


if args.JasonR and args.Save:
    rebuildImage( args.JasonR )

# Init special effects
if args.Effects and args.JasonR:
    pass
    #effects( args.JasonR )
    #pass

