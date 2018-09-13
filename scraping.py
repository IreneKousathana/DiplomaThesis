import tweepy
from tweepy import OAuthHandler
import json
import config
import time
import random
import pymysql

from datetime import datetime
import os
import sys
from data_cleaning import isEnglish



WORLD_WOE_ID = 1
US_WOE_ID = 23424977
# conn = sqlite3.connect('tweets.db')
# c = conn.cursor()
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='meacrouwro', db='tweet_data', autocommit = True)
conn.set_charset('utf8mb4')
c = conn.cursor()
c.execute('SET NAMES utf8mb4;')
c.execute('SET CHARACTER SET utf8mb4;')
c.execute('SET character_set_connection=utf8mb4;')




class Tweet():

    def __init__(self, id, text, loc, name, date, hashtags, user_mentions ):
        self.id = id
        self.text = text
        self.location = loc
        self.name = name
        self.date = date#datetime.strptime(date, '%a %b %d %H:%M:%S %z %Y')
        self.hashtags = hashtags
        self.mentions = user_mentions

    def insertTweet(self):
        c.execute("INSERT INTO `data` (`id`, `username`, `text`, `time`, `location`, `hashtags`, `user_mentions` )"
                  " VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  (self.id, self.name, self.text, self.date, self.location, self.hashtags, self.mentions))
        conn.commit()


def load_api():
    ''' Function that loads the twitter API after authorizing the user. '''

    consumer_key = config.consumer_key
    consumer_secret = config.consumer_secret
    access_token = config.access_token
    access_secret = config.access_secret
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    # load the twitter API via tweepy
    return tweepy.API(auth)


def get_trends(api):
    ''' Function that returns the instersection of the current twitter trends of
    specific geocode and worldwide trends '''

    trends = api.trends_place(WORLD_WOE_ID)
    trends = list([trend['name'] for trend in trends[0]['trends']])
    en_trends = []
    for trend in trends:
        if isEnglish(trend):
            en_trends.append(trend)
    return en_trends[:10]





class MyStreamListener(tweepy.StreamListener):
    #tweetCounter = 0
    def __init__(self,  time_limit = 3600, count_limit=6000 ):
        super(MyStreamListener, self).__init__()
        self.start_time = time.time()
        self.limit = time_limit
        self.count = 0
        self.count_limit = count_limit



    def on_status(self, status):
        try:
            #exclude tweets that are retweets
            if status.retweeted or 'RT @' in status.text or status.lang != 'en' or status.in_reply_to_status_id is not None:
                return
            self.count = self.count + 1
            if status.truncated:
                text = status.extended_tweet['full_text']
            else:
                text = status.text
            entities = status.entities
            hashtags = []
            user_mentions = []
            for tag in entities['hashtags']:
                hashtags.append(tag['text'])
            hashtags = ','.join(hashtags)
            for mention in entities['user_mentions']:
                user_mentions.append(mention['name'])
            user_mentions = ','.join(user_mentions)
            tweet_data = Tweet(
                status.id_str,
                text,
                status.user.location,
                status.user.screen_name,
                status.created_at,
                hashtags,
                user_mentions

                #self.trend_id
            )

            #save in database
            tweet_data.insertTweet()
            print("success")

            if (time.time() - self.start_time) < self.limit :
                return  True
            else:

                return False


        except BaseException as e:
            print("Error on_data:", str(e))
            return True

    def on_error(self, status_code):
        if status_code == 420:
            print("In error")# returning False in on_data disconnects the stream
            return False



def main():

    #authorize and load the twitter API
    api = load_api()
    #search variables:
    search_phrases = get_trends(api)
    for phrase in search_phrases:

        c.execute("INSERT INTO `trends` (`name`) VALUES (%s) ON DUPLICATE KEY UPDATE `name`= VALUES(`name`) ; ",
                  (phrase) )


    print(search_phrases)
    my_listener = MyStreamListener()


    my_stream = tweepy.Stream(auth=api.auth, listener=my_listener)



    while True:
        try:
            #location
            #my_stream.filter(locations=[-125,25,-65,48])
            #search_phrase

            my_stream.filter(track=search_phrases)
            #language
            #my_stream.sample(languages=["en"])
            break
        except Exception as e:
        # Abnormal exit: Reconnect
            print("disconnected")
            nsecs = random.randint(60, 63)
            time.sleep(nsecs)


if __name__ == "__main__":
     main()
