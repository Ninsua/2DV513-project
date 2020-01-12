from lxml.etree import iterparse
import mysql.connector

FILENAME = "discogs_20080309_releases.xml"
N_INSERTS = 10000
DB_USER = 'user'
DB_PASSWORD = 'CorrectHorseBatteryStaple'
DB_NAME = 'assignment3'

def perform_insert():        
    try: 
        artist_query = ("INSERT IGNORE INTO artists (name) VALUES (%s)")
        dbCursor.executemany(artist_query, artist_data)

        label_query = ("INSERT IGNORE INTO labels (name) VALUES (%s)")
        dbCursor.executemany(label_query, label_data)
        
        genre_query = ("INSERT IGNORE INTO genres (name) VALUES (%s)")
        dbCursor.executemany(genre_query, genre_data)
        
        style_query = ("INSERT IGNORE INTO styles (name) VALUES (%s)")
        dbCursor.executemany(style_query, style_data)

        dbConnector.commit()
        
        release_query = ("INSERT INTO releases (title, date, format, artist_id, label_id) "
                    "VALUES (%s, %s, %s, "
                    "(SELECT artists.id FROM artists WHERE artists.name = %s), "
                    "(SELECT labels.id FROM labels WHERE labels.name = %s)"
                    ")")
        
        release_genre_query = ("INSERT INTO release_genre (genre_id, style_id, release_id) "
                        "VALUES ("
                        "(SELECT genres.id FROM genres WHERE name = %s), "
                        "(SELECT styles.id FROM styles WHERE name = %s), "
                        "%s"
                        ")")
                
        for release in superlistan:            
            rdata = release[0]
            if rdata[3] == None: continue
            dbCursor.execute(release_query, rdata)            
            release_id = dbCursor.lastrowid
                        
            for style in release[1]:
                sdata = (style[0], style[1], release_id)                
                if release_id == 0: break
                dbCursor.execute(release_genre_query, sdata)
            
        dbConnector.commit()        
    
    except mysql.connector.Error as err:
        print(err)
    
    print("Inserted so far: ", counter)
    

def reset_lists():
    artist_data = []            
    label_data = []
    genre_data = []
    style_data = []    
    superlistan = []

artist_data = []            
label_data = []
genre_data = []
style_data = []
release_data = ()
release_genre_data = []
superlistan = []

counter = 0

dbConnector = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host='localhost')
dbCursor = dbConnector.cursor()
database = DB_NAME
dbConnector.database = database

for event, elem in iterparse(FILENAME):    
    if elem.tag == "release":
        counter += 1
        
        title = None
        date = None
        r_format = None
        artist = None
        label = None
        genre = None
        styles = []
        
        for e in elem.iter():            
            if e.tag == "genre":
                genre = e.text
                genre_data.append((e.text,))                
            if e.tag == "style":
                styles.append(e.text)
                style_data.append((e.text,))
            if e.tag == "title": title = e.text
            if e.tag == "released": date = e.text
            if e.tag == "format": r_format = e.attrib['name']
            if e.tag == "name":
                artist = e.text
                if artist != None:
                    artist_data.append((e.text,))
            if e.tag == "label":
                label = e.attrib['name']
                label_data.append((e.attrib['name'],))
                
        release_data = (title, date, r_format, artist, label)
        
        if len(styles) > 0:
            for style in styles:
                release_genre_data.append((genre, style)) 
        else:
            release_genre_data.append((genre, None))

        superlistan.append((release_data, release_genre_data))
        
        release_genre_data = []        

        if counter % N_INSERTS == 0:
            perform_insert()
            reset_lists()              

perform_insert()
dbConnector.commit()
dbConnector.close()
