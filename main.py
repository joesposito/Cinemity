from flask import Flask
from bs4 import BeautifulSoup
import json
import requests

app = Flask(__name__)

showtimes_url = "https://www.imdb.com/showtimes"

#returns list of movies playing locally
@app.route("/currently-playing/<region>/<postal_code>", methods=['GET'])
def currently_playing(region, postal_code):
    print(showtimes_url + "/" + region + "/" + postal_code)
    data_list = scrape_movies(showtimes_url + "/" + region + "/" + postal_code)
    return json.dumps(data_list, indent=4)

#returns list of local movie theaters
@app.route("/theaters-nearby/<region>/<postal_code>", methods=['GET'])
def local_theaters(region, postal_code):
    print(showtimes_url + "/" + region + "/" + postal_code)
    data_list = scrape_theaters(showtimes_url + "/" + region + "/" + postal_code)
    return json.dumps(data_list, indent=4)


def scrape_movies(url):
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching results, status code: " + str(response.status_code))
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    theater_divs = soup.find_all('div', {'class': ['list_item odd', 'list_item even']})
    movies_list = []

    for theater_div in theater_divs:
        movie_divs = theater_div.find_all('div', {'class': 'list_item'})

        for movie_div in movie_divs:
            data = get_movie_info(movie_div)

            if not any(movie.get('title') == data.get('title') for movie in movies_list):
                movies_list.append(data)


    return movies_list

def scrape_theaters(url):
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching results, status code: " + str(response.status_code))
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    #The divs containing theater information are labeled odd and even
    theaters = soup.find_all('div', {'class': ['list_item odd', 'list_item even']})
    theater_list = []

    for theater in theaters:
        data = get_theater_info(theater)
        theater_list.append(data)

    return theater_list

def get_child_value(parent_tag, child_tag):
    try:
        return parent_tag.find(*child_tag).text
    except AttributeError:
        return "n/a"

def get_value(tag, attribute):
    try:
        result = tag.find(attribute).text
        return result
    except AttributeError:
        return 'n/a'

def get_theater_info(theater_div):
    #Go to the descendent of the <h3> tag containing the theater name inside of the correct <a> tag
    theater_name_parent = theater_div.find('h3', {'itemprop': 'name'})
    theater_name = get_child_value(theater_name_parent, ('a', {'itemprop': 'url'}))
    cinema_id = theater_name_parent.find('a', {'data-cinemaid': True}).get('data-cinemaid')

    hearing_accessibility = theater_div.find('li', {'title': 'Hearing Devices Available'})
    has_hearing_accessibility = hearing_accessibility is not None

    wheelchair_accessibility = theater_div.find('li', {'title': 'Wheelchair Accessible'})
    has_wheelchair_accessibility = wheelchair_accessibility is not None

    street_address = get_child_value(theater_div, ('span', {'itemprop': 'streetAddress'}))
    address_locality = get_child_value(theater_div, ('span', {'itemprop': 'addressLocality'}))
    address_region = get_child_value(theater_div, ('span', {'itemprop': 'addressRegion'}))
    address_postal_code = get_child_value(theater_div, ('span', {'itemprop': 'postalCode'}))
    address = street_address + ', ' + address_locality + ', ' + address_region + ', ' + address_postal_code

    data = {'theater_name': theater_name, 'cinema_id': cinema_id, 'address': address, 'has_hearing_accessibility': has_hearing_accessibility,
                           'has_wheelchair_accessibility': has_wheelchair_accessibility}

    return data

def get_movie_info(movie_div):
    title = get_child_value(movie_div, ('a', {'title': True}))

    user_rating = get_value(movie_div, ('strong', {'itemprop': 'ratingValue'}))
    if user_rating != 'n/a':
        user_rating += '/10'

    runtime = get_value(movie_div, ('time', {'itemprop': 'duration'}))

    try:
        content_rating = movie_div.find('span', {'itemprop': 'contentRating'}).find('img').get('title')
    except AttributeError:
        content_rating = 'n/a'

    data = {'title': title, 'user-rating': user_rating, 'runtime': runtime, 'content-rating': content_rating}
    return data

if __name__ == "__main__":
    app.run(port=7777)