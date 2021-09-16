import sys
from newspaper import Article
import config
import tweepy
import requests
import json
from itertools import chain
import time

isNote = True


# note


# 最新のnote記事のidを取得
def getArticleKey():
    ArticlesUrl = 'https://note.com/api/v2/creators/urouro_tk/contents?kind=note&page=1'
    r = requests.get(ArticlesUrl)
    res = r.json()
    articleKey: str = res['data']['contents'][0]['key']
    return articleKey


# 最新のnote記事のタイトルと本文を取得
def getArticle():
    scrapingUrl: str = f'https://note.com/urouro_tk/n/{getArticleKey()}'
    article = Article(scrapingUrl)
    article.download()
    article.parse()
    title: str = article.title.split('｜')[0]
    text: str = article.text
    return {'title': title, 'text': text}


def getRequestUrl(id):
    return f'https://api.notion.com/v1/blocks/{id}/children'


def shapeNovelContentID(res):
    return res.json()['results'][-1]['id']


def shapeNovelContent(res):
    return res.json()['results'][0]['toggle']['text'][0]['text']['content']


def shapeNovelTitle(res):
    return res.json()['results'][-1]['toggle']['text'][0]['text']['content']


def shapeOldID(res):
    return res.json()['properties']['ID']['rich_text'][0]['text']['content']


def getDBUrl(notionOrNote):  # id保存先の行の選択
    notion_row_id = config.DB_NOTION_ROW_ID
    note_row_id = config.DB_NOTE_ROW_ID

    if notionOrNote['notion'] and not notionOrNote['note']:
        id = notion_row_id
    elif not notionOrNote['notion'] and notionOrNote['note']:
        id = note_row_id
    else:
        return {
            'note': f'https://api.notion.com/v1/pages/{note_row_id}',
            'notion': f'https://api.notion.com/v1/pages/{notion_row_id}'
        }

    return f'https://api.notion.com/v1/pages/{id}'


def getOldIDs(notionOrNote):
    if not notionOrNote['notion'] and not notionOrNote['note']:
        requestUrls = getDBUrl(notionOrNote)
        notion_api_key = config.NOTION_SECRET
        headers = {"Authorization": f"Bearer {notion_api_key}",
                   "Content-Type": "application/json",
                   "Notion-Version": "2021-05-13"}
        old_ids = {}
        for k, v in requestUrls.items():
            res = requests.request(
                'GET', url=v, headers=headers)
            old_ids[k] = shapeOldID(res)
        print(old_ids['notion'])
        return old_ids

    else:
        print('some trouble')


def isNotionOrNote(notionOrNote):
    if notionOrNote['notion'] and not notionOrNote['note']:
        return 'notion_old_id'
    elif not notionOrNote['notion'] and notionOrNote['note']:
        return 'note_old_id'


def updateOldID(notionOrNote, new_id):
    notion_api_key = config.NOTION_SECRET
    headers = {"Authorization": f"Bearer {notion_api_key}",
               "Content-Type": "application/json",
               "Notion-Version": "2021-05-13"}
    data = {
        "properties": {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": isNotionOrNote(notionOrNote)
                        }
                    }
                ]
            },
            "ID": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": new_id
                        }
                    }
                ]
            }
        }
    }

    return requests.request(
        'PATCH', url=getDBUrl(notionOrNote), headers=headers, data=json.dumps(data))


# notionから本文,タイトル, id取得
def getBlockFromNotion(block_id):  # notionのapi呼び出しを共通化
    notion_api_key = config.NOTION_SECRET
    headers = {"Authorization": f"Bearer {notion_api_key}",
               "Content-Type": "application/json",
               "Notion-Version": "2021-05-13"}
    return requests.request(
        'GET', url=getRequestUrl(block_id), headers=headers)


def getNotionContentID():
    block_id = config.NOTION_REPOST_BLOCK_ID
    response = getBlockFromNotion(block_id)
    content_id = shapeNovelContentID(response)
    print('new_id'+content_id)
    return content_id


