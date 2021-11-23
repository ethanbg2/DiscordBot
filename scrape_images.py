import urllib.request
import bs4 as bs
import random

import re
RE_EMOJI = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)

#Caption
from caption_images import caption_image

def process_caption(caption, user):
  #get rid of numbers and '#' from username
    user = ''.join([i for i in str(user) if (not i.isdigit() and not i == '#')])
    #get rid of emojis
    caption = RE_EMOJI.sub(r'', str(caption))

    #add the author of the quote to the caption
    caption  = "\"" + str(caption) + "\"" + "\n" + "-" + str(user)
    return caption

def scrape_images(term, caption, user):
    caption = process_caption(caption, user)
    file_name = ""

    #scrape stock photos site
    url = 'https://www.istockphoto.com/search/2/image?excludenudity=false&mediatype=photography&phrase='+term 
    html = urllib.request.urlopen(url)
    soup = bs.BeautifulSoup(html,'lxml')

    #Get a list of all images
    #valid image links from this website contain "photos"
    images = [img for img in soup.findAll('img') if "photos" in img.get('src')]

    #If no images were found
    if len(images) == 0:
      return "None"

    #pick random image
    random_num = random.randint(0, len(images) - 1)
    image = images[random_num]
    print(image.get('src'))

    #retrieve image
    #if problem with getting image print error
    try:
      URL = image.get('src')
      file_name = term + ".jpeg"
      urllib.request.urlretrieve(URL, file_name)
    except Exception as e:
      pass
      print(e)
      return "None"

    #caption image but make sure there wasn't a problem processing it
    #check if there was problem processing image
    try:
      caption_image(file_name, caption)
      return file_name
    except Exception as e:
      pass
      print(e)
      return "None" 