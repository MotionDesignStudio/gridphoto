#!/usr/bin/env python3
from textwrap import indent
from xmlrpc.client import TRANSPORT_ERROR
from PIL import Image
import argparse
import pathlib
import os

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
parser.add_argument( "-e", "--Effects", help = "Randomized Tiling" )

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
        self.listForCroppingAndRebuilding = []
        #self.rebuildList=[]
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
                #print (" W :: "+ str (incrementX - i) + "  H :: " + str ( incrementY - y ) )
                W = incrementX - i
                H = incrementY - y


                croppingList.append( ( i, y, incrementX, incrementY ) )
                #filenameforDictionary = "%s_%s_%s_%s%s" % ( i, y, incrementX, incrementY, self.fileExtension )
                filenameforDictionary = "%s_%s_%s_%s_%s_%s%s" % ( i, y, incrementX, incrementY, W, H, self.fileExtension )
                #print ( "filenameforDictionary :: %s" % filenameforDictionary )
                filenameList.append( filenameforDictionary )            
                #ex: 0_0_65_65.png

            self.listForCroppingAndRebuilding.append( croppingList.copy() )
           
            # This is row position for the images in the dictionary 
            self.rebuildDictionary[ rowPosition ] = filenameList.copy()
            rowPosition += 1
            # Clear important variables for each row
            croppingList.clear()
            filenameList.clear()
            incrementX = 0
        
        # Add information for the two tiles that could cause issues when doing a randomization of positions
        removedExt = os.path.splitext( self.rebuildDictionary[0][-1] )[0].split( "_") 
        self.rebuildDictionary[ "info" ]["lastTileWidth"] = int (removedExt[2]) - int (removedExt[0])

        removedExt=  os.path.splitext( self.rebuildDictionary[rowPosition - 1][-1]  )[0].split( "_") 
        self.rebuildDictionary[ "info" ]["lastBottomRithTileHeight"] = int (removedExt[-1]) - int (removedExt[1])
        
        # This will feel strange because I use range as a counter 
        # that uses this number for the dictionary values later when rebuilding the image
        # range terminate before the last number
        self.rebuildDictionary[ "info" ]["numOfRows"] = rowPosition 

        # create json object from dictionary
        import json
        with open( "%s.json" % (self.imgObject.filename), "w") as fp:
            json.dump( self.rebuildDictionary, fp, indent = 4)

    def makeImages(self):
        savedToDirectory = ""
        # Failsafe if the directory already exists.
        if args.Directory:
            savedToDirectory = args.Directory +"/"
            try:
                os.mkdir( savedToDirectory )
            except OSError as error:
                print ( error )

        print (  "XXXX self.rebuildDictionary XXXXX :: %s" % self.rebuildDictionary )
        #print (  "WWWWW self.listForCroppingAndRebuilding  WWWWW :: %s" % self.listForCroppingAndRebuilding )

        for i in range ( self.rebuildDictionary["info"]["numOfRows"] ) :
            print ( self.rebuildDictionary[ i ] )
            print ( self.listForCroppingAndRebuilding[i] )
            for file in self.rebuildDictionary[ i ]:
                pass
                #print ( file )
        

        nameOfTileImage = ""
        for outerList in self.listForCroppingAndRebuilding:
            for innerTuples in outerList:
                # Build the name
                
                for character in innerTuples:
                    nameOfTileImage += str(character)+"_"

                nameOfTileImage = savedToDirectory + nameOfTileImage[:-1] + self.fileExtension 

                #print (  "OOOOO :: %s" % nameOfTileImage )

                # Build list of filenames used to place image back together
                #self.rebuildList.append( nameOfTileImage )

                self.imgObject.crop( innerTuples ).save( nameOfTileImage , quality=args.Quality if args.Quality else 75 )
                
                # Reset this name variable
                nameOfTileImage = ""

            

    
# Function only for rebuilding an image from an external JSON file
def rebuildImage(JSONFile):
    # The original dimensions of the image are available
    # I am calulating then from the array if trying to build the image from a dictionary

    print ( "Rebuilding Image")
    import json
    with open(JSONFile, "r") as fp:
        rebuildDictionary = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()} )
    
    originalImgWidth = rebuildDictionary["info"]["width"]
    originalImgHeight= rebuildDictionary["info"]["height"]

    # This needs to be exxpanded to incluse other file formats not supporting RGBA
    setModeDepth = "RGBA"

    # Failsafe if the user provides no filename to be saved
    try:
        if pathlib.Path( args.Save ).suffix.find("jpg"):
            setModeDepth = "RGB"
    except TypeError as error:
        print ( error )
        print (  "If you are rebuilding an image you need to add an output name using ex. -s IMAGE_NAME.EXT" )

    newImage = Image.new( setModeDepth, ( originalImgWidth, originalImgHeight ))

    for i in range ( rebuildDictionary["info"]["numOfRows"] ) :
        #print ( i )
        for image in  rebuildDictionary[ i ]:
            newImage.paste( Image.open( image ), ( int ( image.split( "_")[0] ), int ( image.split( "_")[1] ) ) )

    # Failsafe for ...
    try:
        newImage.save( args.Save, quality=args.Quality if args.Quality else 75 )
    except ValueError as error:
        print ( error )

    

def effects( JSONFile ):
    print ( "Applying Special Effects" )
    import json
    with open(JSONFile, "r") as fp:
        rebuildDictionary = json.load(fp, object_hook=lambda d: {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()} )
    
    print ( rebuildDictionary )

    print ( rebuildDictionary[0] )

    # Rebuild Image


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
    effects( args.JasonR )
    #pass

