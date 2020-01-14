"Flask routes"

from flask import render_template
from app import app
import mysql.connector
import sys

#Change this to use different database_host/(user/password)/database_name
DB_HOST = 'localhost'
DB_USER = 'user'
DB_PASSWORD = 'CorrectHorseBatteryStaple'
DB_NAME = 'assignment3'

dbConnector = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
dbCursor = dbConnector.cursor(dictionary=True)
database = DB_NAME
dbConnector.database = database

not_found_error_message = '404 Not found'
internal_server_error_message  = '500 internal server error'

def get_tuple_from_table(id, table):
    input_data = (id,)
    query = 'SELECT * FROM ' + table +' WHERE id = %s'
    dbCursor.execute(query, input_data)
    results = dbCursor.fetchall()

    return results

def get_all_from_table(table, limit):
    query = 'SELECT * FROM ' + table +' LIMIT ' + str(limit)
    dbCursor.execute(query)
    results = dbCursor.fetchall()

    return results

def get_releases_for_artist(id):
    input_data = (id,)
    query = ('SELECT artist_id, title, date, format, label_id, releases.id AS release_id, name as label_name '
             'FROM releases '
             'JOIN labels ON releases.label_id = labels.id '
             'WHERE releases.artist_id = %s')
    dbCursor.execute(query, input_data)
    releases_list = dbCursor.fetchall()

    return releases_list

def get_releases_for_labels(id):
    input_data = (id,)
    query = ('SELECT artist_id, title, date, format, label_id, releases.id AS release_id, artists.name AS artist_name '
             'FROM releases '
             'JOIN artists ON releases.artist_id = artists.id '
             'WHERE releases.label_id = %s')
    dbCursor.execute(query, input_data)
    releases_list = dbCursor.fetchall()

    return releases_list

def get_subgenres_for_genre(id):
    input_data = (id,)
    query = ('SELECT DISTINCT styles.name AS style_name, styles.id AS style_id '
             'FROM styles '
             'JOIN release_genre ON release_genre.style_id = styles.id '
             'WHERE release_genre.genre_id = %s')
    dbCursor.execute(query, input_data)
    subgenres_list = dbCursor.fetchall()

    return subgenres_list

def get_genre_releases(id):
    input_data = (id,)
    query = ('SELECT DISTINCT artist_id, title, date, format, label_id, releases.id AS release_id, artists.name AS artist_name, labels.name as label_name '
             'FROM releases '
             'JOIN artists ON releases.artist_id = artists.id '
             'JOIN release_genre ON release_genre.release_id = releases.id '
             'JOIN labels ON releases.label_id = labels.id '
             'WHERE release_genre.genre_id = %s')
    dbCursor.execute(query, input_data)
    results = dbCursor.fetchall()
    releases_list = results

    return releases_list

def get_subgenre_releases(id):
    input_data = (id,)
    query = ('SELECT DISTINCT artist_id, title, date, format, label_id, releases.id AS release_id, artists.name AS artist_name, labels.name as label_name '
             'FROM releases '
             'JOIN artists ON releases.artist_id = artists.id '
             'JOIN release_genre ON release_genre.release_id = releases.id '
             'JOIN labels ON releases.label_id = labels.id '
             'WHERE release_genre.style_id = %s')
    dbCursor.execute(query, input_data)
    results = dbCursor.fetchall()
    releases_list = results

    return releases_list

def get_search_results(term, type):
    wildcarded_input_data = ('%'+ term + '%',)
    if type == 'artists' or type == 'labels' or type == 'genres':
        query = 'SELECT * FROM ' + type + ' WHERE name LIKE %s'
    elif type == 'releases':
        query = ('SELECT DISTINCT artist_id, title, date, format, releases.id AS release_id, artists.name AS artist_name FROM ' + type +
                 ' JOIN artists ON releases.artist_id = artists.id'
                 ' WHERE title LIKE %s')
    else:
        return []
    dbCursor.execute(query, wildcarded_input_data)
    results = dbCursor.fetchall()

    return results

