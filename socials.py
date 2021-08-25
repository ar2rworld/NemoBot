from random import random as rnd
import sched
import time
import re
from requests_html import HTMLSession
import requests as req
import os

from twitter2 import twitter_post
from linkedin2 import linkedin
from access_tokens import tokens

def dec(s):
    d={}
    for i in s.split('&'):
        t=i.split('=')
        d[t[0]]=t[1]
    return d

def getDivAttributeValue(line, str):
    value_index = line.index(str)
    value_start = line[line.index(str):].index('"') + 1 + value_index
    value_end = line[value_start:].index('"')
    value = line[value_start: value_start + value_end]
    return value

def findTags(html, tag='', type=''):
    tags = []
    for line in html.split('\n'):
        if '<'+tag in line and type in line:
            try:
                name = getDivAttributeValue(line, 'name')
                value = getDivAttributeValue(line, 'value')
                tags.append({'name' : name, 'value' : value})
            except Exception as e:
                print('findTags() error: ', e)
    return tags

def findValue(s, key):
  try:
    st=s.index(key)+len(key)+2
    end=s[st:].index(',')-1
    #print(s[st:st+end])
    return s[st:st+end].replace('\'', '').replace('\ ', '')[1:]
  except ValueError as v_e:
    print(f'Substring not found, probably smt went wrong also in findValue():\n{v_e}')
    raise v_e
  except Exception as e:
    print(f'Error occured in findValue():\n{e}')
    raise e

def find_to_parameter(html):
  #in js page
  str = '"to":'
  for line in html.split('\n'):
    if str in line:
      #print(line)
      s = line.index(str) + len(str) +1 
      return (line[s : s + line[s : ].index('"')])

def loginVK():
    s3 = HTMLSession()
    i=0
    for i in range(5):
        time.sleep(0.5)
        r3 = s3.get('https://vk.com/')
        d={}
        for tag in findTags(r3.text, 'input', 'hidden'):
            d[tag['name']]=tag['value']
        #You email/phone and password
        d['email'] = tokens['vk']['email']
        d['pass']=tokens['vk']['pass']
        to = find_to_parameter(r3.text)
        print(d)
        url='https://login.vk.com/?act=login'
        r3=s3.post(url, data=d)
        #print(r3.headers)
        has_sid = 'remixsid' in r3.headers['Set-Cookie']
        #print('remixsid : ', has_sid)
        if has_sid:
            uid = findValue(r3.text, 'uid')
            return (s3, uid)
    print(f'loginVk() didnot work, attemps: {i}')
    return (None, None)
#loginVK()

def make_post(session, uid, hash, message='testing'):
    post='act=post&to_id=' +str(uid)+ '&type=all&friends_only=&best_friends_only=&close_comments=0&mute_notifications=0&mark_as_ads=0&official=&signed=&hash=' +hash+ '&from=&fixed=461&update_admin_tips=0&al=1'
    data_post=dec(post)
    data_post['Message'] = message
    r0=session.post('https://vk.com/al_wall.php?act=post',data=data_post)
    return r0.text

def post(update, context):
    #print(update.message.chat.id, os.getenv('tg_my_id'))
    if str(update.message.chat.id) == str(os.getenv('tg_my_id')) and len(update.message.text.split(' '))>1:
        message=update.message.text
        first_token = message.split(' ')[1]
        out=''
        if '-' in first_token:
            second_space = message.index(' ', message.index(' ')+1)
            if 'li' in first_token:
                message = message[second_space:]
                out += linkedin(message) +'\n'
            if 'vk' in first_token:
                s, uid = loginVK()
                response0 = s.get('https://oauth.vk.com/authorize?client_id=7888891&display=page&redirect_uri=https://vk.com/ar2r.life&scope=8192&response_type=token&v=5.131&state=123456') 
                #print(response0.text)
                my_page_url='https://vk.com/id'+str(uid)
                #print(my_page_url)
                req_my_page = s.get(my_page_url)
                post_hash = findValue(req_my_page.text, 'post_hash')
                update.message.chat.send_message('logged in:'+uid)
                message = message[second_space:]
                if(s != None):
                    out += make_post(s, uid, post_hash, message) +'\n'
            if 'tw' in first_token:
                twitter_post(message)
            update.message.chat.send_message(out+'worked!')
        else:
            update.message.chat.send_message('-[li][vk][tw] <message> required!')
    else:
        update.message.chat.send_message('You are not my architector')
