#!/usr/bin/env python
import time
import json
import sys
import argparse
import tweepy
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

def get_followers(account, out_handle):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=50, retry_delay=30)
    ids = []
    try:
        for page in tweepy.Cursor(api.followers_ids, screen_name = account).pages():
            ids.extend(page)
        print(len(ids))

        #cannot marge following 3 lines or error cannot use + between dict and str
        input = json.dumps({"account":str(account,'utf-8'), "followers":ids})
        out_handle.write(bytes(input + "\n",'utf-8'))
    except tweepy.TweepError as err:
        print("\t\terror - %s" % err)

    #for i in range(16):
    #    print("\tpage -- %d" % i)
    #    try:
    #        tweets = api.user_timeline(screen_name = account, count=200, page=i,tweet_mode = "extended")
    #        if len(tweets) == 0:
    #            break
    #        print(len(tweets))
    #        for tweet in tweets:
    #            out_handle.write(bytes(json.dumps(tweet._json) + "\n",'utf-8'))
    #    except tweepy.error.tweeperror as err: 
    #        print("\t\terror - %s"  % err)
    #        break
    #    time.sleep(1)
        
    #print("\tpage -- %d" % 16)
    #try:
    #    tweets = api.user_timeline(screen_name = account, count=200, page=i,tweet_mode = "extended")

        
    #    for j in range (len(tweets)):
    #        out_handle.write(bytes(json.dumps(tweets[j]._json) + "\n",'utf-8'))
    #except tweepy.error.tweeperror as err: 
    #    print("\t\terror - %s"  % err)

    #time.sleep(1)





def main():
    args = parse_cmd()

    in_handle = open(args.input_filename, "rb")
    out_handle = open(args.output_filename, "wb")
    #in_handle = open("fox.txt", "rb")
    #out_handle = open("fox_out.json", "wb")
    account = in_handle.readline().strip()

    while account:
        print( "Scraping %s" % account)
        get_followers(account, out_handle)
        out_handle.flush()
        account = in_handle.readline().strip()
    in_handle.close()
    out_handle.close()

main()
