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
class TaskThread(threading.Thread):
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

''' Task queue '''
class TaskQueue(object):
    def __init__(self, url, finishedUrls):
        self.waitingUrls = [url]
        self.finishedUrls = finishedUrls

    def pop(self):
        return self.waitingUrls.pop()

    def append(self, url):
        if url not in self.waitingUrls:
            self.waitingUrls.append(url)

    def feedback(self, url):
        self.finishedUrls.append(url)

    def size(self):
        return len(self.waitingUrls)

    def backupWaitingUrls(self):
        f = open('waitingUrls.conf', 'w')
        for url in self.waitingUrls:
            f.write(url + '\n')
        f.close()

    def backupFinishedUrls(self):
        f = open('finishedUrls.conf', 'w')
        for url in self.finishedUrls:
            f.write(url + '\n')
        f.close()

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

''' html parser '''
def parse(url, html):
    selectorDict = {}

    selectorDict['base'] = {}
    selectorDict['basic'] = {}
    selectorDict['links'] = []

    selectorDict['base']['website'] = settings.siteName
    selectorDict['base']['srcid'] = md5(url)
    selectorDict['base']['srclink'] = url

    for pattern in settings.urlPatterns:
        if re.match(pattern['url'], url) is not None:
            selectorDict['store'] = pattern['store']
            
            soup = BeautifulSoup(html, "html.parser")
            for key in pattern['selector'].keys():
                if key.startswith('links_'):
                    for link in soup.select(pattern['selector'][key]):
                        link = link.get('href')
                        if link[:4] != 'http' and link.find(r'://') == -1:
                            link = urljoin(url, link)
                        selectorDict['links'].append(link)
                else:
                    selectList = soup.select(pattern['selector'][key])
                    if len(selectList) and key == 'content':
                        selectorDict['basic'][key] = str(selectList[0])
                    elif len(selectList):
                        selectorDict['basic'][key] = selectList[0].string.strip()
                    else:
                        selectorDict['basic'][key] = ''
            break

    return selectorDict

''' save article '''
def save(article):
    f = open('artile.dat', 'a')
    f.write(article + '\n')
    f.close()

def consumer(urlQueue, nThread):
    print('Consumer (%d) starts...' % nThread)
    while urlQueue.size():
        url = urlQueue.pop()
        print('Consumer (%d) gets the task: %s, (%s) tasks remained...' % (nThread, url, urlQueue.size()))

        reply = download(url)
        if reply.startswith('***'):
            print(reply, '...skipping parse')
            continue

        urlQueue.feedback(url)

        selectorDict = parse(url, reply)
        if selectorDict['store']:
            save(json.dumps(selectorDict))

        for link in selectorDict['links']:
            urlQueue.append(link)

        if urlQueue.size():
            time.sleep(settings.downloadInterval)

def process(url):
    funcs = []
    threads = []
    consumer_num = 1

    urlQueue = TaskQueue(url, [])

    for i in range(consumer_num):
        funcs.append(consumer)

    nfuncs = range(len(funcs))

    for i in nfuncs:
        t = TaskThread(funcs[i], (urlQueue, i), funcs[i].__name__)
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

