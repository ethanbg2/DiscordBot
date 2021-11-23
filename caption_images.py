# importing necessary functions from PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageFilter

def caption_image(file_path, caption):
    img = Image.open(file_path)
    img = img.filter(ImageFilter.GaussianBlur(3))
    width, height = img.size

    # darken image
    source = img.split()

    R, G, B = 0, 1, 2
    constant = 1.5  # constant by which each pixel is divided

    Red = source[R].point(lambda i: i / constant)
    Green = source[G].point(lambda i: i / constant)
    Blue = source[B].point(lambda i: i / constant)

    img = Image.merge(img.mode, (Red, Green, Blue))

    # draw image
    draw = ImageDraw.Draw(img)

    # get font for image and size
    font = ImageFont.truetype("Arial-Bold.ttf", 15)
    w, h = draw.textsize(caption, font=font)
    #h += int(h*.25)

    # First Caption on First image
    draw.text(((width-w)/2, (height - h)/2), caption, fill="white", font=font, align="center")

    # save image
    img.save(file_path)

