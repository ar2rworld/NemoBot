from bs4 import BeautifulSoup as bs
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

def findValue(s, key):
    try:
        st=s.index(key)+len(key)+2
        end=s[st:].index(',')-1
        #print(s[st:st+end])
        return s[st:st+end].replace('\'', '').replace('\ ', '')[1:]
    except Exception as e:
        print(f"error: {e} with key : {key}")

def loginVK():
    s3 = HTMLSession()
    r3=s3.get('https://vk.com/im')
    soup = bs(r3.text, 'html.parser')
    payload3=soup.find('form').get('action').split('&')[1:]
    d={}
    input3=soup.find('form').findAll('input', type='hidden')
    for i in input3:
        #print(i.attrs['name'],i.attrs['value'])
        d[i.attrs['name']]=i.attrs['value']
    #You email/phone and password
    d['email'] = tokens['vk']['email']
    d['pass']=tokens['vk']['pass']
    #print(d)
    url='https://login.vk.com/?act=login'
    r3=s3.post(url, data=d)
    uid = findValue(r3.text, 'uid')#237125584
    request=s3.get('https://vk.com/im')
    tempPage=request.text
    with open('1.html', 'w') as f:
        f.write(tempPage)
        f.close()
    starting=tempPage.index('<title>')
    #print(tempPage[starting: starting+100])
    return (s3, uid)

def make_post(session, uid, hash, message='testing'):
    post='act=post&to_id=' +str(uid)+ '&type=all&friends_only=&best_friends_only=&close_comments=0&mute_notifications=0&mark_as_ads=0&official=&signed=&hash=' +hash+ '&from=&fixed=461&update_admin_tips=0&Message=' +str(message)+ '&al=1'
    data_post=dec(post)
    r0=session.post('https://vk.com/al_wall.php?act=post',data=data_post)
    #print(r0.text)

def post(update, context):
    #print(update.message.chat.id, os.getenv('tg_my_id'))
    if str(update.message.chat.id) == str(os.getenv('tg_my_id')) and len(update.message.text.split(' '))>1:
        s, uid = loginVK()
        response0 = s.get('https://oauth.vk.com/authorize?client_id=7888891&display=page&redirect_uri=https://vk.com/ar2r.life&scope=8192&response_type=token&v=5.131&state=123456') 
        print(response0.text)
        my_page_url='https://vk.com/id'+str(uid)
        #print(my_page_url)
        req_my_page = s.get(my_page_url)
        post_hash = findValue(req_my_page.text, 'post_hash')
        message=update.message.text
        first_token = message.split(' ')[1]
        out=''
        if '-' in first_token:
            second_space = message.index(' ', message.index(' ')+1)
            if 'l' in first_token:
                message = message[second_space:]
                out += linkedin(message) +'\n'
        else:
            message = message[message.index(' ') : ]
        message = message.strip()   
        twitter_post(message)
        #print(post_hash)
        if s!=-1:
            update.message.chat.send_message('logged in:'+uid)
            #if len(message.split(' '))>1:
            make_post(s, uid, post_hash, message)
            update.message.chat.send_message(out+'worked!')
            #else:
            #    update.messsage.chat.send_message('put some content')
        else:
            update.message.chat.send_message(out+'did not worked(')
            
    else:
        update.message.chat.send_message('You are not my architector')

