import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def request_song_info(song_title, artist_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + 'UYc49IZCXtRp-1GIQ7LLeORJAslM1dUJa3w9fzwNh2FvShdXcbtwaXlgahYZFzVx'}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)

    return response
	
def get_result(song_title, artist_name):
    # Search for matches in the request response
	response = request_song_info(song_title,artist_name)
	json = response.json()
	remote_song_info = None

	for hit in json['response']['hits']:
		if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
			remote_song_info = hit
			return hit
			
			
def get_url_of_lyrics(response):
    return response['result']['url']
	

def get_lyrics_from_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics
	
def clean_lyrics(lyrics):
    ##deletes newline and punctuation, and returns everything lowercase
    return lyrics.replace("\n", ". ").lower()


def fill_happy_sad(lyr):
	sid = SentimentIntensityAnalyzer()
	ans = sid.polarity_scores(lyr)
	pos, neu, neg = ans["pos"], ans["neu"], ans["neg"]
	opp_neg = 1 - neg
	final = statistics.mean([pos, opp_neg])
	return pos, neu, neg, opp_neg, final
	
if __name__ == '__main__':
	result = get_result("skyfall", "adele")
	print(result)
	url = get_url_of_lyrics(result)
	print("url is "+ url)
	lyrics = get_lyrics_from_url(url)
	print(type(lyrics))
	new_lyrics = clean_lyrics(lyrics)
	print("new lyrics" +new_lyrics)
	a,b ,c,d,e = fill_happy_sad(new_lyrics)
	print(a)
	print(b)
	print(c)
	print(d)
	print(e)
