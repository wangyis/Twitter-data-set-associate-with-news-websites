# Twitter-data-set-associate-with-news-websites
We built a data set containing data from Twitter associate with major news websites for further study such as opinion formation and echo chamber. We also uploaded the data to Google Cloud Platform (GCP)) and keep the dataset up to date. The repo contains the data we collected as well as the source code for Twitter data extracting and web-scraping.

# Prerequisites
Apply a Twitter developer account for getting data from Twitter. \
Use pyhon3 to run the python code.\
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
