from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
url="https://www.imdb.com/showtimes"

def scrape_movies(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error: Status Code " + response.status_code)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    list_item = soup.find_all('div', {'class': 'list_item'})
    titles = []

    for item in list_item:
        #Goes to the child of the <span> tag containing the <a> link with the value being the movie name
        title = item.find('span', {"itemprop": True}).find('a', {"title": True})
        if title is not None:
            titles.append(title.text)
            #print(title.text)
    print(titles)
    return

@app.route("/<region>/<postal_code>", methods=['GET'])
def movieData(region, postal_code):
    print(url + "/" + region + "/" + postal_code)
    scrape_movies(url + "/" + region + "/" + postal_code)
    return jsonify(message="Getting movies for " + postal_code + ", " + region)

if __name__ == "__main__":
    app.run(port=7777)