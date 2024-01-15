from flask import Flask, jsonify
import json
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
showtimes_url = "https://www.imdb.com/showtimes"
movies_url = "https://www.imdb.com/showtimes/location"

def scrape_movies(url):
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching results, status code: " + str(response.status_code))
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    movie_list = soup.find_all('div', {'class': 'lister-item mode-grid'})
    movies_list = []

    for movie in movie_list:
        title_parent = movie.find('div', {'class': 'title'})
        title = get_child_value(title_parent, ('a', {'href': True}))

        metascore_parent = movie.find('div', {'class': 'inline-block ratings-metascore'})
        metascore = get_child_value(metascore_parent, 'span')
        metascore = metascore.strip()

        runtime_parent = movie.find('div', {'id': 'runtime'})
        runtime = get_child_value(runtime_parent, ('strong'))

        release_date_parent = movie.find('div', {'id': 'release_date'})
        release_date = get_child_value(release_date_parent, 'span')

        data = {title: {'metascore': metascore, 'runtime': runtime, 'release-date': release_date}}
        movies_list.append(data)

    return movies_list

def get_child_value(parent_div, child_tag):
    try:
        return parent_div.find(child_tag).text
    except AttributeError:
        return "n/a"

@app.route("/current-movies/<region>/<postal_code>", methods=['GET'])
def currently_playing(region, postal_code):
    print(url + "/" + region + "/" + postal_code)
    data_list = scrape_movies(url + "/" + region + "/" + postal_code)
    return json.dumps(data_list, indent=4)

if __name__ == "__main__":
    app.run(port=7777)