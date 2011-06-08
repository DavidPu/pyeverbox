#!/usr/bin/env python
#-*- coding: utf-8 -*-

import optparse
import everbox
import os
import time
import json
import ConfigParser
import getpass

'''
breadth first.
isdir(x) and isdir(y) === > x==y, return 0
isdir(x) and isfile(y) ===> x  > y, return 1
isfile(x) and isfile(y) ==> cmp(filesize(x,y))
'''

def eb_isdir(t):
    if (t & 0x2) != 0:
        return True
    else:
        return False

def eb_isfile(t):
    if (t & 0x1) != 0:
        return True
    else:
        return False

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
            js = json.loads(eb.mkdir(l))
            print 'mkdir %s --- status:%d' % (l, js['code'])
        
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
        resp, c = eb.write2(src, dst)
        print 'write %s to %s ---status:%s' % (src, dst, resp['status'])
    else:
        print "%s is not a file or dir." % src
        return {'status':-1,}, None

def do_list(eb, opt, path, level=0):
    js = eb.ls(path)
    ret = json.loads(js)
    if 'data' in ret:
        data = ret['data']
    else:
        return None
    
    t = data['type']
    
    if (eb_isdir(t)):
        for item in data['entries']:
            if eb_isdir(item['type']) and item['fileCount'] > 1:
                item['entries'] = do_list(eb, opt, item['path'], level + 1)['entries']
    else:
        if eb_isfile(t):
            print "file: %s" % path
        else:
            print "oops.."

    return data
            

def dump(data):
    if eb_isdir(data['type']):
        entries = data['entries']
        if type(entries).__name__ == 'dict':
            t = list()
            t.append(entries)
            entries = t
            
        for item in entries:
            if eb_isdir(item['type']) and item['fileCount'] > 1:
                dump(item)
            else:
                print item['path']
    
    
def list(eb, opt, args):
    data = do_list(eb, opt, args[0])
    print "loaded==", type(data)
    print data
    #dump(data)

def upload(eb, opt, args):
    dst = args[-1:][0]
    for i in args[0:len(args)-1]:
        do_upload(eb, i, dst)
    

commands={
    'upload':upload,
    'list':list,
    'ls':list
}


def process(eb, opt, args):
    if commands.has_key(args[0]):
        if len(args) < 2:
            return
        commands[args[0]](eb, opt, args[1:])
        
def load_config(reset=False):
    cfg_file = os.path.expanduser('~/.pyeverbox/config')
    config = ConfigParser.ConfigParser()
    try:
        if reset:
            raise
        fd = open(cfg_file, "r")
        config.readfp(fd)
        fd.close()
        id = config.get('account', 'id')
        pwd = config.get('account', 'password')
    except:
        if not os.path.isdir(os.path.dirname(cfg_file)):
            os.makedirs(os.path.dirname(cfg_file))
        fd = open(cfg_file, "w+")
        id = raw_input("everbox id:")
        pwd = getpass.getpass()
        config.add_section('account')
        config.set('account', 'id', id)
        config.set('account', 'password', pwd)
        config.write(fd)
        fd.close()
    return id, pwd
    
def main():
    usage = "usage: %prog [options] arg"
    parser = optparse.OptionParser(usage)

    (options, args) = parser.parse_args()
    print options
    print args
    eb = everbox.everbox_client()    
    trycount = 0
    user, password = load_config()
    while trycount < 5:
        if not eb.login(user=user, pwd=password):
            trycount += 1
            time.sleep(1)
            user, password = load_config(reset=True)
        else:
            break

    process(eb, options, args)

if __name__ == '__main__':
    main()