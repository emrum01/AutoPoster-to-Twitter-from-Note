from newspaper import Article
import config
import tweepy
import requests
import json
import time

isNote = True


def getArticleKey():
    ArticlesUrl = 'https://note.com/api/v2/creators/urouro_tk/contents?kind=note&page=1'
    r = requests.get(ArticlesUrl)
    res = r.json()
    articleKey: str = res['data']['contents'][0]['key']
    return articleKey


def getArticle():
    scrapingUrl: str = f'https://note.com/urouro_tk/n/{getArticleKey()}'
    article = Article(scrapingUrl)
    article.download()
    article.parse()
    return article


def getNotionContent():
    novelUrl = 'https://api.notion.com/v1/blocks/45bcd275b4b444d8b22d2ccaed91b254/children'


def getArticleLength(article):
    return len(article)


def getArticleLengthForTweet(article):  # 一の位で四捨五入
    textLength = getArticleLength(article)
    if(float(textLength/10) - float(int(textLength/10))) >= 0.5:
        return (int(textLength/10)+1)*10
    else:
        return int(textLength/10)*10


def time2Read(length):
    LETTERS_READ_IN_A_MIN = 600
    if length % LETTERS_READ_IN_A_MIN > 0.5*LETTERS_READ_IN_A_MIN:
        return int(length/LETTERS_READ_IN_A_MIN) + 1
    else:
        return int(length/LETTERS_READ_IN_A_MIN)


file = "elems_text.txt"


def is_not_changed(old_elem, new_elem):
    return old_elem == new_elem


def set_old_elems():
    try:
        f = open(file)
        old_elems = f.read()
        print(f'{"old_elem":10} : {old_elems}')
    except:
        old_elems = ''
    return old_elems


def set_new_elems():
    new_elems = getArticleKey()
    print(f'{"new_elem":10} : {new_elems}')
    return new_elems


def is_newArticle_posted(old_elem, new_elem):
    if not is_not_changed(old_elems, new_elems):
        f = open(file, 'w')
        f.writelines(new_elems)
        f.close()
        print("Change is detected!!")
        return True
    else:
        print("not changed...")
        return False


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
        f'胡乱なるウーロン茶\n@urouro_tk\nで公開しているショートショートの１つ、「{title}」です。\nnoteでも無料公開しています。\n{getArticleLengthForTweet(article.text)}字程ですのでおよそ{time2Read(getArticleLength(article.text))}分程で読めると思います。')
    articleSentences: list = article.text.splitlines()
    articleSentences = [a for a in articleSentences if a != '']
    numArticleSentence: int = len(articleSentences)

    # 本文1ツイート分の内容を作成
    while i < numArticleSentence:
        i = start
        removeCount: int = 0
        while len(oneTweet) < 140 and i < numArticleSentence:
            oneTweet += articleSentences[i]+'\n'
            i += 1

        sentencesInATweet = oneTweet.splitlines()
        print(sentencesInATweet)
        while len(oneTweet) > 140 - 2:
            del sentencesInATweet[-1]
            removeCount += 1
            oneTweet = '\n'.join(sentencesInATweet)+'\n'
        print(oneTweet)

        tw.append(oneTweet)

        oneTweet = ''
        start = i - removeCount
    return tw


def tweet(contents, articleLength):
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
    # try:
    #     while True:
    #         print("="*100)
    #         new_elems = set_new_elems()
    #         old_elems = set_old_elems()
    #         if is_newArticle_posted(old_elems, new_elems):
    #             article = getArticle()
    #             articleLength = len(article.text)
    #             tweets: list = makeTweets(article, articleLength)
    #             tweet(tweets, articleLength)
    #         time.sleep(40)
    # except KeyboardInterrupt:
    #     print("Interrupted by Ctrl + C")
    article = getArticle()
    tweets: list = makeTweets(article)
    print(getArticleLengthForTweet(article.text))
    for i in tweets:
        print(i)
        print(len(i))
        print('-'*100)
