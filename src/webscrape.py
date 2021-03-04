import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_soup_by_genre(genre):
    if genre != "all music":
        url = f'http://www.popvortex.com/music/charts/new-{genre}-songs.php'
    else:
        url = 'http://www.popvortex.com/music/charts/top-new-songs.php'
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def get_artist_and_song(soup):
    ranking_list = []
    for i in range(1, 6):
        div = soup.find('div', id='chart-position-' + str(i))
        song_name = div.find('cite', class_='title').text
        artist = div.find('em', class_='artist').text
        ranking_list.append({"No": i, "Song Name": song_name, "Artist": artist})
    return ranking_list


def get_top5_dataframe(genre):
    soup = get_soup_by_genre(genre)
    df = pd.DataFrame.from_dict(get_artist_and_song(soup))
    return df