def get_top_labels():
    query = 'SELECT * FROM top_labels'
    dbCursor.execute(query)
    results = dbCursor.fetchall()
    return results

def get_top_artists():
    query = 'SELECT * FROM top_artists'
    dbCursor.execute(query)
    results = dbCursor.fetchall()
    return results

@app.route('/')
@app.route('/index')
def index():
    top_labels = get_top_labels()
    top_artists = get_top_artists()
    return render_template('index.html', top_labels=top_labels, top_artists=top_artists)

@app.route('/artists')
def render_artists():
    artists = get_all_from_table('artists', 100)
    return render_template('artists.html', artists=artists)

@app.route('/labels')
def render_labels():
    labels = get_all_from_table('labels', 100)
    return render_template('labels.html', labels=labels)

@app.route('/releases')
def render_releases():
    releases = get_all_from_table('releases', 100)
    return render_template('releases.html', releases=releases)

@app.route('/genres')
def render_genres():
    genres = get_all_from_table('genres', 100)
    return render_template('genres.html', genres=genres)

@app.route('/artist/<artist_id>/')
def render_artist(artist_id):
    artist = get_tuple_from_table(artist_id, 'artists')

    if len(artist) == 0:
        return render_template('error.html', errorMessage=not_found_error_message)
    else:
        artist = artist[0]
        artist_releases = get_releases_for_artist(artist_id)
        return render_template('artist.html', title=artist['name'], artist=artist, artist_releases=artist_releases)

@app.route('/label/<label_id>/')
def render_label(label_id):
    label = get_tuple_from_table(label_id, 'labels')

    if len(label) == 0:
        return render_template('error.html', errorMessage=not_found_error_message)
    else:
        label = label[0]
        label_releases = get_releases_for_labels(label_id)
        return render_template('label.html', title=label['name'], label=label, label_releases=label_releases)

@app.route('/release/<release_id>/')
def render_release(release_id):
    release = get_tuple_from_table(release_id, 'releases')

    if len(release) == 0:
        return render_template('error.html', errorMessage=not_found_error_message)
    else:
        release = release[0]
        label = get_tuple_from_table(release['label_id'], 'labels')[0]
        artist = get_tuple_from_table(release['artist_id'], 'artists')[0]
        return render_template('release.html', release=release, label=label, artist=artist)

@app.route('/genre/<genre_id>/')
def render_genre(genre_id):
    genre = get_tuple_from_table(genre_id, 'genres')

    if len(genre) == 0:
        return render_template('error.html', errorMessage=not_found_error_message)
    else:
        genre = genre[0]
        releases = get_genre_releases(genre_id)
        subgenres = get_subgenres_for_genre(genre_id)

        return render_template('genre.html', subgenres=subgenres, genre=genre, genre_releases=releases)

@app.route('/subgenre/<subgenre_id>/')
def render_subgenre(subgenre_id):
    subgenre = get_tuple_from_table(subgenre_id, 'styles')

    if len(subgenre) == 0:
        return render_template('error.html', errorMessage=not_found_error_message)
    else:
        subgenre = subgenre[0]
        releases = get_subgenre_releases(subgenre_id)

        return render_template('subgenre.html', subgenre=subgenre, subgenre_releases=releases)        

@app.route('/search/<type>/<term>')
def render_search(term, type):
    type = type.lower()
    type = type + 's'
    if type == 'artists' or type == 'releases' or type == 'labels' or type == 'genres':
        search_results = get_search_results(term, type)
        return render_template('search.html', type=type, search_results=search_results)

    return render_template('error.html', errorMessage='Broken search usage...')

@app.errorhandler(404) 
def not_found(e): 
  return render_template("error.html", errorMessage=not_found_error_message)

@app.errorhandler(500) 
def internal_server_error(e):
  return render_template("error.html", errorMessage=internal_server_error_message)
