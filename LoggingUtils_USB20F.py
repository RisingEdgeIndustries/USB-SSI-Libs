#
# Title: LoggingUtils_USB20F
#
#
# Module Description:
# ----------------------
# Logging module message filters
#
#
# TODO:
# ----------------------
#
#
# ----------------------------------------------------------------
# Notes:
# ----------------------------------------------------------------
#
#


import logging
from logging.handlers import QueueHandler, QueueListener
try:
    import Queue as queue
except:
    import queue
import os
import sys
dir_path = 'logs/'





class MsgFilter(logging.Filter):
    """Filter only <logging.level> messages"""
    def __init__(self, level):
        self.__level = level


    # used to filter logging records and return true/false
    def filter(self, record):
        # format mod on record members
        if record.levelno == self.__level:
            record.levelname = '[%s]' % record.levelname
            record.name = '[%s]' % record.name
            return 1
        else:
            return 0


class MsgFilterAllPass(logging.Filter):
    """Filter only <logging.level> messages"""
    def __init__(self):
        pass

    # used to filter logging records and return true/false
    def filter(self, record):
        if record.levelno == logging.CRITICAL:
            # format mod on record members
            record.levelname = '[%s]' % record.levelname
            record.name = '[%s]' % record.name
        return 1



class StreamMsgFilter(logging.Filter):
    """Filter only <logging.level> messages"""
    def __init__(self, level_from):
        self.__level_from = level_from



    # used to filter logging records and return true/false
    def filter(self, record):
        # format mod on record members
        if (record.levelno > self.__level_from):
            record.levelname = '%s' % record.levelname
            record.name = '%s' % record.name
            return 1
        else:
            return 0



class StreamMsgFilterLess(logging.Filter):
    """Filter only <logging.level> messages"""
    def __init__(self, level_from):
        self.__level_from = level_from



    # used to filter logging records and return true/false
    def filter(self, record):
        # format mod on record members
        if (record.levelno < self.__level_from):
            record.levelname = '%s' % record.levelname
            record.name = '%s' % record.name
            return 1
        else:
            return 0


class StreamMsgFilterGreater(logging.Filter):
    """Filter only <logging.level> messages"""
    def __init__(self, level_from):
        self.__level_from = level_from



    # used to filter logging records and return true/false
    def filter(self, record):
        # format mod on record members
        if (record.levelno > self.__level_from):
            record.levelname = '%s' % record.levelname
            record.name = '%s' % record.name
            return 1
        else:
            return 0




class CustomConsoleLogHandler(logging.StreamHandler):
    def __init__(self, wxDest=None, wxLogEvent=None):
        logging.Handler.__init__(self)
        self.wxDest = wxDest
        self.wxLogEvent = wxLogEvent


    def flush(self):
        """
        Do nothing
        """


    def emit(self, record):
        """Constructor"""
        msg = self.format(record)
        evt = self.wxLogEvent(message=msg, levelname=record.levelname)
        wx.PostEvent(self.wxDest, evt)





class LogClass():

    def __init__(self, name, quiet=False):
        self.LOG_ROOT_PATH = 'logs/'
        self.NAME = name
        self.LoggerInit(quiet)


    #
    # Setup logging
    #
    def LoggerInit(self, quiet):
        

        # init log folder
        path = os.getcwd() + '/' + self.LOG_ROOT_PATH
        if(not os.path.isdir(path)):
            os.mkdir(path)

        self.q = queue.Queue(-1)
        self.queue_handler = QueueHandler(self.q)


        # setup formatter for handlers
        formatter = logging.Formatter('%(levelname)-10s:: %(name)-100s: %(message)s')

        #
        # setup handler5 - log all
        # - pass all leves (DEBUG, INFO, ERROR etc...) to the file handler
        self.handler5 = logging.FileHandler(self.LOG_ROOT_PATH + self.NAME + ".log", mode='w')
        self.handler5.setLevel(logging.INFO)
        self.handler5.setFormatter(formatter)
        self.handler5.addFilter(MsgFilterAllPass())
        

        #
        # Setup stream handler to get rid of console output
        #
        self.console = logging.StreamHandler(sys.stdout)


        # set quiet mode for no console printing if necessary
        if(quiet):
            self.console.addFilter(StreamMsgFilterLess(logging.NOTSET))   
        else:
            self.console.addFilter(StreamMsgFilterGreater(logging.DEBUG))




        # create listener
        self.listener = logging.handlers.QueueListener(self.q, self.handler5, self.console)       
        self.listener.start()


        # create root logger
        self.root = logging.getLogger(self.NAME)
        self.root.setLevel(logging.DEBUG)
        self.root.addHandler(self.queue_handler)





    def write(self, level, msg):
        # check level for valid values
        opts = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if(level not in opts):
            self.root.error(f"write method received <{level}> value for level var!")

        else:
            # write output
            if(level == "DEBUG"):
                self.root.debug(msg)
            elif(level == "INFO"):
                self.root.info(msg)
            elif(level == "WARNING"):
                self.root.warning(msg)
            elif(level == "ERROR"):        
                self.root.error(msg)
        



    def writeUSBPacket(self, level, msg):
        opts = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if(level not in opts):
            self.root.error(f"write method received <{level}> value for level var!")
        else:
            j = ""
            k = 0
            p = 1
            addr = 0
            j += f'[Addr {addr:#04x}] '

            for i in msg:
                j += f'{i:#04x}, '
                k += 1

                if(k >= 64):
                    self.write(level, f'packet {p}:\n{j}')
                    p += 1
                    k = 0
                    j = []
                    break

                if((k % 16) == 0):
                    addr += 16
                    j += "\n"
                    j += f'[Addr {addr:#04x}] '


    #
    # This function/method is important because
    # if the logger isn't shutdown correctly it
    # doesn't print all the log records and causes
    # problems exiting the aplication 'using' this
    # logging library. I ran into this in the
    # tst_dump-regs.py.
    #
    # MUST shutdown listener and flush all logging
    # handlers.
    #
    def shutdown_logging(self):
        self.handler5.flush()
        self.console.flush()
        self.console.close()
        self.listener.stop()

        logging.shutdown()



