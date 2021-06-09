from flask import Flask, render_template, make_response
from flask import request
import os
import datetime
from datetime import datetime
import pdb
from bson import json_util
import hashlib
from pymongo import MongoClient
from bson.objectid import ObjectId

import calendar

import traceback
from src import myconfig, mylogger
from pprint import pprint

app = Flask(__name__)

# create a logger.
project_root_path = os.getenv("FARMERS_HELPER")
cfg = myconfig.get_config('{}/share/project.config'.format(
    project_root_path))
db_ip = cfg['db']['ip']
db_port = int(cfg['db']['port'])
db_name = cfg['db']['name']
db_client = MongoClient(db_ip, db_port)

db = db_client[db_name]

col_crop = db['Crop']
col_diary = db['Diary']
col_member = db['Member']
col_schedule = db['Schedule']
col_vermin = db['Vermin']

log_directory = cfg['logger'].get('log_directory')
loggers = dict()
loggers['login'] = mylogger.get_logger('login', log_directory)

@app.route('/')
def web_login():
    sess = request.cookies.get('username')
    if not sess:
        return render_template("login.html")
    else:
        username = request.cookies.get('username')
        user = col_member.find_one({'username': username})
        crop = col_crop.find_one({'_id': user['Crop']})
        
        return render_template('index.html', username=user['name'], usercrop=crop['name'])

@app.route('/member')
def member():
    return render_template("member.html")

@app.route('/help')
def web_help():
    return render_template("help.html")

@app.route('/handle-login', methods=["POST"])
def handle_login():
    username = request.form['username']
    password = request.form['password']
    
    user = col_member.find_one({'username': username})
    if not user:
        return {'statusCode': 400, 'msg': '아이디 오류'}
    if convert_to_SHA256(password) != user['password']:
        return {'statusCode': 400, 'msg': '패스워드 오류'}
    
    return {'statusCode': 200}

@app.route('/handle-register', methods=["POST"])
def handle_register():
    try:
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        Crop = request.form['Crop']
        phone = request.form['phone']
        address = request.form['address']
        
        if not (username and password and name and Crop and phone and address):
            return {'statusCode': 400, 'msg': '정보부족'}
        
        if col_member.find_one({'username': username}):
            return {'statusCode': 400, 'msg': '아이디 중복'}

        info = {
            'username' : username,
            'password' : convert_to_SHA256(password),
            'name' : name,
            'Crop' : col_crop.find_one({'name' : Crop})['_id'],
            'phone' : phone,
            'address' : address
        }

        col_member.insert(info)
        return {'statusCode': 200}
    except:
        return {'statusCode': 500, 'msg': '서버에러'}

@app.route('/information', methods=['GET'])
def information():
    username = request.cookies.get('username')
    user = col_member.find_one({'username': username})
    if not user:
        return render_template('login.html')
    
    crop = col_crop.find_one({'_id': user['Crop']})
    
    member_info = list(col_member.find({'username' : username}))
    diary_info = list(col_diary.find({'Member': user['_id']}))
    
    info_ret = {}
    for info in member_info:
        info_ret['username'] = info['username']
        info_ret['name'] = info['name']
        phone = info['phone']
        info_ret['phone'] = phone[0:3] + ' - ' + phone[3:7] + ' - ' + phone[7:]
        info_ret['address'] = info['address']
    
    diary_ret = []
    for info in diary_info:
        date = info['date'].strftime('%Y-%m-%d')
        people = info['people']
        duration = info['duration']
        step = col_schedule.find_one({'_id' : info['step'] })['event']
        content = info['content']
        useditem = info['useditem']
        etc = info['etc']
        
        total_info = {'date' : date,
                      'people' : people,
                      'duration' : duration,
                      'step' : step,
                      'content' : content,
                      'useditem' : useditem,
                      'etc' : etc
                     }
        
        diary_ret.append(total_info)
    
    diary_ret.sort(key=lambda x: x['date'])

    return render_template('information.html', usercrop=crop['name'], username=user['name'], 
                           diary_info=diary_ret, info=info_ret)
    
    