def getNotionContentTitle():
    block_id = config.NOTION_REPOST_BLOCK_ID
    response = getBlockFromNotion(block_id)
    novelTitle = shapeNovelTitle(response)
    return novelTitle


def getNotionContentText(content_id):
    notion_api_key = config.NOTION_SECRET
    headers = {"Authorization": f"Bearer {notion_api_key}",
               "Content-Type": "application/json",
               "Notion-Version": "2021-05-13"}
    resContent = requests.request(
        'GET', url=getRequestUrl(content_id), headers=headers)
    novelText = shapeNovelContent(resContent)

    return novelText


def getNovelFromNotion(content_id):
    title = getNotionContentTitle()
    text = getNotionContentText(content_id)
    return {'title': title, 'text': text}


# ツイート関係
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


def makeTweets(article):
    tw: list = []
    oneTweet: str = ''
    sentencesInATweet: list = []
    start: int = 0
    i: int = 0

    title: str = article['title']
    text: str = article['text']

    # 最初のツイートを作成
    tw.append(
        f'胡乱なるウーロン茶\n@urouro_tk\nで公開しているショートショートの１つ、「{title}」です。\nnoteでも無料公開しています。\n{getArticleLengthForTweet(text)}字程ですのでおよそ{time2Read(getArticleLength(text))}分程で読めると思います。')
    articleRows: list = text.splitlines()

    rowslen = len(articleRows)
    for i in range(rowslen):
        # 改行後の文が140字を超える場合は
        if len(articleRows[i]) > 140 - 2:
            l = articleRows[i].split('。')
            l = [i+'。'for i in l if i != '']
            # if i == 0:
            #     articleRows = l + articleRows[i+1:]
            # elif 0 < i and i < rowslen-1:
            #     articleRows = articleRows[:i-1] + l + articleRows[i+1:]
            # elif i == rowslen-1:
            #     articleRows = articleRows[:i-1] + l
            articleRows[i] = l
        else:
            articleRows[i] = ''.join(list(articleRows[i]))
    articleRows = [a for a in articleRows if a != '']
    def flatten(x): return [z for y in x for z in (
        flatten(y) if hasattr(y, '__iter__') and not isinstance(y, str) else (y,))]
    articleRows = flatten(articleRows)
    numArticleSentence: int = len(articleRows)

    # 本文1ツイート分の内容を作成
    # i = 0 # 型エラーが出たのでキャスト&初期化
    while i < numArticleSentence:
        i = start
        removeCount: int = 0
        while len(oneTweet) < 140 and i < numArticleSentence:
            oneTweet += articleRows[i]+'\n'
            i += 1

        sentencesInATweet = oneTweet.splitlines()
        while len(oneTweet) > 140 - 2:
            del sentencesInATweet[-1]
            removeCount += 1
            oneTweet = '\n'.join(sentencesInATweet)+'\n'

        tw.append(oneTweet)

        oneTweet = ''
        start = i - removeCount
    return tw


def tweet(contents, articleLength):
    # 取得した各種キーを格納
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
    notionOrNote = {'notion': False, 'note': False}  # notion, note変更通知用変数
    old_ids = getOldIDs(notionOrNote)
    notion_new_id = getNotionContentID()
    note_new_id = getArticleKey()
    print(f'note_new_id  {note_new_id}')

    # note, notion のどちらが変更されたか判定
    # notion のみが変更された場合
    if notion_new_id != old_ids['notion'] and note_new_id == old_ids['note']:
        notionOrNote['notion'] = True
        updateOldID(notionOrNote, notion_new_id)
        print('notion id is successfully updated')
        # 小説を取得
        novel: object = getNovelFromNotion(notion_new_id)
        tw = makeTweets(novel)
        for i in tw:
            print(i)
            print(len(i))
            print('---')

    # note のみが変更された場合
    elif notion_new_id == old_ids['notion'] and note_new_id != old_ids['note']:
        notionOrNote['note'] = True
        updateOldID(notionOrNote, note_new_id)
        print('note id is successfully updated')
        novel: object = getArticle()
        tw = makeTweets(novel)

    else:
        print('no change happend')
