#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from logging import handlers


class MyLogger:

    def __init__(
        self,
        myloggername,
        myloggerpath,
        mylogfilename,
        ):
        self.myloglevel = logging.INFO
        self.mylogformat = '%(asctime)s %(levelname)s => %(message)s'
        self.maxBytes = 10 * 1024 * 1024
        self.backupCount = 5

        self.myloggername = myloggername
        self.myloggerpath = myloggerpath
        self.mylogfilename = mylogfilename
        self.mylogfile = self.myloggerpath + '/' + self.mylogfilename

        logging.basicConfig(format=self.mylogformat)
        self.loghandler = \
            logging.handlers.RotatingFileHandler(self.mylogfile,
                maxBytes=self.maxBytes, backupCount=self.backupCount)
        self.loghandler.setFormatter(logging.Formatter(self.mylogformat))

        self.mylogger = logging.getLogger(self.myloggername)
        self.mylogger.setLevel(self.myloglevel)
        self.mylogger.addHandler(self.loghandler)
        self.debug('loading logger: ' + myloggername + ' logger path: '
                   + myloggerpath + '/' + mylogfilename)

    def info(self, msg):
        return self.mylogger.info(msg)

    def debug(self, msg):
        return self.mylogger.debug(msg)

    def error(self, msg):
        return self.mylogger.error(msg)

    def getMyLogger(self):
        return self.mylogger
