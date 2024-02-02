
# IMDB Showtimes API
This is a simple Flask application that provides an API to retrieve information about currently playing movies, local theaters, and showtimes based on the region and postal code.
My original intention was to use this to pull real time data into a Spring Boot movie theater web application.

# How To
Prerequisites:
Make sure you have Python installed on your system.


Clone the repository to your local machine:

```bash
git clone https://github.com/joesposito/Cinemity
cd Cinemity
```

Install the required Python packages:
```bash
pip install Flask
pip install beautifulsoup4
pip install requests
```

Run the application:
```bash
python main.py
```

The application will start running on port 7777 automatically.
At this point you can make requests using either Postman or via the http://localhost:7777 URL.

## Access the API endpoints:

Currently Playing Movies:

Endpoint: /currently-playing/&lt;region&gt;/&lt;postal_code&gt;
Example: http://localhost:7777/currently-playing/us/90210


Local Theaters:
Endpoint: /theaters-nearby/&lt;region&gt;/&lt;postal_code&gt;
Example: http://localhost:7777/theaters-nearby/us/90210

Showtimes for a Theater:
Endpoint: /&lt;region&gt;/&lt;postal_code&gt;/&lt;cinema_id&gt;
Example: http://localhost:7777/us/90210/12345
