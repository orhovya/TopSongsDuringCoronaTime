import requests
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
import json
from datetime import timedelta
import datetime
import lyricsgenius
genius = lyricsgenius.Genius("UYc49IZCXtRp-1GIQ7LLeORJAslM1dUJa3w9fzwNh2FvShdXcbtwaXlgahYZFzVx")
import csv
ANALYSIS_ALL_SONGS = {}

LIST_OF_COUNTRIES ={ 
	"it":"Italy",
	"us":"United states",
	"gb":"United kingdom",
	"ar":"Argentina",
	"bg":"Bulgaria",
	"br":"Brazil",
	"co":"Colombia",
	"de":"Germany",
	"es":"Spain",
	"fr":"France",
	"gt":"Guatemala",
	"ee":"Estonia",
	"in":"India",
	"jp":"Japan",
	"mx":"Mexico",
	"pa":"Panama",
	"th":"Thailand",
	"za":"South afrika",
	"vn":"Vietnam",
	"il":"Israel",
	#"hk":"China",}
	"cn":"China"}

START_DATE_SONGS = '2019-11-29'
END_DATE_SONGS = '2020-05-01'

START_DATE_CORONA = '2020-01-31'
END_DATE_CORONA = '2020-05-15'


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
	lyrics = html.find('div', class_='lyrics')
	if lyrics:
		try:
			lyrics = lyrics.get_txt()
		except:
			return None
	else:
		return None
	

# ---------------------------------------   Analysis Algorithem   --------------------------------------------------

def fill_happy_sad(lyr):
	"""
	Function that Runs the SentimentIntensityAnalyzer on the lyrics of a specific song.
	Args:
		lyr(str): Givven lyrics to analysis.
	Return:
		Return the algorithems analysis Positive,Negative,Neutral of those lyrics.
	"""
	sid = SentimentIntensityAnalyzer()
	ans = sid.polarity_scores(lyr)
	pos, neu, neg = ans["pos"], ans["neu"], ans["neg"]
	print("Overall sentiment dictionary is : ", ans) 
	print("sentence was rated as ", neg*100, "% Negative") 
	print("sentence was rated as ", neu*100, "% Neutral") 
	print("sentence was rated as ", pos*100, "% Positive") 	
	if ans['compound'] >= 0.05 : 
		return "Positive" 
	elif ans['compound'] <= - 0.05 : 
		return "Negative"
	else : 
		return "Neutral"
		
# ---------------------------------------   Analysis Algorithem   --------------------------------------------------
	
def top_songs_spotify_request(country,start_date,end_date):
	"""
	Function that connects the the api and return html of track table.
	Args:
		country(str): Country which we run on.
		start_date(str): the start date of the week.
		end_date(str): the end date of this week.
	Return:
		List of htmls of songs.
	"""
	response = requests.request("GET",f"https://spotifycharts.com/regional/{country}/weekly/{start_date}--{end_date}")
	html_file = BeautifulSoup(response.text, "html.parser")
	return html_file.find_all('td', attrs={'class':'chart-table-track'})

def search_song_in_list(song,list_of_songs):
	print("song in search")
	print(song)
	for song_in_list in list_of_songs:
		print("song in list")
		print(song_in_list)
		if song_in_list['song_name']== song['song_name']:
			return True
	return False
	
def top_songs_monthly_of_country(country,start_month,end_month):
	start_curr_week =  datetime.datetime.strptime(start_month,'%Y-%m-%d')
	end_curr_week = (start_curr_week + timedelta(days=7)).strftime('%Y-%m-%d')
	start_curr_week = start_curr_week.strftime('%Y-%m-%d')
	list_of_songs = []
	while(start_curr_week < end_month):
		new_weekly_songs = []
		new_weekly_songs = list_songs_of_week = top_song_by_dates_of_county_spotify(country,start_curr_week,end_curr_week)
		#list_songs_of_week = top_song_by_dates_of_county_spotify(country,start_curr_week,end_curr_week)
		#for song in list_songs_of_week:
		#	is_in_list = search_song_in_list(song,list_of_songs)
		#	if not is_in_list:
		#		new_weekly_songs.append(song)
		list_after_analysis = run_analysis_on_songs(new_weekly_songs)
		list_of_songs.extend(list_after_analysis)
		#print("list_of songs")
		#print(list_of_songs)

		start_curr_week =  datetime.datetime.strptime(end_curr_week,'%Y-%m-%d')
		end_curr_week = (start_curr_week + timedelta(days=7)).strftime('%Y-%m-%d')
		start_curr_week = start_curr_week.strftime('%Y-%m-%d')
	print("list monthly")
	print(list_of_songs)
	return list_of_songs
	
