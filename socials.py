from bs4 import BeautifulSoup as bs
from random import random as rnd
import sched
import time
import json
import re
from requests_html import HTMLSession
from twitter2 import twitter_post
import os

def dec(s):
    d={}
    for i in s.split('&'):
        t=i.split('=')
        d[t[0]]=t[1]
    return d

def findValue(s, key):
    st=s.index(key)+len(key)+2
    end=s[st:].index(',')-1
    #print(s[st:st+end])
    return s[st:st+end].replace('\'', '').replace('\ ', '')[1:]

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
    d['email']=os.getenv('vk_email')
    d['pass']=os.getenv('vk_pass')
    #print(d)
    url='https://login.vk.com/?act=login'
    r3=s3.post(url, data=d)
    uid = findValue(r3.text, 'uid')
    request=s3.get('https://vk.com/im')
    tempPage=request.text
    starting=tempPage.index('<title>')
    if 'мессенджер' in tempPage[starting: starting+50].lower():
        return (s3, uid)
    return -1, -1

def make_post(session, uid, hash, message='testing'):
    post='act=post&to_id=' +uid+ '&type=all&friends_only=&best_friends_only=&close_comments=0&mute_notifications=0&mark_as_ads=0&official=&signed=&hash=' +hash+ '&from=&fixed=461&update_admin_tips=0&Message=' +str(message)+ '&al=1'
    data_post=dec(post)
    r0=session.post('https://vk.com/al_wall.php?act=post',data=data_post)
    #print(r0.text)

def post(update, context):
    #print(update.message.chat.id, os.getenv('tg_my_id'))
    if str(update.message.chat.id) == str(os.getenv('tg_my_id')) and len(update.message.text.split(' '))>1:
        s, uid = loginVK()
        my_page_url='https://vk.com/id'+uid
        #print(my_page_url)
        req_my_page = s.get(my_page_url)
        post_hash = findValue(req_my_page.text, 'post_hash')
        message=update.message.text
        space_index=message.index(' ')
        twitter_post(message[space_index+1:])
        #print(post_hash)
        if s!=-1:
            print('logged in:', uid)
            #if len(message.split(' '))>1:
            make_post(s, uid, post_hash, message[space_index+1:])
            update.message.chat.send_message('worked!')
            #else:
            #    update.messsage.chat.send_message('put some content')
        else:
            update.message.chat.send_message('did not worked(')
            
    else:
        update.message.chat.send_message('You are not my architector')

