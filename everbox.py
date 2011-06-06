#!/usr/bin/env python
#-*- coding: utf-8 -*-

import httplib2
from urllib import urlencode
import math, time
import logging
import os
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s:%(lineno)d %(message)s')

def debug(msg, *args, **kargs):
    logging.debug(msg, *args, **kargs)

def get_csrf(html):
    """
    <meta name="csrf-param" content="authenticity_token" />
    <meta name="csrf-token" content="VoW6gcweDDOAhvSognTnulLriJZjAAOWnzBzkn3b288=" />
    """
    start = html.find("csrf-param") + len("csrf-param") + 1
    csrf_param = html[start : html.find("/>", start)].split('"')[1]

    start = html.find("csrf-token") + len("csrf-token") + 1
    csrf_token = html[start : html.find("/>", start)].split('"')[1]
    return csrf_param, csrf_token

def local_to_utc(t):
    """Make sure that the dst flag is -1 -- this tells mktime to take daylight
    savings into account"""
    secs = time.mktime(t)
    return time.gmtime(secs)

def utc_to_local(t):
    secs = calendar.timegm(t)
    return time.localtime(secs)

def getutctime():
  return int(math.floor(time.time()))

def urlencode_array(arr_name, param):
    if type(param).__name__ == 'str':
        return urlencode({arr_name: param})
    elif type(param).__name__ == 'list':
        s = None
        for d in param:
            if s == None:
                s = urlencode({arr_name: d})
            else:
                s = s + '&' + urlencode({arr_name: d})
        return s

