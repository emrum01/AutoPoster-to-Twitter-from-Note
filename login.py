
import urllib
import webbrowser
import oauth2 as oauth
import config


class TwitterOauth:

    REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
    ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
    AUTHENTICATE_URL = "https://api.twitter.com/oauth/authenticate"

    def __init__(self, key, secret):
        self.consumer = oauth.Consumer(key=key, secret=secret)

    def get_authenticate_url(self):
        """
        認証ページのURLを返す
        """
        self._set_request_token_content()
        request_token = self.request_token_content["oauth_token"][0]
        query = urllib.parse.urlencode({"oauth_token": request_token})
        authenticate_url = self.AUTHENTICATE_URL + "?" + query
        return authenticate_url

    def get_access_token_content(self, pin):
        """
        Access Token などの情報が入ったdictを返す
        """
        oauth_token = self.request_token_content["oauth_token"][0]
        oauth_token_secret = self.request_token_content["oauth_token_secret"][0]
        token = oauth.Token(oauth_token, oauth_token_secret)
        client = oauth.Client(self.consumer, token)
        body = urllib.parse.urlencode({"oauth_verifier": pin})
        resp, content = client.request(
            self.ACCESS_TOKEN_URL, "POST", body=body)
        return urllib.parse.parse_qs(content.decode())

    def _set_request_token_content(self):
        client = oauth.Client(self.consumer)
        resp, content = client.request(self.REQUEST_TOKEN_URL, "GET")
        self.request_token_content = urllib.parse.parse_qs(content.decode())


if __name__ == '__main__':

    ###############################################################################
    CONSUMER_KEY = config.API_KEY            # ここに API key を設定する
    CONSUMER_SECRET = config.API_KEY_SECRET  # ここに API secret key を設定する
    ###############################################################################

    t = TwitterOauth(CONSUMER_KEY, CONSUMER_SECRET)
    authenticate_url = t.get_authenticate_url()  # 認証ページのURLを取得する
    webbrowser.open(authenticate_url)            # ブラウザで認証ページを開く

    print("PIN? >> ", end="")
    pin = int(input())

    access_token_content = t.get_access_token_content(pin)
    access_token = access_token_content["oauth_token"][0]
    access_token_secret = access_token_content["oauth_token_secret"][0]
    s = "ACCESS TOKEN        = {}\nACCESS TOKEN SECRET = {}"
    s = s.format(access_token, access_token_secret)
    print(s)
