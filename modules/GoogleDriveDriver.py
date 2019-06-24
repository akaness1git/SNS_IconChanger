#!/usr/bin/python3
# coding: utf-8
import yaml
import os
import random
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class GoogleDriveDriver:
    '''
    GoogleDriveクラス
    GoogleDriveからアイコンとなるイメージファイルをダウンロードする。
    また、アップロードを行うことも出来る。
    '''
    def __init__ (self,yamldata):
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)
        self.folder_id = yamldata.get('folder_id')
        self.max_results = 100
        self.query = f"'{self.folder_id}' in parents and trashed=false"
    
    def _get_mimeType(self,filename):
        """
        アップロードする際のmimeTypeの判別をする。イメージファイル専用
        :params filename: アップロードファイル名
        :return: jpg or png
        """
        extension = os.path.splitext(filename)[1][1:]
        if extension == 'jpg' or extension == 'jpeg':
            r = 'image/jpeg'
        elif extension == 'png':
            r = 'image/png'
        return r

    def _upload(self,filename):
        """
        ファイルのアップロードを行う。
        :params filename: アップロードファイル名
        """
        # folder_idの指定がない場合はhomeに
        if self.folder_id is None:
            f = self.drive.CreateFile({'title': os.path.basename(filename)
                                    , 'mimeType': self._get_mimeType(filename)})
        # folder_idの指定がある場合はそのフォルダに
        else:
            f = self.drive.CreateFile({'title': os.path.basename(filename)
                                    , 'mimeType': self._get_mimeType(filename)
                                    , 'parents': [{'kind': 'drive#fileLink', 'id':self.folder_id}]})
        f.SetContentFile(filename)
        f.Upload()

    def _get_filelist(self):
        """
        GoogleDriveのファイルリストを作成する。
        :return: GoogleDriveのファイル辞書データリスト
        """
        l = []
        for file_list in self.drive.ListFile({'q': self.query, 'maxResults': self.max_results}):
            for file in file_list:
                l.append(file)
        return l
    
    def _download(self,file,downloadpath="./"):
        """
        ファイルをローカルにダウンロードする。
        :params downloadpath: ダウンロード先フォルダ。未指定の場合は実行ファイルと同階層。
        """
        file.GetContentFile(os.path.join(downloadpath, file['title']))
    
    def _pick_file(self,filelist):
        """
        GoogleDriveのファイルリストから1つを無作為に選ぶ。
        :params filelist: GoogleDriveのファイル辞書データリスト
        :return: GoogleDriveのファイル辞書データ
        """
        return random.choice(filelist)
    
    def _pick_image(self,downloadpath="./"):
        """
        アイコンにするイメージを1枚選択し、ローカルにダウンロードする。
        :params downloadpath: ダウンロード先フォルダ。未指定の場合は実行ファイルと同階層。
        :return1: status: 0でないならエラー
        :return2:    msg: ファイル名。エラーの場合はエラーメッセージ
        """
        try:
            l = self._get_filelist()
            file = self._pick_file(l)
            self._download(file,downloadpath)
            return 0,file['title']

        except Exception as e:
            import traceback
            msg = f"GoogleDriveDriver._pick_image Error!\n{traceback.format_exc()}"
            return 9,msg