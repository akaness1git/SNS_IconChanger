#!/usr/bin/python3
# coding: utf-8

import yaml
import json
import base64
from requests_oauthlib import OAuth1Session

class TwitterDriver:
    """
    Twitterクラス
    Twitterへアイコンをアップロードし、プロフィールを更新する。
    """
    def __init__ (self,yamldata):
        CK = yamldata.get('TWITTER_CONSUMER_KEY')
        CS = yamldata.get('TWITTER_CONSUMER_SECRET')
        AT = yamldata.get('TWITTER_ACCESS_TOKEN')
        ATS = yamldata.get('TWITTER_ACCESS_TOKEN_SECRET')
        self.twitter = OAuth1Session(CK, CS, AT, ATS)
        self.profile_url = 'https://api.twitter.com/1.1/account/update_profile_image.json'
    
    def _upload_profile_image(self,filename):
        """
        アイコンをアップロードし、更新する。
        :params filename: アップロードするイメージファイル名
        :return1: status: 0でないならエラー
        :return2:    msg: 終了メッセージ
        """
        b64 = base64.encodestring(open(filename, 'rb').read())
        params = {'image': b64}
        r = self.twitter.post(self.profile_url, data=params)
        if r.status_code == 200:
            return 0,"TwitterDriver_upload_profile_image is Done."
        else:
            return 9,"TwitterDriver_upload_profile_image is Failed."
