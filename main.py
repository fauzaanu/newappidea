import json
import os
import time
from pprint import pprint
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv


class TelegramRequest:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv('BOT_TOKEN')
        self.chat_id = os.getenv('CHAT_ID')
        self.max_caption_length = 1024
        self.max_message_length = 4096

    def send_photo(self, message, image_url):
        # sends picture message with caption
        url = "https://api.telegram.org/bot" + self.bot_token + "/sendPhoto"
        data = {
            "chat_id": self.chat_id,
            "caption": message,
            "photo": image_url,
        }
        res = requests.post(url, data=data)
        pprint(res.json())
        return res.json()['result']['message_id']

    def send_message(self, message, reply_to_message_id):
        # sends text message
        url = "https://api.telegram.org/bot" + self.bot_token + "/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        res = requests.post(url, data=data)
        pprint(res.json())
        time.sleep(5)


class PerplexityRequest:
    def __init__(self):
        load_dotenv()
        self.ppx_token = os.getenv('PPX_TOKEN')
        self.model = "pplx-7b-online"

    def call(self, product_name, product_description, product_url, product_image_url):
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Be precise, concise, and clear."
                },
                {
                    "role": "user",
                    "content":
                        "Product Name:" + product_name + "\n" + "Product Description:" + product_description + "\n\nHow unique is this product? Rate it from 1 to 10. Critique it. Are you impressed?"
                }
            ]
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": "Bearer " + self.ppx_token
        }

        response = requests.post(url, json=payload, headers=headers)
        message = response.json()
        pprint(message)
        ppx_thoughts = message['choices'][0]['message']['content']
        # pprint(message)

        message = product_name + "\n" + product_description + "\n\n" + product_url
        call_durov = TelegramRequest()
        message_id = call_durov.send_photo(message, product_image_url)
        pprint(message_id)
        call_durov.send_message(ppx_thoughts, int(message_id))


class ProductHuntScraper:
    def __init__(self):
        self.entry_point = 'https://www.producthunt.com/all'
        self.links = []
        self.base_url = 'https://www.producthunt.com/'
        self.read_page(self.entry_point)

        self.product_name = ""
        self.product_description = ""
        self.product_url = ""
        self.product_image_url = ""

    def read_page(self, url):
        # time.sleep(60)
        page = requests.get(url)
        html = page.content
        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup.find_all('a', href=lambda href: href and 'posts' in href):
            self.product_url = self.base_url + tag['href']
            self.read_meta(self.product_url)

    def read_meta(self, url):
        page = requests.get(url)
        html = page.content
        soup = BeautifulSoup(html, 'html.parser')

        # grab the name
        for tag in soup.find_all('meta', attrs={'property': 'og:title', 'content': True}):
            self.product_name = tag['content'].split(" | ")[0]
            pprint("Product Name: " + str(self.product_name))

        # grab the description
        for tag in soup.find_all('meta', attrs={'name': 'description', 'content': True}):
            self.product_description = tag['content']
            pprint("Product Description: " + str(self.product_description))

        # grab the image
        for tag in soup.find_all('meta', attrs={'property': 'og:image', 'content': True}):
            self.product_image_url = tag['content']
            pprint("Product Image URL: " + str(self.product_image_url))

        # grab product url
        #      "cleanUrl": "malaysiaonlinevisa.com/malaysia-visa-for-india",
        next_data = soup.find("script", {"id": "__NEXT_DATA__"})
        data_content = next_data.string
        data = json.loads(data_content)
        # pprint(data)
        # with open('data.json', 'w') as outfile:
        # json.dump(data, outfile)

        # Extract cleanUrl
        apollo_state = data["props"]["apolloState"]
        pprint(apollo_state)

        for key, value in apollo_state.items():
            if isinstance(value, dict) and "cleanUrl" in value:
                self.product_url = value["cleanUrl"]
                break

        with open('posted_links', 'r') as outfile:
            for line in outfile:
                if self.product_url in line:
                    pprint("Already posted")
                    return

        with open('posted_links', 'a') as outfile:
            outfile.write(self.product_url + "\n")

        PerplexityRequest().call(self.product_name, self.product_description, self.product_url, self.product_image_url)


if __name__ == '__main__':
    scraper = ProductHuntScraper()
