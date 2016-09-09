#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import re
import sys
import time

import gevent
from gevent import monkey

import urllib2
from urllib2 import urlopen, URLError

import Queue
from Queue import Queue

from bs4 import BeautifulSoup
from random import randint
from urlparse import urlparse, urljoin

import settings
from __global_thread import MyThread

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
        for pattern in settings.urlPatterns:
            if re.match(pattern['url'], url) is not None:
                print(pattern['url'])
                for key in pattern['selector'].keys():
                    print(key, pattern['selector'][key])

                    for link in soup.select(pattern['selector'][key]):
                        link = link.get('href')
                        if link[:4] != 'http' and link.find(r'://') == -1:
                            link = urljoin(url, link)
                        urlQueue.put(link)
                        print("URL", link, 'adds to queue, size is', urlQueue.qsize())

        '''
        for link in soup.select(".pagedlist_item a[class='question_link']"):
            link = link.get('href')
            if link[:4] != 'http' and link.find(r'://') == -1:
                link = urljoin(url, link)
            urlQueue.put(link)
            print("URL", link, 'adds to queue, size is', urlQueue.qsize())

        for pageLink in soup.select(".w4_5 span a"):
            pageLink = pageLink.get('href')
            if pageLink[:4] != 'http' and pageLink.find(r'://') == -1:
                pageLink = urljoin(url, pageLink)
            urlQueue.put(pageLink)
            print("URL", pageLink, 'adds to queue, size is', urlQueue.qsize())
        '''

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

