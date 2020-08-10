# TopSongsDuringCoronaTime
This project is part of our top corona songs analysis project of the course **Topics in Digital Humanities** Spring/2020

## Used API's
- Lyric Genius API
- NLTK Sentiment Analysis Algorithm which uses **http://mymemory.translated.net/api** to translate non eng text to eng.
- corona API using **https://api.thevirustracker.com/**
- Spotify API

## Main Functions
| **Fucntion Name** |
| - |
| corona_stats_by_country() |
| - |
| get_list_of_all_songs(by_country) |
| - |
| analysis_songs_by_country_monthly(by_country) |
| - |
| analysis_songs_by_country_monthly_divided_to_weekly(by_country) |
| - |
| all_analysis() |

During our research we used 'Lyric Genius' API to get the lyrics of each song, NLTK Sentiment Analysis Algorithm in its multi-lingual form in order to analyze the sentiments out of the songs' lyrics, corona API for getting the data about cases and deaths for each week, Plot.ly for chart generating and Datawrapper.de for the world map displayed on Home page, and last but not leased we used Spotify API to get the top 20 songs of each country every week. We organized the data in multiple CSV documents, and generated sentiment values for each song. From the CSV we've created the graphs and charts seen on the website along with the world map on the Home page.
