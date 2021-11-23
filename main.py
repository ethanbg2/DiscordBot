# the os module helps us access environment variables
# i.e., our API keys
import os

# these modules are for querying the Hugging Face model
import json
import requests

# the Discord Python API
import discord

#Keey script running
from keep_alive import keep_alive

#Scrape images
from scrape_images import scrape_images

import random
import spacy
from spacy.matcher import Matcher


nlp = spacy.load("en_core_web_sm")

# this is my Hugging Face profile link
API_URL ="https://api-inference.huggingface.co/models/ethanbg2/"
EMOJIS = ["😁", "😍",'☺','😗','😙','😘','🥰','😎','😋','😆','😉','😄']
#list2 = ['😃','🤣','😥','🙄','😏','😣','😶','😑','😑','😐','🤩','😫']
#list3 = ['😪','😯','🤔', '🍆']

class MyClient(discord.Client):
    def __init__(self, model_name):
        super().__init__()
        self.api_endpoint = API_URL + model_name
        self.message_counter = 0
        self.MESSAGE_INTER = 2
        # retrieve the secret API token from the system environment
        huggingface_token = os.environ['HUGGINGFACE_TOKEN']
        # format the header in our request to Hugging Face
        self.request_headers = {
            'Authorization': 'Bearer {}'.format(huggingface_token)
        }

        #Change to image directory and get all files
        os.chdir("CaptionedImages/")

    def query(self, payload):
        """
        make request to the Hugging Face model API
        """
        data = json.dumps(payload)
        response = requests.request('POST',
                                    self.api_endpoint,
                                    headers=self.request_headers,
                                    data=data)
        ret = json.loads(response.content.decode('utf-8'))
        return ret

    def make_swear(self, sentence):
      doc = nlp(sentence)

      matcher = Matcher(nlp.vocab)
      pattern = [[{"POS": "NOUN"}]]
      matcher.add("Nouns", pattern)
      matches = matcher(doc)

      vulgar_phrase = "Cock Sucker!"
      swear = "fucking"

      if len(matches) == 0:
        new_sentence = sentence + " " + vulgar_phrase
      else:
        random_match = matches[random.randint(0, len(matches) - 1)]
        new_sentence = doc[0:random_match[1]].text + " " + swear +  " " + doc[random_match[1]:len(doc)].text

      return new_sentence
    
    def get_rand_image(self):
      images = [name for name in os.listdir('.')]
      rand_int = random.randint(1, len(images) - 1)
      return images[rand_int]
    
    def shorten_input_txt(self, text):
      words = text.split(" ")
      if len(words) <= 5:
        return text
      else:
        return " ".join(words[:3])

    async def on_ready(self):
        # print out information when the bot wakes up
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        # send a request to the model without caring about the response
        # just so that the model wakes up and starts loading
        self.query("Hello!")


    async def on_message(self, message):
        """
        this function is called whenever the bot sees a message in a channel
        """
        # ignore the message if it comes from the bot itself
        if message.author.id == self.user.id:
            return

        text = message.content
        #if they want inspirational image
        if text == "!inspire":
          picture = self.get_rand_image()
          await message.channel.send(file=discord.File(picture))
          return
        #if they want to caption an image
        elif text[:1] == "#":
          keyword = text[1:]
          #can't have spaces in search
          if " " in keyword:
            await message.channel.send("Get rid of your spaces fucker!")
            return

          # TODO make sure pinned message is not image
          #pick random pinned message
          pins = await message.channel.pins()
          pin = pins[random.randint(0, len(pins) - 1)]
          

          #find picture, caption it and send it
          file_path = scrape_images(keyword, pin.content, pin.author)
          if file_path == "None":
            await message.channel.send("Couldn't find this image you Bitch!")
            return
          else:
            await message.channel.send(file=discord.File(file_path))
          #remove file afterwards
          os.remove(file_path)


        #So it doesn't respond after every chat
        self.message_counter += 1
        if self.message_counter < self.MESSAGE_INTER:
          return
        else:
          # change the response interval so it's random
          self.MESSAGE_INTER = random.randint(3,7)
          self.message_counter = 0

        #shorten text so bot can complete it
        text = self.shorten_input_txt(text)

        # while the bot is waiting on a response from the model
        # set the its status as typing for user-friendliness
        async with message.channel.typing():
          response = self.query(text)
        
        #Handles response if the model is still loading
        try:
          bot_response = response[0].get('generated_text', None)
        except Exception as e:
          pass
          print(e)
          await message.channel.send("...Waking up... you bastard!")
          return
        
        # we may get ill-formed response if the model hasn't fully loaded
        # or has timed out
        if not bot_response:
            if 'error' in response:
                bot_response = '`Error: {}`'.format(response['error'])
            else:
                bot_response = 'Hmm... something is not right.'
        
        #add swears and emojis
        bot_response = self.make_swear(bot_response)
        emoji1 = EMOJIS[random.randint(0, len(EMOJIS) - 1)]
        emoji2 = EMOJIS[random.randint(0, len(EMOJIS) - 1)]
        bot_response = bot_response + " " + emoji1 + emoji2

        # send the model's response to the Discord channel
        await message.channel.send(bot_response)




def main():
    # DialoGPT-medium-joshua is my model name
    client = MyClient('DialoGPT-small-BonerBot')
    keep_alive()
    client.run(os.environ['DISCORD_TOKEN'])

if __name__ == '__main__':
  main()