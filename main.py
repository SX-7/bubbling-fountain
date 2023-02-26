from io import BytesIO
import sys
import requests
from PIL import Image
from PIL import ImageDraw
#as of rn we're assuming 100% goodwill from the user, and no errors
source_image = Image.open(BytesIO(requests.get(sys.argv[1]).content))
#additional handling for animated content?

#higher level overview - make a speechbubble from pieslice and ellipse, but inverted - it's a mask for tranparency layer
bubble_mask = Image.new("RGBA",(1000,1000),(255,255,255,255))
bubble_mask_drawable = ImageDraw.Draw(bubble_mask)
#in finalized version this will probably need custom inputs
bubble_mask_drawable.pieslice(xy=(0,0,1000,750),start=270,end=280,fill=(255,255,255,0))
bubble_mask_drawable.ellipse(xy=(-500,-1000,1500,150),fill=(255,255,255,0))
bubble_mask = bubble_mask.resize((source_image.width,source_image.height),resample=Image.Resampling.NEAREST)
transparent = Image.new("RGBA",(source_image.width,source_image.height),(255,255,255,0))
result = Image.composite(source_image,transparent,bubble_mask)

#how to handle output? termux's an issue
result.save("res.gif")