def top_song_by_dates_of_county_spotify(country,start_date,end_date):
	"""
	Function the connects to api and from html result parses the name of the song and the artist of the song.
	Args:
		country(str): Country which we run on.
		start_date(str): the start date of the week.
		end_date(str): the end date of this week.
	Return:
		A list of Dict when each dict had data regarding a specific song.
	"""
	# the required format for dates =2020-04-10
	print(start_date)
	print(end_date)
	songs_list_html = top_songs_spotify_request(country,start_date,end_date)
	print(songs_list_html)
	list_songs_by_country_and_time = []
	for i in range(0,20):
		dict = {}
		song_name_html =  str(songs_list_html[i].find('strong'))
		song_name_html = re.sub('</strong>', '', song_name_html)
		song_name = re.sub('<strong>', '', song_name_html)
		dict['song_name'] = song_name
		song_artist_html = str(songs_list_html[i].find('span'))
		song_artist_html = re.sub('</span>', '',song_artist_html)
		song_artist = re.sub('<span>', '',song_artist_html)
		song_artist = re.sub('by ','',song_artist)
		dict['song_artist'] = song_artist
		dict['track number'] = i+1
		dict['country'] =  LIST_OF_COUNTRIES[country]
		dict['start date'] =  start_date
		dict['end date'] = end_date
		list_songs_by_country_and_time.append(dict)
	return list_songs_by_country_and_time
		
		
def get_list_of_all_songs(country):
	"""
	Function which creates json files which contain the data of the songs of a specific country from START_DATE_SONGS until END_DATE_SONGS
	Args:
		country(str):Country which we run on.
	Return:
		A json file for each week which contain the week data and the songs data by rank.
	"""
	start_date_curr =  datetime.datetime.strptime(START_DATE_SONGS,'%Y-%m-%d')
	end_date_curr = (start_date_curr + timedelta(days=28)).strftime('%Y-%m-%d')
	end_date = datetime.datetime.strptime(END_DATE_SONGS,'%Y-%m-%d')
	while(start_date_curr< end_date):
		start_date_curr = start_date_curr.strftime('%Y-%m-%d')
		print(start_date_curr)
		print(end_date_curr)
		list_songs = top_songs_monthly_of_country(country,start_date_curr,end_date_curr)
		print(list_songs)
		# json files
		#with open(f'songs_{country}_{start_date_curr}_{end_date_curr}', 'w') as fout:
		#	fout.write(json.dumps(list_after_analysis, indent=4))
		with open(f'songs_{LIST_OF_COUNTRIES[country]}_{start_date_curr}_{end_date_curr}.csv', 'w', encoding='utf8', newline='') as output_file:
			fc = csv.DictWriter(output_file, fieldnames=list_songs[0].keys(),)
			fc.writeheader()
			fc.writerows(list_songs)	
		start_date_curr =  datetime.datetime.strptime(end_date_curr,'%Y-%m-%d')
		end_date_curr = (start_date_curr + timedelta(days=28)).strftime('%Y-%m-%d')
		print(start_date_curr)
		print(end_date_curr)


	
	
# ---------------------------------------   Analysis of Song   --------------------------------------------------

def get_lyrics_of_song(song_name,song_artist):
	"""
	Function that when a givven name of a song and artist name, tries using genius api to get the lyrics of the specific song.
	Args:
		song_name(str):Name of the song.
		song_artist(str): Name of the artist that sings the song.
	Return:
		String which is the lyrics of the specific song, None if the lyrics were not found.
	"""
	print("in analysis")
	print(song_name)
	print(song_artist)
	lyrics = None
	url = None
	try_var = 0
	while lyrics==None and try_var<5:
		try:
			#result = get_result(song_name,song_artist)
			#if result:
			#	url = get_url_of_lyrics(result)
			#	print("url is "+ url)
			#	lyrics = get_lyrics_from_url(url)
			song  = genius.search_song(song_name,song_artist)
			url = song.url
			if song!=None:
				lyrics = song.lyrics
			try_var +=1
		except:
			try_var +=1
			continue
	return lyrics,url

