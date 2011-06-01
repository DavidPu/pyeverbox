#!/usr/bin/env python
# -*- coding: utf-8 -*-
username='your everbox id'
password='your password'

import everbox

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

def dir_walker(arg, dirname, names):
    print arg
    print dirname
    print names
    
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
        print 'write %s to %s' % (src, os.path.dirname(dest))
        eb.write2(src, os.path.dirname(dest))

def upload(src, dest):
    eb = everbox.everbox_client()
    eb.login(user=username, pwd=password)
    do_upload(src, dest)

do_upload(os.path.expanduser('/usr/src/linux-2.6'), '/home/linux-2.6')    
#do_upload(os.path.expanduser('~/Documents'), '/home/Documents')
#do_upload(os.path.expanduser('~/testsuite/everbox'), '/home/everbox')
#eb.read(os.sys.argv[1], os.sys.argv[2])
#print resp
eb.logout()

