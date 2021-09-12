from newspaper import Article
import config
import tweepy

TWEET_NUM = 140

url = 'https://note.com/urouro_tk/n/n53cad04b3ec1'
article = Article(url)
article.download()
article.parse()
title = article.title.split('｜')[0]

articleLength = len(article.text)

# ツイートの回数を計算
tweetTimes = 1
tweetTimes += int(articleLength/140)
if articleLength % 140 > 0:
    tweetTimes += 1

letterNum = 0
start = 0
end = 0
tw = []

tw.append(
    '胡乱なるウーロン茶\n@urouro_tk\nで公開しているショートショートの１つ、「{}」です。\nnoteでも無料公開しています。\n800字程ですのでおよそ2分程で読めると思います。'.format(title))
for i in range(tweetTimes):
    if len(article.text) > 140:
        tw.append(article.text[letterNum:TWEET_NUM])
        letterNum += 140
        TWEET_NUM += 140
    else:
        tw.append(article.text)
    print(tw[i])

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


# # ツイートを投稿
for i in range(tweetTimes):
    if i == 0:
        status = api.update_status(tw[i])
    else:
        status = api.update_status(tw[i], status.id_str)

# Account = "@tacubaya_"  # 取得したいユーザーのユーザーIDを代入
# tweets = api.user_timeline(Account, count=20, page=1)
# num = 1  # ツイート数を計算するための変数
# for tweet in tweets:
#     print('twid : ', tweet.id)               # tweetのID
#     print('user : ', tweet.user.screen_name)  # ユーザー名
#     print('date : ', tweet.created_at)      # 呟いた日時
#     print(tweet.text)                  # ツイート内容
#     print('favo : ', tweet.favorite_count)  # ツイートのいいね数
#     print('retw : ', tweet.retweet_count)  # ツイートのリツイート数
#     print('ツイート数 : ', num)  # ツイート数
#     print('='*80)  # =を80個表示
#     num += 1  # ツイート数を計算
