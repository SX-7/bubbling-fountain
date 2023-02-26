from io import BytesIO
import sys
import requests
from PIL import Image
from PIL import ImageDraw
from PIL import UnidentifiedImageError
from PIL import ImageSequence
try:
    source_image = Image.open(BytesIO(requests.get(sys.argv[1]).content))
except IndexError:
    print("URL adress has not been provided")
    sys.exit(-1)
except UnidentifiedImageError:
    print("File at the URL adress is not an image file")
    sys.exit(-2)
except:
    print("Error while parsing URL, or retrieving content")
    sys.exit(-3)
#additional handling for animated content?

output_frames =[]
frame_length=[]

for frame in ImageSequence.Iterator(source_image):
    #higher level overview - make a speechbubble from pieslice and ellipse, but inverted - it's a mask for tranparency layer
    
    bubble_mask = Image.new("RGBA",(1000,1000),(255,255,255,255))
    bubble_mask_drawable = ImageDraw.Draw(bubble_mask)
    #in finalized version this will probably need custom inputs
    bubble_mask_drawable.pieslice(xy=(0,0,1000,750),start=270,end=280,fill=(255,255,255,0))
    bubble_mask_drawable.ellipse(xy=(-500,-1000,1500,150),fill=(255,255,255,0))
    bubble_mask = bubble_mask.resize((source_image.width,source_image.height),resample=Image.Resampling.NEAREST)
    transparent = Image.new("RGBA",(source_image.width,source_image.height),(255,255,255,0))
    output_frames.append(Image.composite(frame,transparent,bubble_mask))
    try:
        frame_length.append(frame.info['duration'])
    except:
        frame_length.append(0)

#how to handle output? termux's an issue
output_frames[0].save("res.gif",save_all=True, append_images=output_frames[1:],loop=0,duration=frame_length)