from newspaper import Article
import config

print(config.API_KEY)
TWEET_NUM = 140

url = 'https://note.com/urouro_tk/n/n53cad04b3ec1'
article = Article(url)
article.download()
article.parse()

articleLength = len(article.text)

# ツイートの回数を計算
tweetTimes = int(articleLength/140)
if articleLength % 140 > 0:
    tweetTimes += 1

letterNum = 0
start = 0
end = 0
tw = []

for i in range(tweetTimes):
    if len(article.text) > 140:
        tw.append(article.text[letterNum:TWEET_NUM])
        letterNum += 140
        TWEET_NUM += 140
    else:
        tw.append(article.text)
    print(tw[i], i)
