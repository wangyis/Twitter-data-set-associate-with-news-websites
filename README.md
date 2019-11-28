# Twitter-data-set-associate-with-news-websites
We built a data set containing data from Twitter associate with major news websites for further study such as opinion formation and echo chamber. We also uploaded the data to Google Cloud Platform (GCP)) and keep the dataset up to date. The repo contains the data we collected as well as the source code for Twitter data extracting and web-scraping.

# Prerequisites
The environment for running the code is python3.\
Packages needed for extracting Twitter data: (Read social_property_based_media_data_set_creation.pdf in folder Twitter-data-set for more details)
- tweepy

Packages needed for web-scraping: (Read report in folder news-website-web-scraping for more details)
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
Input file should contain the list of usernames of Twitter accounts that we want to get tweets from. And the output would contain detailed json-formed tweets data including: (Please refer to social_property_based_media_data_set_creation.pdf in folder Twitter-data-set for more details)
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
Input file should contain the list of usernames of Twitter accounts that we want to get followers information from. And the output file will contain the unique ids for all Twitter users who are following the target accounts.

# Extract data from news websites
