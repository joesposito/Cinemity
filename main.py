from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
#url="https://www.imdb.com/showtimes"
url = "https://www.imdb.com/showtimes/location"

def scrape_movies(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching results, status code: " + response.status_code)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    movie_list = soup.find_all('div', {'class': 'lister-item mode-grid'})
    movie_titles = []
    for movie in movie_list:
        title = movie.find('div', {'class': 'title'}).find('a', {'href': True})
        if title is not None:
            movie_titles.append(title.text)
            print(title.text)

    return movie_titles

@app.route("/current-movies/<region>/<postal_code>", methods=['GET'])
def currently_playing(region, postal_code):
    print(url + "/" + region + "/" + postal_code)
    return jsonify(scrape_movies(url + "/" + region + "/" + postal_code))

if __name__ == "__main__":
    app.run(port=7777)