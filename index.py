from newspaper import Article
import config
import tweepy
import requests
import json


ArticlesUrl = 'https://note.com/api/v2/creators/urouro_tk/contents?kind=note&page=1'
r = requests.get(ArticlesUrl)
res = r.json()
articleKey = res['data']['contents'][2]['key']
scrapingUrl = 'https://note.com/urouro_tk/n/{}'.format(articleKey)

article = Article(scrapingUrl)
article.download()
article.parse()
articleLength = len(article.text)


def time2Read(length):
    LETTERS_READ_IN_A_MIN = 600
    if length % LETTERS_READ_IN_A_MIN > 0.5*LETTERS_READ_IN_A_MIN:
        return int(length/LETTERS_READ_IN_A_MIN) + 1
    else:
        return int(length/LETTERS_READ_IN_A_MIN)


def makeTweets(article):
    tw: list = []
    oneTweet: str = ''
    sentencesInATweet: list = []
    start: int = 0
    i: int = 0

    # スクレイピング結果を整形
    title: str = article.title.split('｜')[0]

    # 最初のツイートを作成
    tw.append(
        f'胡乱なるウーロン茶\n@urouro_tk\nで公開しているショートショートの１つ、「{title}」です。\nnoteでも無料公開しています。\n{articleLength}字程ですのでおよそ{time2Read(articleLength)}分程で読めると思います。')
    articleSentences: list = article.text.split('。')
    numArticleSentence: int = len(articleSentences)

    # 本文1ツイート分の内容を作成
    while i < numArticleSentence:
        i = start
        removeCount: int = 0
        while len(oneTweet) < 140 and i < numArticleSentence:
            oneTweet += articleSentences[i]+'。'
            i += 1

        sentencesInATweet = oneTweet.split('。')
        while len(oneTweet) > 140:
            del sentencesInATweet[-1]
            oneTweet = '。'.join(sentencesInATweet) + '。'
            removeCount += 1
        tw.append(oneTweet)

        oneTweet = ''
        start = i - removeCount + 1
    return tw


def tweet(contents):
    # 取得した各種キーを格納-----------------------------------------------------
    consumer_key: str = config.API_KEY
    consumer_secret: str = config.API_KEY_SECRET
    access_token: str = config.ACCESS_TOKEN
    access_token_secret: str = config.ACCESS_TOKEN_SECRET
    # Twitterオブジェクトの生成
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # ツイートの回数を計算
    tweetCount: int = 1
    tweetCount += int(articleLength/140)
    if articleLength % 140 > 0:
        tweetCount += 1
    # ツイートを投稿
    for i in range(tweetCount):
        if i == 0:
            status = api.update_status(contents[i])
        else:
            status = api.update_status(contents[i], status.id_str)


if __name__ == '__main__':
    tweets: list = makeTweets(article)

    # デバッグ用
    for i in tweets:
        print(i)
        print(len(i))
        print('---')