class everbox_client():
    def __init__(self):
        self.csrf_param = None
        self.csrf_token = None
        self.h = httplib2.Http(".cache")
        self.headers = dict()
        self.headers['User-Agent'] = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.17) Gecko/20110420 Firefox/3.6.17'
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        self.headers['Accept-Language'] = 'en-us,en;q=0.5'
        self.headers['Accept-Encoding'] = 'gzip,deflate'
        self.headers['Keep-Alive'] = '115'
        self.headers['Connection'] = 'keep-alive'
        #self.header['Referer'] = 'http://www.everbox.com/'

    def getcookie(self, name):
        val = ''
        try:
            cookie = self.headers['Cookie']
            s =cookie.find(name)
            val = cookie[s : cookie.find(';', s)].split('=')[1]
        finally:
            return val

    def process(self, resp, content):
        if 'Cookie' in resp:
            self.headers['Cookie'].join( resp['set-cookie'])
        else:
            self.headers['Cookie'] = resp['set-cookie']
        if 'referer' in resp:
            self.headers['Referer'] = resp['referer']
        if resp['content-length'] > 0 and 'content-type' in resp:
            if resp['content-type'].find('text/html') != -1 and resp['status'] == '200':
                self.csrf_param, self.csrf_token = get_csrf(content)

    def login(self, user=None, pwd=None):
        resp, html = self.h.request("http://www.everbox.com", "GET",
                                         headers=self.headers)
        self.process(resp, html)
        #login
        data = dict(sdo_account='1',
            login=user,
            pwd=pwd,
            rememberme='1',
            submit_new='立即登录')
        data[self.csrf_param] = self.csrf_token
        resp, html = self.h.request("https://www.everbox.com/login", "POST",
                                         body=urlencode(data))
        self.process(resp, html)
        #http status:302
        resp, html = self.h.request("http://www.everbox.com/file", "GET", headers=self.headers)
        self.process(resp, html)

    def logout(self):
        resp, html = self.h.request('http://www.everbox.com/logout', 'GET', headers=self.headers)
        if resp.status != 200:
            raise

    def txtreq(self):
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        if 'Content-Type' in self.headers:
            del self.headers['Content-Type']
        if 'X-Requested-With' in self.headers:
            del self.headers['X-Requested-With']

    def xhr(self):
        self.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        self.headers['Referer'] = 'http://www.everbox.com/file'

    def ls(self, p):
        self.xhr()
        data = dict(path=p)
        data[self.csrf_param] = self.csrf_token
        resp, json = self.h.request('http://www.everbox.com/api/fs/get','POST',
                                       body=urlencode(data), headers=self.headers)
        return json

    def mkdir(self, p):
        self.xhr()
        data = dict(new_path=p, edit_time=getutctime())
        data[self.csrf_param] = self.csrf_token
        resp, json = self.h.request('http://www.everbox.com/api/fs/mkdir', 'POST',
                                    body=urlencode(data),headers=self.headers)
        return json

    def rename(self, p, new_p):
        self.xhr()
        data = dict(path=p, new_path=new_p)
        data[self.csrf_param] = self.csrf_token
        resp, json = self.h.request('http://www.everbox.com/api/fs/rename', 'POST',
                                    body=urlencode(data), headers=self.headers)
        return json

    def mv(self, old_p, dest_p):
        self.xhr()
        data = dict()
        data[self.csrf_param] = self.csrf_token
        data['target_dir'] = dest_p
        body = urlencode(data) + '&' + urlencode_array('old_paths[]', old_p)
        resp, json = self.h.request('http://www.everbox.com/api/fs/move', 'POST',
                                         body, headers=self.headers)
        return json

    def rm(self, p):
        self.xhr()
        data=dict()
        data[self.csrf_param] = self.csrf_token
        body = urlencode(data) + '&' + urlencode_array('paths[]', p)
        resp, json = self.h.request('http://www.everbox.com/api/fs/delete', 'POST',
                                         body, headers=self.headers)
        return json


    def read(self, p, out_dir):
        #self.txtreq()
        self.headers['Referer'] = 'http://www.everbox.com/file'
        data = dict(path=p)
        url = 'http://www.everbox.com/api/fs/download?'+ urlencode(data)


        import subprocess
        wget_cmd = 'wget -q -O ' + out_dir + ' '
        for k, v in self.headers.items():
            wget_cmd += '--header \'' + k + ': ' + v + '\' '
        wget_cmd += '\'' + url + '\''
        subprocess.Popen(wget_cmd, shell=True)
        resp, html = self.h.request('http://www.everbox.com/api/fs/download?'+
                                    urlencode(data), 'GET', headers=self.headers)
        #status:302
        if resp['status'] == '302':
            process(html)
            return self.h.request(resp['location'], 'GET', headers=self.headers)
        elif resp['status'] == '200':
            return resp, html
        else:
            raise

    def swfupload_hdr(self):
        hdr = dict()
        hdr['Accept'] = 'text/*'
        hdr['Content-Type'] = 'multipart/form-data; boundary=----------gL6GI3GI3Ij5Ef1GI3ei4ae0ei4gL6'
        hdr['User-Agent'] = 'Shockwave Flash'
        hdr['Host'] = 'www.everbox.com'
        hdr['Connection'] = 'Keep-Alive'
        hdr['Cache-Control'] = 'no-cache'
        hdr['Cookie'] = self.headers['Cookie']
        return hdr

    def swfupload_data(self, path, target_dir):
        f = open(path, 'rb')
        try:
            data = f.read()
        finally:
            f.close()

        filename = os.path.basename(path)
        boundary = '------------gL6GI3GI3Ij5Ef1GI3ei4ae0ei4gL6'
        body = StringIO()
        body.write('%s\r\n' % boundary)
        body.write('Content-Disposition: form-data; name="Filename"\r\n\r\n')
        body.write('%s\r\n%s\r\n' % (filename, boundary))
        body.write('Content-Disposition: form-data; name="target_dir"\r\n\r\n')
        body.write('%s\r\n%s\r\n' % (target_dir, boundary))
        body.write('Content-Disposition: form-data; name="Filedata"; filename="%s"\r\n' % filename)
        body.write('Content-Type: application/octet-stream\r\n\r\n')
        body.write(data)
        body.write('\r\n%s\r\n' % boundary)
        body.write('Content-Disposition: form-data; name="Upload"\r\n\r\n')
        body.write('Submit Query\r\n%s--' % boundary)
        return body.getvalue()

    def write(self, path, target_dir):
        hdr = self.swfupload_hdr()
        data = self.swfupload_data(path, target_dir)
        hdr['Content-Length'] = str(len(data))
        url = urlencode({'_session_id' : self.getcookie('_session_id'),
                         self.csrf_param : self.csrf_token})
        #resp, html = self.h.request('http://www.everbox.com/api/fs/upload?'+url, 'POST',
        #                            headers=hdr, body=data)

        resp, html = self.h.request('http://www.everbox.com/async_upload?'+url, 'POST',
                                    headers=hdr, body=data)

        return resp, html


    def swfupload_multiformdata(self, path, target_dir):
        filename = os.path.basename(path)
        boundary = '------------gL6GI3GI3Ij5Ef1GI3ei4ae0ei4gL6'
        body = StringIO()
        body.write('%s\r\n' % boundary)
        body.write('Content-Disposition: form-data; name="Filename"\r\n\r\n')
        body.write('%s\r\n%s\r\n' % (filename, boundary))
        body.write('Content-Disposition: form-data; name="target_dir"\r\n\r\n')
        body.write('%s\r\n%s\r\n' % (target_dir, boundary))
        body.write('Content-Disposition: form-data; name="Filedata"; filename="%s"\r\n' % filename)
        body.write('Content-Type: application/octet-stream\r\n\r\n')

        body2 = StringIO()
        body2.write('\r\n%s\r\n' % boundary)
        body2.write('Content-Disposition: form-data; name="Upload"\r\n\r\n')
        body2.write('Submit Query\r\n%s--' % boundary)
        return body.getvalue(), body2.getvalue()

    def write2(self, path, target_dir):
        if not os.path.isfile(path):
            raise

        hdr = self.swfupload_hdr()
        form1, form2 = self.swfupload_multiformdata(path, target_dir)
        hdr['Content-Length'] = str(len(form1) + len(form2) + os.path.getsize(path))

        url = urlencode({'_session_id' : self.getcookie('_session_id'),
                         self.csrf_param : self.csrf_token})
        f = UploadFile(form1, form2, path)
        resp, html = self.h.request('http://www.everbox.com/async_upload?'+url, 'POST',
                                    headers=hdr, body=f)
        return resp, html

