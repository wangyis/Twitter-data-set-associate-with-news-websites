#!/usr/bin/env python
import time
import json
import sys
import argparse
import tweepy
import csv
'''
consumer_key = INSERT_KEY_HERE
consumer_secret = INSERT_KEY_HERE
access_key = INSERT_KEY_HERE
access_secret = INSERT_KEY_HERE

'''

consumer_key = /*YOUR KEY*/
consumer_secret = /*YOUR KEY*/
access_key = /*YOUR KEY*/
access_secret = /*YOUR KEY*/

def parse_cmd():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="File of accounts to scrape one per line",
            required=True, dest="input_filename")
    parser.add_argument("-o", "--output", help="Where to write timelines",
            required=True, dest="output_filename")

    return parser.parse_args()

def get_tweets(account, out_handle):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=50, retry_delay=30)
    for i in range(16):
        print("\tPage -- %d" % i)
        try:
            tweets = api.user_timeline(screen_name = account, count=200, page=i, tweet_mode = "extended")
            if len(tweets) == 0:
                break
            print(len(tweets))
            for tweet in tweets:
                data = {"tweet_id":tweet.id_str}
                data["time_stamp"] = str(tweet.created_at)
                data["screen_name"] = str(tweet.user.screen_name)
                data["location"]=str(tweet.geo)
                data["text"]= str(tweet.full_text)
                
                if hasattr(tweet, "retweeted_status"):
                    data["retweeted_id"] = str(tweet.retweeted_status.id_str)
                else:
                    data["retweetd_id"] = "none"
                    
                if hasattr(tweet, "quoted_status"):
                    data["quoted_id"] = str(tweet.quoted_status.id_str)
                else:
                    data["quoted_id"] = "none"
                
                mentions = tweet.entities['user_mentions']
                data["mentions"] = []
                for mention in mentions:
                    data["mentions"].append(mention['screen_name'])
                    
                hashtags = tweet.entities['hashtags']
                data["hash_tags"] = []
                for hashtag in hashtags:
                    data["hash_tags"].append(hashtag['text'])
                 
                urls = tweet.entities['urls']
                data["urls"]= []
                for url in urls:
                    data["urls"].append(url["url"])
                
                data["media_urls"] = []
                if hasattr(tweet, "extended_entities"):
                    medias = tweet.entities['media']
                    for media in medias:
                        data["media_urls"].append(media['media_url'])
                        
                data["retweet_count"] = str(tweet.retweet_count)
                    
                input = json.dumps(data)
                out_handle.write(bytes(input + "\n", 'utf-8'))
                #out_handle.write(bytes(json.dumps(tweet._json) + ",\n",'UTF-8'))
        except tweepy.error.TweepError as err: 
            print("\t\tERROR - %s"  % err)
            break
        time.sleep(1)
    print("\tPage -- %d" % 1)
    #try:
    #    tweets = api.user_timeline(screen_name = account, count=200, page=i, tweet_mode="extended")

    #    j=0
    #    for j in range (len(tweets)):
    #        data = {"tweet_id":tweets[j].id_str}
    #        data["time_stamp"] = str(tweets[j].created_at)
    #        input = json.dumps(data)
    #        out_handle.write(bytes(input + "\n", 'utf-8'))
    #        #out_handle.write(bytes(json.dumps(tweets[j]._json) + "\n",'utf-8'))
    #except tweepy.error.TweepError as err: 
    #    print("\t\tERROR - %s"  % err)
    time.sleep(1)





def main():
    args = parse_cmd()

    in_handle = open(args.input_filename, "rb")
    out_handle = open(args.output_filename, "wb")
    account = in_handle.readline().strip()

    #while account:
    #    print( "Scraping %s" % account)
    #    get_tweets(account, out_handle)
    #    out_handle.flush()
    #    account = in_handle.readline().strip()
    #in_handle.close()
    #out_handle.close()
    #f=open(args.output_filename,'r')
    #origin=json.loads(f.read(),strict=False)
    #with open("tweet.csv",'a+') as ff:
    #    csv_write=csv.writer(f)
    #    csv_head=["tweet_id","time_stamp","screen_name","location","text","mentions","hash_tags","urls"]
    #    csv_write.writerow(csv_head)
    #for obj in origin:
    #    csv_write.wirterow([obj["id"],obj["created_at"],obj["user"]["screen_name"],obj["user"]["location"],obj["text"],obj["entities"]["user_mentions"],obj["entities"]["hastags"],obj["entities"]["urls"]])
    while account:
        print( "Scraping %s" % account)
        get_tweets(account, out_handle)
        out_handle.flush()
        account = in_handle.readline().strip()
    in_handle.close()
    out_handle.close()



main()
