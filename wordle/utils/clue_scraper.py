import json
import re
import requests
from typing import Dict, Optional

from bs4 import BeautifulSoup


# Constants
CLUES_FILE_PATH = '../resources/clues.json'
BASE_URL = 'https://www.graycell.ru'
NUM_LETTERS = 5  # note: code tested for 5-letter-words only


# fetch HTML content
def fetch_html(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch {url}")


def extract_word_links(html_content: bytes) -> Optional[Dict]:
    word_links = {}
    soup = BeautifulSoup(html_content, 'html.parser')
    try:
        word_link_elements = (soup.find('div', class_='maincontent')
                              .find('p', class_='otst')
                              .findAll('a', class_='baseblue'))
    except AttributeError:
        return None

    for element in word_link_elements:
        text = element.get_text()
        word_links[text] = f'/word/{text}'

    return word_links


# extract the first word clue from a word page
def extract_description(html_content: bytes) -> str:
    description = ''
    soup = BeautifulSoup(html_content, 'html.parser')

    description_block = (soup.find('div', class_='maincontent')
                             .find('div', itemprop="mainEntity")
                             .find('p', class_='description'))

    if description_block:
        element = description_block.find('span', class_='base')
        if element:
            description = element.get_text(separator=' ', strip=True).split(' ', 1)[1]

    return description


def clean_text(text: str) -> str:
    text = re.sub(r'\s+([,.!?:;-])', r'\1', text)
    text = re.sub(r'«\s+', '«', text)
    text = re.sub(r'\s+»', '»', text)

    return text


def scrape_data() -> json:
    data = {}
    page_number = 1
    looping = True

    while looping:
        page_url = f'{BASE_URL}/dict/{NUM_LETTERS}/{page_number}.html'
        # Fetch the page HTML
        page_html = fetch_html(page_url)

        # Extract word links
        word_links = extract_word_links(page_html)

        if word_links:
            for word, link in word_links.items():
                word_url = f'{BASE_URL}{link}'
                word_html = fetch_html(word_url)
                description = extract_description(word_html)
                if description:
                    description = clean_text(description)
                    data[word.lower()] = description

            page_number += 1
        else:
            looping = False
    return json.dumps(data, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    result = scrape_data()
    with open(CLUES_FILE_PATH, 'w') as json_file:
        json_file.write(result)

