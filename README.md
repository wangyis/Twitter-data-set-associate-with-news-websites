# Twitter-data-set-associate-with-news-websites
We built a data set containing data from Twitter associate with major news websites for further study such as opinion formation and echo chamber. We also uploaded the data to Google Cloud Platform (GCP)) and keep the dataset up to date. The repo contains the data we collected as well as the source code for Twitter data extracting and web-scraping.

# Prerequisites
Apply a Twitter developer account for getting data from Twitter. \
Use pyhon3 to run the python code.\
Packages needed for extracting Twitter data: (Please refer to social_property_based_media_data_set_creation.pdf in folder Twitter-data-set for more details)
- tweepy

Packages needed for web-scraping: (Please refer to Amy Pandit - report for news website Web-scraping .pdf in folder news-website-web-scraping for more details)
- Selenium
- BeautifulSoup4
- Re
- Html2Text
- Sqlite3
- Google.cloud
- articleDateExtractor

# Extract data from Twitter
Run following command to get tweets from target accounts:
```
python get_tw.py -i <input file> -o <output file>
```
Input file should contain the list of usernames of Twitter accounts that we want to get tweets from. And the output would contain detailed json-formed tweets data including the following columns: (Please refer to social_property_based_media_data_set_creation.pdf in folder Twitter-data-set for more details)
- tweet_id
- time_stamp
- screen_name
- location
- text
- retweeted_id
- quoted_id
- mentions
- hash_tags
- urls
- media_urls
- retweet_acount

Run following command to get follower imformation from target accounts:
```
python followers.py -i <input file> -o <output file>
```
Input file should contain the list of usernames of Twitter accounts that we want to get followers information from. And the output file will contain the json-formed information for all Twitter users who are following the target accounts with the form of following columns: (Please refer to social_property_based_media_data_set_creation.pdf in folder Twitter-data-set for more details)
- screen_name
- followers

We found target accounts by scanning through political panel of FOX news and political panel of CNN news, collecting the author of each news report. The 
process of finding target accounts would be automated after the web-scrapping code being able to detect and collect the authors' Twitter links.

The cnn.txt contains the list of target accounts whose owners work in CNN. cnn_out.json contains the follower information of CNN target accounts. cnn_twitter_out.json contains the tweets information of CNN target accounts.

The fox.txt contains the list of target accounts whose owners work in FOX. fox_out.json contains the follower information of FOX target accounts. fox_twitter_out.json contains the tweets information of FOX target accounts.

We then uploaded the data into the Google Cloud Platform(GCP). We used Bigquery to store the json data, and use Compute Engine to run upload.sh on a regular basis to update the dataset in Bigquery. 

# Extract data from news websites

We also wrote code for web-scraping and the Twitter handle detection in FOX and CNN news websites. 

extration.py contains all the code for extraction from news websites and saving to the database. This could potentially be split up into multiple files in the future for easier testing, scaling, and readability.

run the extraction.py using the command:
```
python extraction.py
```

dumpdata.py contains important code that is commented out -- it is used for opening sqlite and saving the extracted data to article_dump.csv. This could’ve also been put in a bash script. There is also a Google Cloud function declared with some usage also written in a main(), but it wasn’t
used because of the issues with debugging Google Cloud. They could be tested in the future and used for automation, in addition to the sqlite code.

Each row of scrapped data contains the following columns: (Please refer to Amy Pandit - report for news website Web-scraping .pdf in folder news-website-web-scraping for more details)
- article_link
- article_date
- author_name
- aurthor_handle
- site
- article_title
- category
- text_preview

We also uploaded the data manually to GCP and the process getting data & upload can be automated in the future work. 