def clean_lyrics(lyrics):
    ##deletes newline and punctuation, and returns everything lowercase
    return lyrics.replace("\n", ". ").lower()

def run_analysis_on_songs(list_of_dict_of_songs):
	"""
	Function that runs the algorithem on each song of the list of songs and adds Analysis key to its dict which is set to what the algo returned.
	Args:
		list_of_dict_of_songs(list): A list of dictionaries when each dictionary has song_name,song_artist,song_rank,start_date,end_date
	Return:
		String which represents Positive,Neutral,Negative according to max of songs of that kind.
	"""
	i=0
	for songs in list_of_dict_of_songs:
		print("song_name "+ songs['song_name'])
		print("song_artist "+ songs['song_artist'])
		if songs['song_name'] in ANALYSIS_ALL_SONGS:
			songs['Analysis'],songs['Lyrics'] = ANALYSIS_ALL_SONGS[songs['song_name']]
			list_of_dict_of_songs[i] = songs
			i =i+1
			#print("song already in analysis list")
			#print(ANALYSIS_ALL_SONGS)
			print(songs['Lyrics'])
			continue
		lyrics, url = get_lyrics_of_song(songs['song_name'],songs['song_artist'])
		analysis = ''
		if lyrics:
			new_lyrics = clean_lyrics(lyrics)
			analysis = fill_happy_sad(new_lyrics)
		if analysis:
			songs['Analysis'] = analysis
			songs['Lyrics'] = url
		else:
			songs['Analysis'] = "could not determine analysis"
			songs['Lyrics'] = url
		ANALYSIS_ALL_SONGS[songs['song_name']] = (songs['Analysis'],songs['Lyrics'])
		print(songs['Lyrics'])
		list_of_dict_of_songs[i] = songs
		#print(songs)
		i =i+1
	return list_of_dict_of_songs
#		result = get_result(songs['song_name'],songs['song_artist'])
#		if result:
#			url = get_url_of_lyrics(result)
#			print("url is "+ url)
#			lyrics = get_lyrics_from_url(url)
#			if lyrics:
#				new_lyrics = clean_lyrics(lyrics)
#				print("new lyrics" +new_lyrics)
#				fill_happy_sad(new_lyrics)
			
def analysis_of_a_month_in_country(country,start_date,end_date):
	"""
	Function that returns an analysis of a country from start_date until end_date after which is a specific week.
	We count the number of Positive,Negative,Neutral analysis for each song on that week and return the one that appeared the most.
	Args:
		country(str): A country which we check.
		start_date(str): Begining of a week date.
		end_date(Str): End of the week.
	Return:
		String which represents Positive,Neutral,Negative according to max of songs of that kind.
	"""
	json_analysis = []
	with open(f'songs_{LIST_OF_COUNTRIES[country]}_{start_date}_{end_date}.csv', 'r', encoding="utf8") as fin:
		reader = csv.reader(fin)
		headers = next(reader)
		for row in reader:
			mydict = {}
			for i in range(0,len(headers)):
				mydict.update({headers[i]:row[i]})
			#print(mydict)
			json_analysis.append(mydict)
		#json_analysis = json.load(fin)	
	number_positive= 0
	number_negative =0
	number_neutral = 0
	for song in json_analysis:
		if song['Analysis'] == "Negative":
			number_negative =number_negative + 1
		if song['Analysis'] == "Positive":
			number_positive= number_positive + 1
		if song['Analysis'] == "Neutral":
			number_neutral = number_neutral + 1
	return number_positive , number_negative, number_neutral

def analysis_corona_monthly_count(country,start_date):
	corona_stat_all = []
	corona_monthly = []
	with open(f'corona_stats_{LIST_OF_COUNTRIES[country]}.csv', 'r', encoding="utf8") as fin:
		reader = csv.reader(fin)
		headers = next(reader)
		for row in reader:
			mydict = {}
			for i in range(0,len(headers)):
				mydict.update({headers[i]:row[i]})
			print(mydict)
			corona_stat_all.append(mydict)
	i = 0
	for corona in corona_stat_all:
		print(corona)
		if corona['Start Date'] == start_date:
			total_cases_per_month = corona_stat_all[i+3]['Total Cases']
			print(total_cases_per_month)
			return total_cases_per_month
		i = i+1
		