@app.route('/vermin', methods=['GET'])
def vermin():
    username = request.cookies.get('username')
    user = col_member.find_one({'username': username})
    if not user:
        return render_template('login.html')
    
    crop = col_crop.find_one({'_id': user['Crop']})
    vermin_data = list(col_vermin.find({'_id': {'$in': crop['Vermin']} }))
    for vermin in vermin_data:
        del vermin['_id']
    
    return render_template('vermin.html', vermin_data=vermin_data, usercrop=crop['name'], username=user['name'])
     
@app.route('/diary', methods=["GET"])
def diary():
    username = request.cookies.get('username')
    user = col_member.find_one({'username': username})
    if not user:
        return render_template('login.html')
    
    crop = col_crop.find_one({'_id': user['Crop']})
    schedule_data = list(col_schedule.find({'_id': {'$in': crop['Schedule']}, 'category': '생육과정(주요농작업)'}))
    schedule = ''.join([
        '<option value="%s">%s</option>' %(str(sch['_id']), sch['event'])
        for sch in schedule_data
    ])
    
    return render_template('diary.html', schedule=schedule, username=user['name'], usercrop=crop['name'])

@app.route('/handle-diary', methods=['POST'])
def handle_diary():
    try:
        date = request.form['date']
        people = request.form['people']
        duration = request.form['duration']
        step = request.form['step']
        content = request.form['content']
        useditem = request.form['useditem']
        etc = request.form['etc']
        
        if not (date and people and duration and step and content and useditem and etc):
            return {'statusCode': 400, 'msg': '정보부족. 모든 정보를 다 입력해주세요!'}
        
        info = {
            'date' : datetime.strptime(date, '%Y-%m-%d'),
            'people' : int(people),
            'duration' : int(duration),
            'step' : ObjectId(step),
            'content' : content,
            'useditem' : useditem,
            'etc' : etc,
            'Member': col_member.find_one({'username': request.cookies.get('username')})['_id']
        }
        print(info)

        col_diary.insert(info)
        
        return {'statusCode': 200} 
    except:
        traceback.print_exc()
        return {'statusCode': 500, 'msg': '서버에러'}
    
@app.route('/schedule', methods=["GET"])
def schedule():
    
    import datetime
    
    username = request.cookies.get('username')
    user = col_member.find_one({'username': username})
    
    if not user:
        return render_template('login.html')
    
    crop = col_crop.find_one({'_id': user['Crop']})
    
    today = datetime.date.today()
    
    year = today.year
    month = today.month
    
    start_day, last_day = calendar.monthrange(year, month)
    
    start_day = datetime.date(year, month, 1)
    start_week = (start_day.weekday() + 1) % 7 # return 0~6 (일 ~ 토)
    
    schedule_data = list(col_schedule.find({'_id': {'$in': crop['Schedule']}, 'category': '생육과정(주요농작업)'}))
    
    events = ['%d' %(i+1) for i in range(last_day)]
    for sch in schedule_data:
        start = sch['start']
        end = sch['end']
        for day in range(1, last_day+1):
            if start <= datetime.datetime(year, month, day) < end:
                events[day-1] += '<br/>' + sch['event']
                
    events = [''] * start_week + events
             
    return render_template('schedule.html', username=user['name'], usercrop=crop['name'], 
                           year=year, month=month, events=events)
    
@app.route('/information', methods=["POST"])
def infomation():
    
    return render_template('information.html')
    
def user_crop():
    crop = request.form['Crop']
    
    return crop
    
def convert_to_SHA256(x):
    """Convert a given string to SHA256-encoded string.
    :param x: arbitrary string.
    :type x: str
    :return: SHA256 encoded string
    :rtype: str
    """
    result = hashlib.sha256(x.encode())
    result = result.hexdigest()
    return result