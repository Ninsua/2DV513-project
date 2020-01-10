"Flask routes"

from flask import render_template
from app import app

def get_artist(id):
    return defsanity

def get_label(id):
    return willowtip

def get_release(id):
    return psalms

def get_releases_for_artist(id):
    releases_list = []
    releases_list.append(psalms)
    releases_list.append(chapters)
    releases_list.append(verses)
    releases_list.append(disposal_dharmata)
    return releases_list

def get_releases_for_labels(id):
    releases_list = []
    releases_list.append(chapters)
    releases_list.append(verses)
    releases_list.append(disposal_dharmata)
    return releases_list

artists = []
labels = []
releases = []
genres = []

laibach = {
    'name':'Laibach',
    'id':1
    }
defsanity = {
    'name':'Defeated Sanity',
    'id':2
}

willowtip = {
    'name':'Willowtip Records',
    'id':1
}

mute = {
    'name':'Mute Records',
    'id':2
}

psalms = {
    'title':'Psalms of the Moribund',
    'format':'CD',
    'release_date':'2000-00-00',
    'id':1,
    'label_id':1,
    'artist_id':2
}

chapters = {
    'title':'Chapters of Repugnance',
    'format':'CD',
    'release_date':'2000-00-00',
    'id':2,
    'label_id':1,
    'artist_id':2
}

verses = {
    'title':'Verses of deformity',
    'format':'CD',
    'release_date':'2000-00-00',
    'id':3,
    'label_id':1,
    'artist_id':2
}

disposal_dharmata = {
    'title':'Disposal of the dead/Dharmata',
    'format':'CD',
    'release_date':'2000-00-00',
    'id':4,
    'label_id':1,
    'artist_id':2
}

wat = {
    'title':'WAT',
    'format':'CD',
    'release_date':'2000-00-00',
    'id':10,
    'label_id':2,
    'artist_id':1
}

artists.append(laibach)
artists.append(defsanity)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Musica!', artists=artists)

@app.route('/artist/<artist_id>/')
def artist(artist_id):
    artist = get_artist(artist_id)
    artist_releases = get_releases_for_artist(artist_id)

    for release in artist_releases:
        release['label_name'] = get_label(release['label_id'])['name']

    return render_template('artist.html', artist=artist, artist_releases=artist_releases)

@app.route('/label/<label_id>/')
def label(label_id):
    label = get_label(label_id)
    label_releases = get_releases_for_labels(label_id)
    return render_template('label.html', label=label, label_releases=label_releases)

@app.route('/release/<release_id>/')
def release(release_id):
    release = get_release(release_id)
    return render_template('release.html', release=release)
