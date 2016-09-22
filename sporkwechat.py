#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import re
import sys
import time

import hashlib
import json
import threading

import urllib2
from urllib2 import urlopen, URLError

import Queue
from Queue import Queue

from bs4 import BeautifulSoup
from random import randint
from time import ctime
from urlparse import urlparse, urljoin

import settings

''' Threading module '''
class MyThread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name=name
        self.func=func
        self.args=args
        
    def getResult(self):
        return self.res

    def run(self):
        print('Starting', self.name, 'at:', ctime())
        self.res=apply(self.func, self.args)
        print(self.name, 'Finished at:', ctime())

''' url downloading function '''
def download(url):
    request = urllib2.Request(url)
    request.add_header('Referer', settings.domainHost)
    request.add_header('User-agent', settings.userAgents[randint(0, len(settings.userAgents)-1)])

    try:
        reply = urllib2.urlopen(request, timeout=5).read()
    except URLError, e:
        print(e.getcode(), e.geturl(), e.reason)
        print(e.info())
        print(e.read())
        reply = ('*** ERROR: invalid URL "%s"' % url)
    finally:
        return reply

''' md5 '''
def md5(srcstr):
    md5Str = hashlib.md5(srcstr).hexdigest()[:-16]
    hexList = []
    for i in range(0, len(md5Str), 2):
        hexList.append(md5Str[i:i+2])
    md5Num = str(long(''.join(hexList[::-1]), 16))
    return md5Num

def consumer(urlQueue, nThread):
    print('Consumer (%d) starts...' % nThread)
    while not urlQueue.empty():
        url = urlQueue.get(1)
        print('Consumer (%d) gets the task: %s...' % (nThread, url))

        reply = download(url)
        if reply.startswith('***'):
            print(reply, '...skipping parse')
            continue

        soup = BeautifulSoup(reply, "html.parser")
        selectorDict = {}

        selectorDict['base'] = {}
        selectorDict['basic'] = {}
        selectorDict['links'] = []

        selectorDict['base']['website'] = settings.siteName
        selectorDict['base']['srcid'] = md5(url)
        selectorDict['base']['srclink'] = url

        for pattern in settings.urlPatterns:
            if re.match(pattern['url'], url) is not None:
                if settings.DEBUG:
                    print(pattern['url'])

                for key in pattern['selector'].keys():
                    if key.startswith('links_'):
                        for link in soup.select(pattern['selector'][key]):
                            link = link.get('href')
                            if link[:4] != 'http' and link.find(r'://') == -1:
                                link = urljoin(url, link)
                            selectorDict['links'].append(link)
                    else:
                        selectList = soup.select(pattern['selector'][key])
                        if len(selectList):
                            if key == 'content':
                                selectorDict['basic'][key] = str(selectList[0])
                            else:
                                selectorDict['basic'][key] = selectList[0].string.strip()
                        else:
                            selectorDict['basic'][key] = ''

        '''
        urlQueue.put(link)
        print("URL", link, 'adds to queue, size is', urlQueue.qsize())
        '''
        print(json.dumps(selectorDict))

        time.sleep(1)

def process(url):
    urlQueue = Queue()
    urlQueue.put(url)

    funcs = []
    threads = []
    consumer_num = 1

    for i in range(consumer_num):
        funcs.append(consumer)

    nfuncs = range(len(funcs))

    for i in nfuncs:
        t = MyThread(funcs[i], (urlQueue, i), funcs[i].__name__)
        threads.append(t)

    for i in nfuncs:
        threads[i].start()

    for i in nfuncs:
        threads[i].join()

def main():
    parser = argparse.ArgumentParser("Weixin-spork")
    parser.add_argument('-f', action='store', dest='name_of_file', help='Store an input file')
    parser.add_argument('-s', action='store', dest='starting_url', help='Store an starting url')
    parser.add_argument('--flag', action='store_false', default=False, dest='flag', help='Set a flag')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.starting_url:
        process(args.starting_url)
    elif args.name_of_file:
        pass

if __name__ == '__main__':
    main()

