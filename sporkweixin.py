#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys
import time
from Queue import Queue

import gevent
from gevent import monkey

listPageUrlFormat = 'http://chuansong.me/account/%s?start=0'

def processAccountInfo(name_of_account):
    urls = []
    listPageUrl = listPageUrlFormat % (name_of_account)
    urls.append(listPageUrl)

def consumer(nThread):
    print 'Consumer (%d) starts...' % nThread
    while True:
        url = urlQueue[nThread-1].get(1)
        print 'Consumer (%d) gets an task...' % nThread

def start():
    funcs = []
    threads = []

    consumer_num = 8

    for i in range consumer_num:
        funcs.append(consumer)

    nfuncs = range(len(funcs))

    for i in nfuncs:
        t = MyThread(funcs[i], (queues, i), funcs[i].__name__)
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
        processAccountInfo(args.name_of_account)
    elif args.name_of_file:
        pass

if __name__ == '__main__':
    main()

