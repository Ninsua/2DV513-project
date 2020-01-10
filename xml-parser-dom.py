from xml.dom.minidom import parse
import xml.dom.minidom
import mysql.connector

print("\nGenerating DOM and making collection of releases...")
DOMTree = xml.dom.minidom.parse("discogs_20080309_releases.xml")
collection = DOMTree.documentElement

releases = collection.getElementsByTagName("release")
print("Done")

def add_artists(artist_data):     
    artist_query = ("INSERT IGNORE INTO artists (name) VALUES (%s)")
    dbCursor.executemany(artist_query, artist_data)

def add_labels(label_data):
    label_query = ("INSERT IGNORE INTO labels (name) VALUES (%s)")
    dbCursor.executemany(label_query, label_data)

def add_genres(genre_data):
    genre_query = ("INSERT IGNORE INTO genres (name) VALUES (%s)")
    dbCursor.executemany(genre_query, genre_data)

def add_styles(style_data):
    style_query = ("INSERT IGNORE INTO styles (name) VALUES (%s)")
    dbCursor.executemany(style_query, style_data)

def add_releases(release_data): 
    release_query = ("INSERT INTO releases (title, date, format, artist_id, label_id) "
                "VALUES (%s, %s, %s, "
                "(SELECT artists.id FROM artists WHERE artists.name = %s), "
                "(SELECT labels.id FROM labels WHERE labels.name = %s)"
                ")")
    dbCursor.executemany(release_query, release_data)

def add_release_genres(release_genre_data):
    release_genre_query = ("INSERT INTO release_genre (genre_id, style_id, release_id) "
                      "VALUES ("
                      "(SELECT genres.id FROM genres WHERE name = %s), "
                      "(SELECT styles.id FROM styles WHERE name = %s), "
                      "(SELECT releases.id FROM releases JOIN artists WHERE releases.title = %s AND artists.name = %s AND releases.format = %s)"
                      ")")
    dbCursor.executemany(release_genre_query, release_genre_data)

## Establish connection to database and initialize cursor
dbConnector = mysql.connector.connect(user='user', password='CorrectHorseBatteryStaple', host='localhost')
dbCursor = dbConnector.cursor()
database = 'assignment3'
dbConnector.database = database

## Populate data lists for everything except RELEASES and RELEASE_GENRES 
## Execute functions for adding to database
artist_data = []            
label_data = []
genre_data = []
style_data = []

print("Beginning to parse data...")

for release in releases: 
    artist = release.getElementsByTagName("name")[0].childNodes[0].data
    artist_data.append((artist,))
    label = release.getElementsByTagName("name")[0].childNodes[0].data
    label_data.append((label,))
    genre = release.getElementsByTagName("genre")[0].childNodes[0].data
    genre_data.append((genre,))
    styles_list = release.getElementsByTagName("styles")
    if styles_list: 
        styles = styles_list[0].childNodes        
        for style in styles:
            style_data.append((style.childNodes[0].data,)) 

print("Finished parsing data for artist, label, genre, style. Inserting into database...")
add_artists(artist_data)
print("Artists done")
add_labels(label_data)
print("Labels done")
add_genres(genre_data)
print("Genres done")
add_styles(style_data)
print("Styles done")

## Populate data lists for RELEASES and execute function to add to database
release_data = []

for release in releases: 
    title = release.getElementsByTagName("title")[0].childNodes[0].data
    date = release.getElementsByTagName("released")
    if date: 
        date = date[0].childNodes[0].data
    else:
        date = None
    r_format = release.getElementsByTagName("format")[0].getAttribute("name")
    artist = release.getElementsByTagName("name")[0].childNodes[0].data
    label = release.getElementsByTagName("label")[0].getAttribute("name")
    if label == None:
        continue
    else:
        release_data.append((title, date, r_format, artist, label))

print("Finished parsing release data. Inserting into database...")
add_releases(release_data)
print("Releases done")


#print("Commiting changes. REMOVE THIS LATER!")
#dbConnector.commit()

# Populate data lists for RELEASE GENRE and execute function to add to database
release_genre_data = []

for release in releases:    
    genre = release.getElementsByTagName("genre")[0].childNodes[0].data
    title = release.getElementsByTagName("title")[0].childNodes[0].data
    artist = release.getElementsByTagName("name")[0].childNodes[0].data 
    r_format = release.getElementsByTagName("format")[0].getAttribute("name")
    styles_list = release.getElementsByTagName("styles")
    if styles_list: 
        styles = styles_list[0].childNodes        
        for style in styles:            
            release_genre_data.append((genre, style.childNodes[0].data, title, artist, r_format)) 
    else: 
        release_genre_data.append((genre, None, title, artist, r_format))       

print("Finished parsing release genres. Inserting into database...")
add_release_genres(release_genre_data)
print("Release genres done")

## Commit to database and close connections
print("Commiting changes to database and exiting...")
dbConnector.commit()
dbCursor.close()
dbConnector.close()