def analysis_songs_by_country_monthly(country):
	"""
	Function that creates a list of all analysis of a country from START_DATE until END_DATE_SONGS after the algorithem ran.
	Args:
		country(str): A country which we check.
	Return:
		Saves for a given country the analysis for each week from START_DATE until END_DATE_SONGS
	"""
	start_date_curr =  datetime.datetime.strptime(START_DATE_SONGS,'%Y-%m-%d')
	end_date_curr = (start_date_curr + timedelta(days=28)).strftime('%Y-%m-%d')
	end_date = datetime.datetime.strptime(END_DATE_SONGS,'%Y-%m-%d')
	analysis_country = []
	while(start_date_curr< end_date):
		start_date_curr = start_date_curr.strftime('%Y-%m-%d')
		analysis_week = {}
		positive, negative, neutral = analysis_of_a_month_in_country(country,start_date_curr,end_date_curr)
		analysis_week['Number of Positive']= positive
		analysis_week['Number of Negative']= negative
		analysis_week['Number of Neutral'] = neutral
		analysis_week['Start Date']= start_date_curr
		analysis_week['End Date'] = end_date_curr
		analysis_week['Total cases'] = analysis_corona_monthly_count(country,start_date_curr)
		analysis_country.append(analysis_week)
		start_date_curr =  datetime.datetime.strptime(end_date_curr,'%Y-%m-%d')
		end_date_curr = (start_date_curr + timedelta(days=28)).strftime('%Y-%m-%d')
	with open(f'total_analysis_{LIST_OF_COUNTRIES[country]}.csv', 'w', encoding='utf8', newline='') as output_file:
			fc = csv.DictWriter(output_file, fieldnames=analysis_country[0].keys(),)
			fc.writeheader()
			fc.writerows(analysis_country)	
	#with open(f'analysis_{country}', 'w') as fout:
	#	fout.write(json.dumps(analysis_country, indent=4))
	
	
	
# ---------------------------------------   Corona stats   --------------------------------------------------

def corona_stats_request(country):
	"""
	Function that communicates with the api of Corona.
	Args:
		country(str): A country which we check.
	Return:
		A dict of Stats about the country for each day.
	"""
	response = requests.request("GET",f"https://api.thevirustracker.com/free-api?countryTimeline={country}")
	result = response.json()
	corona_stat = result.get('timelineitems',[])
	corona_stat = corona_stat[0] # dict
	return corona_stat
	
	
def corona_stats_by_country(country):
	"""
	Function that calculates the stat of corona in a specific country.
	Args:
		country(str): A country which we check.
	Return:
		Saves for each country a file with all stats
	"""
	list_corona_stat = []
	corona_stat = corona_stats_request(country)
	end_date = datetime.datetime.strptime(END_DATE_CORONA,'%Y-%m-%d')
	start_date_curr =  datetime.datetime.strptime(START_DATE_SONGS,'%Y-%m-%d')
	while(start_date_curr < end_date):
		corona_stats_week = corona_stats_by_week(corona_stat, start_date_curr)
		list_corona_stat.append(corona_stats_week)
		start_date_curr = (start_date_curr + timedelta(days=7))
	with open(f'corona_stats_{LIST_OF_COUNTRIES[country]}.csv', 'w', encoding='utf8', newline='') as output_file:
		fc = csv.DictWriter(output_file, fieldnames=list_corona_stat[0].keys(),)
		fc.writeheader()
		fc.writerows(list_corona_stat)
		#fout.write(json.dumps(list_corona_stat, indent=4))
	
	
