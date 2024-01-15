# ProductHunt Scraper

## Overview

This Python script scrapes product details from [ProductHunt](https://www.producthunt.com/) and utilizes the Perplexity
API to gather thoughts on the product. The information is then sent to a Telegram channel. (t.me/newappidea)

## Dependencies

- Python
- Requests library (`pip install requests`)
- BeautifulSoup (`pip install beautifulsoup4`)
- python-dotenv (`pip install python-dotenv`)

## Configuration

1. Create a `.env` file in the project directory with the following variables:

   ```ini
   BOT_TOKEN=your_telegram_bot_token
   CHAT_ID=your_telegram_chat_id
   PPX_TOKEN=your_perplexity_api_token

## Script Components

TelegramRequest: Handles communication with the Telegram bot API for sending messages and photos.

PerplexityRequest: Utilizes the Perplexity API for generating thoughts on a given product.

ProductHuntScraper: Scrapes product details from ProductHunt and invokes the PerplexityRequest to gather thoughts.

