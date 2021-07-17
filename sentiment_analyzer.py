from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from keys import consumer_key, consumer_secret, access_token, access_secret
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
import matplotlib.pyplot as plt
from tkinter import *
from PIL import ImageTk, Image

#TWITTER CLIENT
class TwitterClient():
    
    def __init__(self, twitter_user = None):
        self.auth = TwitterAuthenticator().authenticate()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user
        
    def get_twitter_client_api(self):
        return self.twitter_client
        
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
        
    def get_friend_list(self, num_friends):
        friends_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friends_list.append(friend)
        return friends_list
    
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = [];
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets
        
        

#TWITTER AUTHENTICATOR
class TwitterAuthenticator():
    
    def authenticate(self):
        auth = OAuthHandler(consumer_key , consumer_secret)
        auth.set_access_token(access_token, access_secret)
        return auth


#TWITTER STREAMER
class TwitterStreamer():
    """
    Class for streaming and processing live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self, fetched_tweets_filename, hashtag_list):
        #This class handles Twitter Authentication and the connection to the Twitter API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate()
        stream = Stream(auth, listener)
        
        #This line filter Twitter Streams to capture data by the keywords 
        stream.filter(track = hashtag_list)

#TWITTER STREAM LISTENER
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename
    
    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True
    
    def on_error(self, status):
        if status == 420:
            #Returning False on_data method in case rate limit occurs
            return False
        print(status)
        

class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets
    """  
    
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1
            
    def tweets_to_df(self, tweets):
        df = pd.DataFrame(data=[self.clean_tweet(tweet.text) for tweet in tweets], columns=['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df
    
    
def showgraph(x, y):
    ticks = [-1, 0, 1]
    labels = ['Negative', 'Neutral', 'Positive']
    plt.yticks(ticks, labels)
    plt.xticks(rotation= 60)
    plt.plot(x, y, color = 'g', marker='o',linestyle = 'dotted')
    plt.ylabel("Sentiment")
    plt.xlabel("Date")
    plt.title('Sentiments Analysis')
    plt.show()
    
    
def run(name, cnt):
    
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()
    
    tweets = api.user_timeline(screen_name= name.get(), count=cnt.get())
    
    df = tweet_analyzer.tweets_to_df(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Tweets']])
    
    df.to_excel("output.xlsx") 
    
    y = df['sentiment']
    x = df['date']
    showgraph(x, y)
    

if __name__=="__main__":
    #GUI USING TKINTER
    root = Tk()
    root.title("Sentiments Analysis")
    root.geometry("400x260")
    
    my_img = Image.open("icon.png")
    resized_img = my_img.resize((190, 193), Image. ANTIALIAS)
    
    new_img = ImageTk.PhotoImage(resized_img)
    
    img_label = Label(root,image = new_img).grid(row = 0, column = 4, rowspan = 6, sticky=E)
    
    Label(root, text="Twitter Username").grid(row = 0, column = 0)
    name = StringVar()
    
    e = Entry(root, textvariable=name)
    e.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
    
    
    Label(root, text="No. of Tweets to Analyze").grid(row = 2, column = 0)
    cnt = IntVar()
    
    e = Entry(root, textvariable=cnt)
    e.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
    
    button_1 = Button(root, text ="Graph It!", command=lambda: run(name, cnt))
    # Button for closing
    exit_button = Button(root, text="Exit", command=root.destroy)
    
    button_1.grid(row=4, column=0)
    exit_button.grid(row=5, column=0)
    
    root.mainloop()