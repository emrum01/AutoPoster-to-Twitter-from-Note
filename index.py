from newspaper import Article
import config
import tweepy

TWEET_NUM = 140

url = 'https://note.com/urouro_tk/n/n800d2b42e21c'
article = Article(url)
article.download()
article.parse()


def time2Read(length):
    LETTERS_READ_IN_A_MIN = 600
    if length % LETTERS_READ_IN_A_MIN > 0.5:
        return int(length/LETTERS_READ_IN_A_MIN) + 1
    else:
        return int(length/LETTERS_READ_IN_A_MIN)


articleLength = len(article.text)
tw = []
title = article.title.split('｜')[0]
tw.append(
    '胡乱なるウーロン茶\n@urouro_tk\nで公開しているショートショートの１つ、「{}」です。\nnoteでも無料公開しています。\n{}字程ですのでおよそ{}分程で読めると思います。'.format(title, articleLength, time2Read(articleLength)))
articleSentences = article.text.split('。')
oneTweet = ''
sentencesInATweet = []
start = 0
i = 0
numArticleSentence = len(articleSentences)
# 1ツイート分の内容を作成

while i < numArticleSentence:
    i = start
    removeCount = 0
    while len(oneTweet) < 140 and i < numArticleSentence:
        oneTweet += articleSentences[i]+'。'
        i += 1

    sentencesInATweet = oneTweet.split('。')
    while len(oneTweet) > 140:
        del sentencesInATweet[-1]
        oneTweet = '。'.join(sentencesInATweet)
        removeCount += 1
    tw.append(oneTweet)

    oneTweet = ''
    start = i - removeCount + 1

# 取得した各種キーを格納-----------------------------------------------------
consumer_key = config.API_KEY
consumer_secret = config.API_KEY_SECRET
access_token = config.ACCESS_TOKEN
access_token_secret = config.ACCESS_TOKEN_SECRET
# Twitterオブジェクトの生成
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
# -------------------------------------------------------------------------


# ツイートの回数を計算

tweetTimes = 1
tweetTimes += int(articleLength/140)
if articleLength % 140 > 0:
    tweetTimes += 1
# ツイートを投稿
for j in range(tweetTimes):
    if j == 0:
        status = api.update_status(tw[j])
    else:
        status = api.update_status(tw[j], status.id_str)
