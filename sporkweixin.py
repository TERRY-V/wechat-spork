#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys
import time

import gevent
from gevent import monkey

import urllib2
from urllib2 import urlopen, URLError

from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin

import Queue
from Queue import Queue

from __global_thread import MyThread

domainUrl = 'http://chuansong.me'
listPageUrlFormat = 'http://chuansong.me/account/%s?start=0'

def download(url):
    request = urllib2.Request(url)
    request.add_header('User-agent', 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)')
    try:
        reply = urllib2.urlopen(request, timeout=5).read()
    except URLError, e:
        print(e.getcode(), e.geturl(), e.reason)
        print(e.info())
        print(e.read())
        reply = ('*** ERROR: invalid URL "%s"' % url)
    finally:
        return reply

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
        for link in soup.select(".pagedlist_item a[class='question_link']"):
            link = link.get('href')
            if link[:4] != 'http' and link.find(r'://') == -1:
                link = urljoin(url, link)
            urlQueue.put(link)
            print(link)

        time.sleep(1)

def start(name_of_account):
    urlQueue = Queue()
    listPageUrl = listPageUrlFormat % (name_of_account)
    urlQueue.put(listPageUrl)

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
    parser.add_argument('-s', action='store', dest='name_of_account', help='Store an account name')
    parser.add_argument('--flag', action='store_false', default=False, dest='flag', help='Set a flag')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    if args.name_of_account:
        start(args.name_of_account)
    elif args.name_of_file:
        pass

if __name__ == '__main__':
    main()

