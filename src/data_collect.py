import requests
from bs4 import BeautifulSoup
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from urllib import parse

import pymongo
from pymongo import MongoClient

fruits = ['감귤', '단감', '매실', '무화과', '배', 
          '복숭아', '사과', '살구', '양앵두', '유자', 
         '자두', '참다래', '포도']

def get_schedule():
    """Collect farming schedule data from fruit.nihhs.go.kr
    
    :return: pairs of {fruit : farming_schedule}
    :rtype: dict
    """
    addr_list = {
        '감귤'  :   'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30654&sj=%EA%B0%90%EA%B7%A4(%EB%B3%B4%ED%86%B5%20%EC%98%A8%EC%A3%BC%EB%B0%80%EA%B0%90)&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '단감'  :   'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30656&sj=%EB%8B%A8%EA%B0%90&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '매실'  :   'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30658&sj=%EB%A7%A4%EC%8B%A4&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '무화과': 'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30659&sj=%EB%AC%B4%ED%99%94%EA%B3%BC(%EB%85%B8%EC%A7%80%EC%9E%AC%EB%B0%B0)&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '배'    :     'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30661&sj=%EB%B0%B0&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '복숭아': 'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30662&sj=%EB%B3%B5%EC%88%AD%EC%95%84&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '사과'  :   'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30663&sj=%EC%82%AC%EA%B3%BC&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '살구'  :   'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30664&sj=%EC%82%B4%EA%B5%AC&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '양앵두': 'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30665&sj=%EC%96%91%EC%95%B5%EB%91%90&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '유자'  : 'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30666&sj=%EC%9C%A0%EC%9E%90&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '자두'  : 'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30667&sj=%EC%9E%90%EB%91%90&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '참다래': 'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30668&sj=%EC%B0%B8%EB%8B%A4%EB%9E%98&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType',
        '포도'  : 'https://fruit.nihhs.go.kr/common/ajax_local_callback.jsp?farmWorkingPlanNew/workScheduleEraInfoLst?apiKey=20181008H9RSARMLDRREKBRCTEGQ&htmlArea=nongsaroApiLoadingArea2&kidofcomdtySeCode=210002&cntntsNo=30669&sj=%ED%8F%AC%EB%8F%84(%ED%91%9C%EC%A4%80%EA%B0%80%EC%98%A8)&kidofcomdtySeCodeNm=%EA%B3%BC%EC%88%98&serviceType=ajaxType'
    }

    ##### fruit information
    fruit_data = {}
    for fruit in addr_list.keys():
        print(fruit, end = ' ')
        html = requests.get(addr_list[fruit])
        soup = BeautifulSoup(html.content, 'html.parser')

        html = soup.find('div', {'id' : 'nongScheduleTit'})

        title = html.findAll({'h2'})
        contents = html.select('div.m_scrollTable')

        farming_schedule = {}

        for i, content in enumerate(contents):
            content = content.select('tbody td')
            data = []
            for line in content:
                if line.get_text() == '':
                    data.append([0, 'EMPTY'])
                elif line.get_text() != '\xa0':
                    data.append([int(line.attrs['colspan']), line.get_text()])
                else:
                    data.append([1, None]) 

            farming_schedule[title[i].get_text()] = data

        fruit_data[fruit] = farming_schedule
        
    ##### farming schedule
    schedule = {}
    for fruit in fruit_data:
        schedule[fruit] = []
        for category in fruit_data[fruit]:
            start = 0
            for n, text in fruit_data[fruit][category]:
                if text == 'EMPTY':
                    start = 0
                elif text is None:
                    pass
                else:
                    start_date, end_date = parse_date(start, n)
                    schedule[fruit].append({
                        'category': category,
                        'start': datetime.strptime('%04d-%02d-%02d' %(2021, *start_date), '%Y-%m-%d'),
                        'end': datetime.strptime('%04d-%02d-%02d' %(2021, *end_date), '%Y-%m-%d'),
                        'event': text
                    })
                start += n

    return schedule