def corona_stats_by_week(stats,start_date_datetime):
	"""
	Function that calculated the number of deaths and number of new cases on a specific week when givven a dict of all stats
	Args:
		stats(dict): a dict that the key is date and the value is a dict of stats that returned from coronasite indicating the numbers of corona.
		start_date_datetime(datetime): the start date of the week.
	Return:
		Dict of stats for the week that starts on the start_date_datetime value
	"""

	date_curr = start_date_datetime.strftime('%m/%d/%y')
	if date_curr[0] == '0':
		date_curr = date_curr[1:]
	new_cases = 0
	new_deaths = 0
	total_cases = 0
	total_deaths = 0
	corona_stats_week = {}
	for i in range(1,7):
		print("\n")
		print(stats)
		print(date_curr)
		try:
			stat_curr = stats[date_curr]
			new_cases = new_cases + stat_curr['new_daily_cases']
			new_deaths = new_deaths + stat_curr['new_daily_deaths']
			total_cases = stat_curr['total_cases']
			total_deaths = stat_curr['total_deaths']
			date_curr =  datetime.datetime.strptime(date_curr,'%m/%d/%y')
			date_curr = (date_curr + timedelta(days=1)).strftime('%m/%d/%y')
			if date_curr[0] == '0':
				date_curr = date_curr[1:]
		except:
			date_curr =  datetime.datetime.strptime(date_curr,'%m/%d/%y')
			date_curr = (date_curr + timedelta(days=1)).strftime('%m/%d/%y')
			if date_curr[0] == '0':
				date_curr = date_curr[1:]
			continue
	start_date = start_date_datetime.strftime('%Y-%m-%d')
	end_date = 	datetime.datetime.strptime(date_curr,'%m/%d/%y')
	end_date = end_date.strftime('%Y-%m-%d')
	corona_stats_week["Start Date"] = start_date
	corona_stats_week["End Date"] = end_date
	corona_stats_week["New cases"] = new_cases
	corona_stats_week["New Deaths"] = new_deaths
	corona_stats_week["Total Cases"] = total_cases
	corona_stats_week["Total Deaths"] = total_deaths
	return corona_stats_week

def all_analysis():
	all_countries = []
	country_analysis = []
	for country in LIST_OF_COUNTRIES.keys():
		country_analysis = []
		country_dict = {}
		with open(f'total_analysis_{LIST_OF_COUNTRIES[country]}.csv', 'r', encoding="utf8") as fin:
			reader = csv.reader(fin)
			headers = next(reader)
			for row in reader:
				mydict = {}
				for i in range(0,len(headers)):
					mydict.update({headers[i]:row[i]})
				country_analysis.append(mydict)
		number_positive = 0
		number_negative = 0
		number_neutral = 0
		for analysis in country_analysis:
			number_negative =number_negative + int(analysis['Negative'])
			number_positive= number_positive + int(analysis['Positive'])
			number_neutral = number_neutral + int(analysis['Neutral'])
		#sum_analysis = max([number_positive,number_negative,number_negative])
		#if number_negative == sum_analysis:
		#	analysis =  "Negative"
		#if number_neutral == sum_analysis:
		#	analysis =  "Neutral"
		#if number_positive == sum_analysis:
		#	analysis =  "Positive"
		country_dict['Country Name'] = LIST_OF_COUNTRIES[country]
		country_dict['Num of Positive Month Songs'] = number_positive
		country_dict['Num of Negative Month Songs'] = number_negative
		country_dict['Num of Neutral Month Songs'] = number_neutral
		country_dict['Total cases'] =  country_analysis[23]['Total cases']
		all_countries.append(country_dict)
	with open(f'all_countries.csv', 'w', encoding='utf8', newline='') as output_file:
		fc = csv.DictWriter(output_file, fieldnames=all_countries[0].keys(),)
		fc.writeheader()
		fc.writerows(all_countries)
		
		
		
# --------------------------------------------- weekly analysis ------------------------------------------		
def analysis_songs_by_country_monthly_divided_to_weekly(country):
	start_date_curr =  datetime.datetime.strptime(START_DATE_SONGS,'%Y-%m-%d')
	end_date_curr = (start_date_curr + timedelta(days=28)).strftime('%Y-%m-%d')
	end_date = datetime.datetime.strptime(END_DATE_SONGS,'%Y-%m-%d')
	analysis_country = []
	while(start_date_curr< end_date):
		start_date_curr = start_date_curr.strftime('%Y-%m-%d')
		analysis_week = {}
		curr_month_by_weekly_analysis= analysis_of_a_month_by_weekly_in_country(country,start_date_curr,end_date_curr)
		print(curr_month_by_weekly_analysis)
		analysis_country.extend(curr_month_by_weekly_analysis)
		start_date_curr =  datetime.datetime.strptime(end_date_curr,'%Y-%m-%d')
		end_date_curr = (start_date_curr + timedelta(days=28)).strftime('%Y-%m-%d')
	print(analysis_country)
	with open(f'total_analysis_{LIST_OF_COUNTRIES[country]}.csv', 'w', encoding='utf8', newline='') as output_file:
			fc = csv.DictWriter(output_file, fieldnames=analysis_country[0].keys(),)
			fc.writeheader()
			fc.writerows(analysis_country)	
	#with open(f'analysis_{country}', 'w') as fout:
	#	fout.write(json.dumps(analysis_country, indent=4))

