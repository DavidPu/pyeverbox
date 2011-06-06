#!/usr/bin/env python
#-*- coding: utf-8 -*-

import optparse
import everbox
import os

'''
breadth first.
isdir(x) and isdir(y) === > x==y, return 0
isdir(x) and isfile(y) ===> x  > y, return 1
isfile(x) and isfile(y) ==> cmp(filesize(x,y))
'''
def cmp_sortdir(x, y):
    if os.path.isdir(x):
        if os.path.isdir(y):
            return 0
        else:
            return 1
    else:
        if os.path.isdir(y):
            return -1
        else:
            return cmp(os.path.getsize(x), os.path.getsize(y))
        
def do_upload(eb, src, dest='/home', level=0):
    if os.path.isdir(src):
        l = '/home'
        dstdirs = dest.split('/')
        for i in range(0, level):
            l += '/' + dstdirs[2+i]
        
        for d in dstdirs[2+level:]:
            l = l + '/' + d
            print eb.mkdir(l)
        
        sdirs=list()
        for d in os.listdir(src):
            sdirs.append(src + '/' + d)
        
        sdirs = sorted(sdirs, cmp=cmp_sortdir)
        for i in sdirs:
            do_upload(eb, i, dest + '/' + os.path.basename(i), level + 1)

    elif os.path.isfile(src):
        if level == 0:
            dst = dest
        else:
            dst = os.path.dirname(dest)
        print 'write %s to %s' % (src, dst)
        return eb.write2(src, dst)
    else:
        print "%s is not a file or dir." % src
        return {'status':-1,}, None


def upload(eb, opt, args):
    dst = args[-1:][0]
    for i in args[0:len(args)-1]:
        do_upload(eb, i, dst)
    
def download(eb, opt, args):
    print "downloading..."
    return

commands=dict()
commands['upload'] = upload
commands['download'] = download

def process(eb, opt, args):
    if commands.has_key(args[0]):
        if len(args) < 2:
            return
        commands[args[0]](eb, opt, args[1:])
        

def main():
    usage = "usage: %prog [options] arg"
    parser = optparse.OptionParser(usage)

    (options, args) = parser.parse_args()
    print options
    print args
    eb = everbox.everbox_client()
    eb.login(user='13795313475', pwd='xUmwcH7kMp')
    process(eb, options, args)

if __name__ == '__main__':
    main()