def parse_date(start, duration):
    """Split farming schedule.
    
    :param start: start date
    :type start: int
    :param duration: farming duration
    :type duration: int
    :return: (start_month, start_day), (end_month, end_day)
    :rtype: tuple, int
    """
    start_month = start // 3 + 1
    start_day = start % 3 * 10 + 1
    end_month = (start + duration) // 3 + 1
    end_day = (start+duration) % 3 * 10 + 1
    if end_month == 13:
        end_month = 12
        end_day = 31
    return (start_month, start_day), (end_month, end_day)


def get_vermin():
    """Collect vermin data from https://ncpms.rda.go.kr/npms/Main.np
    
    :return: pairs of {fruit : vermin_info}
    :rtype: dict
    """

    # apikey for https://ncpms.rda.go.kr/npms/Main.np 
    apiKey = "put your api key"

    # service Code - Detail information in the Open API
    serviceCode = "SVC01"
    serviceCode_detail = 'SVC05'

    serviceType = 'AA001'

    response_element = ['sickNameKor', 'sickNameChn', 'sickNameEng', 'infectionRoute', 'developmentCondition', 
                        'symptoms', 'preventionMethod', 'biologyPrvnbeMth', 'chemicalPrvnbeMth', 'etc']

    ##### vermin information
    vermin = {}
    for fruit in fruits:
        print(fruit, end = ' ')
        res = requests.get('http://ncpms.rda.go.kr/npmsAPI/service',
                           params={
                               'apiKey': apiKey,
                               'serviceCode': serviceCode,
                               'serviceType': serviceType,
                               'cropName': fruit
                           })
        soup = BeautifulSoup(res.content, 'html.parser')

        details = []
        for item in soup.findAll({'item'}):

            res = requests.get('http://ncpms.rda.go.kr/npmsAPI/service',
                               params={
                                    'apiKey': apiKey,
                                    'serviceCode': serviceCode_detail,
                                    'serviceType': serviceType,
                                    'sickKey': item.find('sickkey').text
                                })        
            xml = BeautifulSoup(res.content, "xml") # 대소문자 그대로 가져옴


            detail = {}

            if item.find('sickkey'):
                detail['sickKey'] = item.find('sickkey').text

            for element in response_element:
                detail[element] = xml.find(element).text

            detail['virusImgList'] = [{'title': item_vi.find('imageTitle').text, 
                                       'image': item_vi.find('image').text}
                                      for item_vi in xml.select('virusImgList item')]

            detail['imageList'] = [{'title': item_vi.find('imageTitle').text, 
                                    'image': item_vi.find('image').text}
                                   for item_vi in xml.select('imageList item')]

            detail['virusList'] = [{'name': item_vi.find('virusName').text, 
                                    'sfe': item_vi.find('sfeNm').text}
                                   for item_vi in xml.select('virusList item')]

            details.append(detail)

        vermin[fruit] = details
        
    return vermin

############### input data in mongo ###############

def save_to_db():
    """ave the given {fruit : farming_schedule} and {fruit : vermin_info} pairs to DB"""
    
    client = MongoClient()

    # db & collection creation
    db = client['Farmers_Helper']
    col_crop = db['Crop']
    col_schedule = db['Schedule']
    col_vermin = db['Vermin']
    
    schedule = get_schedule()
    vermin = get_vermin()
    
    schedule_ids = {}
    for fruit in schedule:
        schedule_ids[fruit] = []
        for sch in schedule[fruit]:
            schedule_ids[fruit].append(
                col_schedule.insert(sch)
            )

    vermin_ids = {}
    for fruit in vermin:
        vermin_ids[fruit] = []
        for ver in vermin[fruit]:
            vermin_ids[fruit].append(
                col_vermin.insert(ver)
            )

    for fruit in fruits:
        col_crop.insert({
            'name': fruit,
            'Schedule': schedule_ids[fruit],
            'Vermin': vermin_ids[fruit]
        })            

    client.close()

