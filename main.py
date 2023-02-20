from io import BytesIO
import requests
from PIL import Image
from PIL import ImageDraw
#t=sys.argv[1]
#idk, some processing - as of rn we're assuming 100% goodwill from the user, and no errors
url="https://en.wikipedia.org/static/images/icons/wikipedia.png"
r=requests.get(url)
img = Image.open(BytesIO(r.content))
bubble = Image.new("RGBA",(img.width,100),(255,255,255,255))
d = ImageDraw.Draw(bubble)
d.ellipse(xy=(-50,-100,img.width+50,50),fill=(255,255,255,0),outline=(0,0,0,255),width=10)
#TODO: speech bubble "arrows"
#      math based angles on the ellipsis
#      more might be coming, but that's after this part's done
res = Image.new("RGBA",(img.width,bubble.height+img.height))
res.paste(bubble)
res.paste(img,(0,bubble.height))
res.save("res.png")