def analysis_of_a_month_by_weekly_in_country(country,start_month,end_month):
	json_analysis = []
	with open(f'songs_{LIST_OF_COUNTRIES[country]}_{start_month}_{end_month}.csv', 'r', encoding="utf8") as fin:
		reader = csv.reader(fin)
		headers = next(reader)
		for row in reader:
			mydict = {}
			for i in range(0,len(headers)):
				mydict.update({headers[i]:row[i]})
			#print(mydict)
			json_analysis.append(mydict)
		#json_analysis = json.load(fin)	
	start_curr_week =  datetime.datetime.strptime(start_month,'%Y-%m-%d')
	end_curr_week = (start_curr_week + timedelta(days=7)).strftime('%Y-%m-%d')
	start_curr_week = start_curr_week.strftime('%Y-%m-%d')
	monthly_analysis = []
	while(start_curr_week < end_month):
		weekly_analysis = list_songs_of_week = analysis_of_a_weekly_in_country(country,json_analysis,start_curr_week,end_curr_week)
		monthly_analysis.append(weekly_analysis)
		start_curr_week =  datetime.datetime.strptime(end_curr_week,'%Y-%m-%d')
		end_curr_week = (start_curr_week + timedelta(days=7)).strftime('%Y-%m-%d')
		start_curr_week = start_curr_week.strftime('%Y-%m-%d')
	return monthly_analysis

def analysis_of_a_weekly_in_country(country,list_of_songs,start_date,end_date):
	number_positive= 0
	number_negative =0
	number_neutral = 0
	analysis_week_dict = {}
	for song in list_of_songs:
		if song['start date'] == start_date:
			if song['Analysis'] == "Negative":
				number_negative =number_negative + 1
			if song['Analysis'] == "Positive":
				number_positive= number_positive + 1
			if song['Analysis'] == "Neutral":
				number_neutral = number_neutral + 1
	analysis_week_dict['Negative'] = number_negative
	analysis_week_dict['Positive'] = number_positive
	analysis_week_dict['Neutral'] = number_neutral
	analysis_week_dict['Start Date'] = start_date
	analysis_week_dict['End Date'] = end_date
	analysis_week_dict['Total cases'] = analysis_corona_weekly_count(country,start_date)
	return analysis_week_dict
	
def analysis_corona_weekly_count(country,start_date):
	corona_stat_all = []
	corona_monthly = []
	with open(f'corona_stats_{LIST_OF_COUNTRIES[country]}.csv', 'r', encoding="utf8") as fin:
		reader = csv.reader(fin)
		headers = next(reader)
		for row in reader:
			mydict = {}
			for i in range(0,len(headers)):
				mydict.update({headers[i]:row[i]})
			print(mydict)
			corona_stat_all.append(mydict)
	i = 0
	for corona in corona_stat_all:
		if corona['Start Date'] == start_date:
			total_cases_per_week = corona_stat_all[i]['Total Cases']
			print(total_cases_per_week)
			return total_cases_per_week
		i = i+1

if __name__ == '__main__':
	#save all songs of all countries to json files
	#for key in LIST_OF_COUNTRIES.keys():
	#	corona_stats_by_country(key)
	#for key in LIST_OF_COUNTRIES.keys():
	#	get_list_of_all_songs(key)
	#get_list_of_all_songs('hk')
	#for key in LIST_OF_COUNTRIES.keys():
	#	analysis_songs_by_country_monthly(key)
	#for key in LIST_OF_COUNTRIES.keys():
	#	analysis_songs_by_country_monthly_divided_to_weekly(key)
	#corona_stats_by_country('cn')
	#analysis_songs_by_country_monthly('cn')
	all_analysis()

	
	
	
