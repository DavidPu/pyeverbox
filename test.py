#!/usr/bin/env python
# -*- coding: utf-8 -*-

import everbox
import os
import sys
import getpass
import ConfigParser

def load_config():
    cfg_file = os.path.expanduser('~/.pyeverbox/config')
    config = ConfigParser.ConfigParser()
    try:
        fd = open(cfg_file, "r")
        config.readfp(fd)
        id = config.get('account', 'id')
        pwd = config.get('account', 'password')
    except:
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

username, password = load_config()
#username = raw_input("user id:")
#password = getpass.getpass()

eb = everbox.everbox_client()
eb.login(user=username, pwd=password)
print eb.ls('/home')

print '===cookie: _remember_token==='
print eb.getcookie('_remember_token')
print '===cookie: _session_id==='
print eb.getcookie('_session_id')
'''
print eb.mkdir('/home/测试一下啊')
print eb.mkdir('/home/测试一下啊')
print eb.mkdir('/home/aaa')
print eb.mkdir('/home/bbb')
print eb.mkdir('/home/ccc')
#print eb.rename('/home/测试一下啊', '/home/pics')
print eb.mv('/home/ccc', '/home/pics')
print eb.mv(['/home/aaa', '/home/bbb'], '/home/pics')
#print eb.rm('/home/pics')
'''

'''
print "===test read===="
resp, data = eb.read('/home/boot.img')
print resp
if resp['status'] == '200':
    print "====data===="
    open('./boot.img', 'wb').write(data)
'''
'''
p = '/home/试一下啊/11/22/3/4/5/6'
l = '/home'
for d in p.split('/')[2:]:
    l = l +  '/' + d
    print '====', l
    eb.mkdir(l)
'''

'''

import os
arg = os.sys.argv[1]

if os.path.isdir(arg):
    l = '/home'
    for d in arg.split('/')[2:]:
        l = l + '/' + d
        eb.mkdir(l)
elif os.path.isfile(arg):
    eb.write2(os.sys.argv[1], '/home')
else:
    print 'skip ', arg
'''


import os
import time
    
def do_upload(src, dest='/home', level=0):    
    if os.path.isdir(src):
        l = '/home'
        dstdirs = dest.split('/')
        for i in range(0, level):
            l += '/' + dstdirs[2+i]
        
        for d in dstdirs[2+level:]:
            l = l + '/' + d
            print 'mkdir ', l
            print eb.mkdir(l)
            #time.sleep(6)
            
        for i in os.listdir(src):
            do_upload(src + '/' + i, dest + '/' + i, level + 1)
    elif os.path.isfile(src):
        if level == 0:
            dst = dest
        else:
            dst = os.path.dirname(dest)
        print 'write %s to %s' % (src, dst)
        print eb.write(src, dst)

def upload(src, dest):
    do_upload(src, dest)

import json

def do_download(path, level=0):
    ret = json.loads(eb.ls(path))
    if 'data' in ret:
        data = ret['data']
    else:
        return None
    
    t = data['type']
    
    if t == 2:
        for item in data['entries']:
            if item['type'] == 2 and item['fileCount'] > 1:
                item['entries'] = do_download(item['path'], level + 1)['entries']
    return data
            

def dump(data):
    if data['type'] == 2:
        entries = data['entries']
        if type(entries).__name__ == 'dict':
            t = list()
            t.append(entries)
            entries = t
            
        for item in entries:
            if item['type'] == 2 and item['fileCount'] > 1:
                dump(item)
            else:
                print item['path']
    
    
def download(path):
    data = do_download(path, 0)
    print "loaded==", type(data)
    print data
    dump(data)


#download('/home')
#do_upload('.', '/home/yuyuan.tar.bz2')
#eb.write2('/home/pulq/test', '/home', 'haha')
#eb.write2('/home/pulq/test', '/home')
print eb.read('/home/yuyuan.tar.bz2', './dl')
#do_upload(os.path.expanduser('/usr/src/linux-2.6'), '/home/linux-2.6')    
#do_upload(os.path.expanduser('~/Documents'), '/home/Documents')
#do_upload(os.path.expanduser('~/testsuite/everbox'), '/home/everbox')
#eb.read(os.sys.argv[1], os.sys.argv[2])
#print resp
eb.logout()

