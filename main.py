from flask import Flask
from bs4 import BeautifulSoup
import json
import requests


app = Flask(__name__)
imdb_url = 'https://www.imdb.com/showtimes'


# returns list of movies playing locally
@app.route('/currently-playing/<region>/<postal_code>', methods=['GET'])
def currently_playing(region, postal_code):
    try:
        data_list = scrape_movies(imdb_url + '/' + region + '/' + postal_code)
        return json.dumps(data_list, indent=4)
    except Exception as e:
        return json.dumps({'error': str(e)})


# returns list of local movie theaters
@app.route('/theaters-nearby/<region>/<postal_code>', methods=['GET'])
def local_theaters(region, postal_code):
    try:
        data_list = scrape_theaters(imdb_url + '/' + region + '/' + postal_code)
        return json.dumps(data_list, indent=4)
    except Exception as e:
        return json.dumps({'error': str(e)})


# returns list of movies playing given a cinema id
@app.route('/<region>/<postal_code>/<cinema_id>', methods=['GET'])
def get_showtimes(region, postal_code, cinema_id):
    try:
        data_list = scrape_showtimes(imdb_url + '/' + region + '/' + postal_code, cinema_id)
        return json.dumps(data_list, indent=4)
    except Exception as e:
        return json.dumps({'error': str(e)})

# scrapes the movies
def scrape_movies(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('Error, status code: ' + response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    # The divs containing theater information are labeled odd and even
    theater_divs = soup.find_all('div', {'class': ['list_item odd', 'list_item even']})
    movies_list = []

    # iterate through html structure to get the movie info
    for theater_div in theater_divs:
        movie_divs = theater_div.find_all('div', {'class': 'list_item'})

        for movie_div in movie_divs:
            movie_info = get_movie_info(movie_div, False)

            # no duplicates allowed in this list
            if not any(movie.get('title') == movie_info.get('title') for movie in movies_list):
                movies_list.append(movie_info)

        return movies_list

# scrapes the theaters
def scrape_theaters(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('Error, status code: ' + response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    theaters = soup.find_all('div', {'class': ['list_item odd', 'list_item even']})
    theater_list = []

    # get the info for every theater then add it to our list
    for theater in theaters:
        theater_info = get_theater_info(theater)
        theater_list.append(theater_info)

    return theater_list

# scrapes the showtimes
def scrape_showtimes(url, cinema_id):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception('Error, status code: ' + response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    # The divs containing theater information are labeled odd and even
    theaters = soup.find_all('div', {'class': ['list_item odd', 'list_item even']})
    movies_info = []
    theater_name = 'n/a'


    for theater in theaters:
        # find the specific theater div with the corresponding cinema id
        theater_div = theater.find('a', {'data-cinemaid': cinema_id})
        if theater_div:
            theater_name_parent = theater.find('h3', {'itemprop': 'name'})
            theater_name = get_child_value(theater_name_parent, ('a', {'itemprop': 'url'}))
            movie_divs = theater.find_all('div', {'class': 'list_item'})

            # then get every movie in the movie divs inside of this specific theater
            for movie_div in movie_divs:
                movie_info = get_movie_info(movie_div, True)
                movies_info.append(movie_info)

    movies = []
    showtimes = {'theater-name': theater_name, 'movies': movies}

    # finally add it to our list
    for movie in movies_info:
        showtimes.get('movies').append(movie)

    return showtimes

# useful method for getting the child value of a parent tag if it exists
def get_child_value(parent_tag, child_tag):
    try:
        return parent_tag.find(*child_tag).text
    except AttributeError:
        return 'n/a'

# gets the value a tag given an attribute
def get_value(tag, attribute):
    try:
        result = tag.find(attribute).text
        return result
    except AttributeError:
        return 'n/a'

# helper method to parse the theater html
def get_theater_info(theater_div):
    theater_name_parent = theater_div.find('h3', {'itemprop': 'name'})
    theater_name = get_child_value(theater_name_parent, ('a', {'itemprop': 'url'}))
    cinema_id = theater_name_parent.find('a', {'data-cinemaid': True}).get('data-cinemaid')

    # gets hearing accessibility info
    hearing_accessibility = theater_div.find('li', {'title': 'Hearing Devices Available'})
    has_hearing_accessibility = hearing_accessibility is not None

    # gets wheelchair accessibility info
    wheelchair_accessibility = theater_div.find('li', {'title': 'Wheelchair Accessible'})
    has_wheelchair_accessibility = wheelchair_accessibility is not None

    # gets local theater information
    street_address = get_child_value(theater_div, ('span', {'itemprop': 'streetAddress'}))
    address_locality = get_child_value(theater_div, ('span', {'itemprop': 'addressLocality'}))
    address_region = get_child_value(theater_div, ('span', {'itemprop': 'addressRegion'}))
    address_postal_code = get_child_value(theater_div, ('span', {'itemprop': 'postalCode'}))
    address = street_address + ', ' + address_locality + ', ' + address_region + ', ' + address_postal_code

    theaters = {'theater_name': theater_name, 'cinema_id': cinema_id, 'address': address,
            'has_hearing_accessibility': has_hearing_accessibility,
            'has_wheelchair_accessibility': has_wheelchair_accessibility}

    return theaters

# helper method for getting movie info
def get_movie_info(movie_div, include_showtimes):
    title = get_child_value(movie_div, ('a', {'title': True}))

    user_rating = get_value(movie_div, ('strong', {'itemprop': 'ratingValue'}))
    # if it's a valid rating we can put it out of 10
    if user_rating != 'n/a':
        user_rating += '/10'

    runtime = get_value(movie_div, ('time', {'itemprop': 'duration'}))

    try:
        content_rating = movie_div.find('span', {'itemprop': 'contentRating'}).find('img').get('title')
    except AttributeError:
        content_rating = 'n/a'

    movies = {'title': title, 'user-rating': user_rating, 'runtime': runtime, 'content-rating': content_rating}

    if include_showtimes:
        showtimes_divs = movie_div.find_all('a', {'class': 'tracked-offsite-link'})
        showtimes = []

        # movie times have line breaks we'd like to strip away
        for show in showtimes_divs:
            if show is not None:
                showtimes.append(show.text.strip())

        movies.update({'showtimes': showtimes})

    return movies


if __name__ == '__main__':
    app.run(port=7777)
