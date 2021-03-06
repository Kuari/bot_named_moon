#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import time
import os
import multiprocessing
import psutil
import sqlite3
import random

from run import BAIDUAIP
#from joy import QiuShi
from worm import WORM
from weather import WEATHER
from getMusic import GetMusic 
from TopMusic import TOPMusic
from tuling2 import tuling

class HANDLE:

    def __init__(self):
        self.bd = BAIDUAIP()
        self.weather = WEATHER()
        self.__playmusic = re.compile(r'.*?播放音乐(.*?)，')
        self.__joy = re.compile(r'.*?讲.*?笑话.*?，')
        self.__weather1 = re.compile(r'.*?今[天日].*?天气.*?，')
        self.__weather2 = re.compile(r'.*?明[天日].*?天气.*?，')
        self.__weather3 = re.compile(r'.*?后[天日].*?天气.*?，')
        self.__top = re.compile(r'推荐(.*?)音乐.*?，')
        self.__playtop = re.compile(r'.*?播放(.*?)推荐.*?，')
        self.__collect = re.compile(r'.*?收藏.*?音乐.*?，')
        self.__removecollect = re.compile(r'取消.*?收藏.*?，')
        self.__playcollection = re.compile(r"(.*?)播放收藏.*?，")
        self.conn = sqlite3.connect("thedata.db")
 

    def beText(self):
        return self.bd.getText(".audio.wav")

    def beAudio(self,text):
        return self.bd.getAudio(text)

    def formatHandle(self, indexes, data):
        return { 0:indexes, 1:data }

    def getMusicList(self):
        cur = self.conn.execute("select name from music")
        n = 0
        _List = {}
        for row in cur.fetchall():
            _List[n]=[row]
            n += 1
        return _List


    def handleData(self, data):
        print time.strftime("%Y-%m-%d %H:%M:%S") + "        你说的是 >>>" + data
        if self.__joy.search(data):
            return self.formatHandle("playthis", WORM().worm())
        elif self.__weather1.search(data):
            return self.formatHandle("playthis", self.weather.results("1"))
        elif self.__weather2.search(data):
            return self.formatHandle("playthis", self.weather.results("2")) 
        elif self.__weather3.search(data):
            return self.formatHandle("playthis", self.weather.results("3"))
        elif data == '你好，':
            return self.formatHandle("playthis", '主人，你好呀')
        elif self.__playmusic.search(data):
            _name = self.__playmusic.search(data).group(1)
            return self.formatHandle("playid", GetMusic().getID(_name))
        elif self.__top.search(data):
            _type = self.__top.search(data).group(1)
            return self.formatHandle("playthis", TOPMusic().showTop(_type))
        elif self.__playtop.search(data):
            _type = self.__playtop.search(data).group(1)
            return self.formatHandle("playlist", TOPMusic().playTop(_type))
        elif self.__collect.search(data):
            return self.formatHandle("runco", self.__name[0])
        elif self.__removecollect.search(data):
            return self.formatHandle("runre", self.__name[0])
        elif self.__playcollection.search(data):
            _type = self.__playcollection.search(data).group(1)
            if _type == "随机":
                return self.formatHandle("playcorandom", "none")
            return self.formatHandle("playco", "none")
        elif data == "人生苦短，":
            return self.formatHandle("stopall","none")
        else:
            try:
                ddd = tuling(data)
                return self.formatHandle("playthis", ddd)
            except BaseException:
                return 'Other'

    def runFunction(self, data):
        print 'data is :', data
        try:
            _data = self.handleData(data)
            _data0 = str(_data[0])
            _data1 = _data[1]
            print '#######'*10,'_data0,_data1'
            print _data0,_data1
            print '#######'*10
            if _data0 == "playthis":
                self.beAudio(_data1)
                os.system('mplayer audio.mp3')
            elif _data0 == "playid":
                GetMusic().PlaySong(int(_data1))
            elif _data0 == "playlist":
                for i in xrange(len(_data1)+1):
                    id = GetMusic().getID(_data1[i])
                    GetMusic().PlaySong(id)
            elif _data0 == "runco":
                self.conn.execute("insert into music (name) values '%s'"%str(_data1))
                self.conn.commit()
                print "OK!Successfully collect it."
            elif _data0 == "runre":
                self.conn.execute("delete from music where name = '%s'"%str(_data1))
                self.conn.commit()
                print "Delete the song..."
            elif _data0 == "playcorandom":
                _List = self.getMusicList()
                _Len = len(_List)
                for i in xrange(_Len):
                    _id = random.randint(0,_Len)
                    _id = GetMusic().getID(_List[_id])
                    GetMusic.PlaySong(int(_id))
            elif _data0 == "playco":
                _List = self.getMusicList()
                print _List
                for i in xrange(_Len):
                    print i
                    _id = GetMusic().getID(i)
                    GetMusic.PlaySong(int(_id))
            elif _data0 == "stopall":
                self.killMplayer()
                self.killChilProcess(os.getpid())
            else:
                self.beAudio("主人，我不太明白你的意思")
                os.system("mplayer audio.mp3")
        except BaseException:
            os.system("mplayer '.error.mp3'")


    def runNewProcess(self, _data):
        _newprocess = multiprocessing.Process(target=self.runFunction, args=(_data,))
        _newprocess.start()

    def killChilProcess(self, pid):
        _chidprocess =psutil.Process(pid).children()
        for i in _chidprocess:
            __pid = str(i)[16:-1].split(",")[0][3:]
            print "杀死子进程...",__pid
            os.system("kill -9 %s"%(int(__pid)))

    def killMplayer(self):
        data="mplayer"
        lines = os.popen("ps -aux | grep %s"%data)
        for i in lines:
            _id = i.strip().split()[1]
            print "杀死Mplayer进程...",_id
            os.system("kill -9 %s"%_id)

    def Start(self, data):
        self.runNewProcess(data)

    def Kill(self, pid):
        self.killChilProcess(pid)


if __name__ == "__main__":
    h = HANDLE()
    data = raw_input(' >>>')
    h.Start(data) 