class UploadFile():
    def __init__(self, f1, f2, path):
        self.multiform1 = f1
        self.multiform2 = f2
        self.path = path
        self.f1_len = len(self.multiform1)
        self.f2_len = len(self.multiform2)
        self.f1_cur = 0
        self.f2_cur = 0

        self.size = os.path.getsize(path)
        self.fd = open(path, 'rb')

    def read(self, size):
        len = 0
        data = ''
        if self.f1_cur < self.f1_len:
            l, data = self.read_f1(size)
            len = len + l

        if (len < size) and (self.fd.tell() < self.size):
            #l, d = self.fd.read(size - len)
            pos = self.fd.tell()
            data = data + self.fd.read(size - len)
            l = self.fd.tell() - pos
            len = len + l

        if (len < size) and (self.f2_cur < self.f2_len):
            l, d = self.read_f2(size - len)
            len = len + l
            data = data + d

        if len == 0:
            return None
        else:
            return data

    def read_f1(self, size):
        read = 0
        pos = self.f1_cur
        if self.f1_cur + size <= self.f1_len:
            read = size
        else:
            read = self.f1_len - self.f1_cur
        self.f1_cur = pos + read
        return read, self.multiform1[pos:pos+read]

    def read_f2(self, size):
      read = 0
      pos = self.f2_cur
      if self.f2_cur + size <= self.f2_len:
          read = size
      else:
          read = self.f2_len - self.f2_cur
      self.f2_cur = pos + read
      return read, self.multiform2[pos:pos+read]

    def __del__(self):
        self.fd.close()

