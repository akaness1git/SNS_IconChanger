#!/usr/bin/python3
# coding: utf-8

"""
IconChangerメインクラス
ログ関係の初期化やアイコンチェンジの基底部分を処理する。
また、おまけでGoogleDriveへのファイルアップロード機能も付いてる。
"""
import os
import glob
import yaml
import logging
import datetime
import time
import modules

class SetLogger:
    '''
    Loggerクラス
    Logのセットアップを行う。
    '''
    def __init__(self):
        self.logfh = None
        self.logger = logging.getLogger('LoggingTest')
        self.logfmt = logging.Formatter('%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        self.log_filename = 'info.log'
        self.log_folder = './'

    def _init_log(self):
    	self.logger.setLevel(logging.INFO)
    	sh = logging.StreamHandler()
    	sh.setFormatter(self.logfmt)
    	self.logger.addHandler(sh)
    	self._refresh_log()
    
    def _refresh_log(self):
    	self.logfh = logging.FileHandler(self.log_folder+self.log_filename)
    	self.logger.addHandler(self.logfh)
    	self.logfh.setFormatter(self.logfmt)

class IconChanger:
    '''
    IconChangerクラス
    アイコンチェンジの基底部分を処理する。
    '''
    def __init__(self):
        # 設定ファイル読み込み
        f = open("settings.yaml", "r+")
        yamldata = yaml.load(f)
        f.close()
        # Driver読み込み
        self.Twitter = modules.TwitterDriver.TwitterDriver(yamldata)
        self.GoogleDrive = modules.GoogleDriveDriver.GoogleDriveDriver(yamldata)
    
    def _delete_file(self,filename,delFile):
        """
        一時的にダウンロードしておいたイメージファイルを削除する。
        :params filename:イメージファイル名
        :params delFile: 画像ファイルを削除するかどうか。
        """
        if delFile:
            os.remove(filename)

    def _check_status(self,status):
        """
        各API接続後のステータスチェックを行う。
        :params status: ステータス。0以外は異常コード
        :return:  msg: 異常時のメッセージ
        """
        msg = None
        if status == 0:
            return msg
        elif status == 9:
            msg = "GoogleDriveDriver Error End."
            return msg
        elif status == 8:
            msg = "TwitterDriver Error End."
            return msg
            
    def _iconchanger_main(self,logger,delFile=True):
        """
        アイコンチェンジャーのメイン部分。
        :params logger: ログ変数
        :params delFile: 終了後にダウンロードした画像ファイルを削除するかどうか。未指定の場合は削除する。
        """
        msg = None
        # ランダムで選択されたイメージファイルをローカルにダウンロードする。
        status,filename = self.GoogleDrive._pick_image()
        result = filename
        msg = self._check_status(status)
        if status != 0:
            logger.info(msg)
            logger.info(result)
            return 
        # Twitterのアイコンを更新する。
        status,result = self.Twitter._upload_profile_image(filename)
        msg = self._check_status(status)
        if status != 0:
            logger.info(msg)
            logger.info(result)
        # イメージファイルを削除する。
        self._delete_file(filename,delFile)
        logger.info(f"Icon Changer is Done. {filename}")
        return 

def main():
    """
    アイコンチェンジャーメイン部
    """
    # 開始時間の記録
    start_time = time.time()
    # ログセットアップ
    Log = SetLogger()
    Log._init_log()
    Log.logger.info("Icon changer started!")
    # アイコンチェンジャーセットアップ
    iconChanger = IconChanger()
    # 実行
    iconChanger._iconchanger_main(Log.logger)
    # 処理時間をログに記載
    Log.logger.info("Processing time: %.6f[sec]" % (time.time() - start_time))

def upload():
    """
    GoogleDriveにイメージファイルをアップロードする。
    アップロード対象はuploadsフォルダの中にあるpngファイルのみ。
    """
    # 開始時間の記録
    start_time = time.time()
    # ログセットアップ
    Log = SetLogger()
    Log._init_log()
    Log.logger.info("Image upload started!")
    try:
        iconChanger = IconChanger()
        filelist = glob.glob("./uploads/*.png")
        for file in filelist:
            iconChanger.GoogleDrive._upload(file)
            Log.logger.info(f"upload is done. {os.path.basename(file)}")
    except Exception as e:
        import traceback
        msg = f"GoogleDriveDriver._upload Error!\n{traceback.format_exc()}"
        Log.logger.info(f"Error!\n{msg}")
    Log.logger.info("Processing time: %.6f[sec]" % (time.time() - start_time))

if __name__ == "__main__":
    #upload()
    main()
    