# coding:utf-8
import datetime
import logging
import requests
from lxml import etree
import traceback
import time
import pymysql as mysql

make = ['']
model = ['']
body_style = ['sedan', 'coupe']
city = 'Chapel Hill' # case sensitive
city = city.replace(' ', '+')
state = 'NC'
location = city + '%2C+' + state
search_radius = 75
miles = 530000
year_min = 2008
year_max = 2018
price_min = 0
price_max = 13000
sort = 'mileage'
state = ['used'] # new, used, certified+pre-owned
condition = ''
for each in state:
    add = 'condition%s%s=%s' % ('%5B', '%5D', each)
    condition = condition + add + '&'

md = ''
for each in model:
    app = '%s' % each
    md = md + app

for make in make:
    for style in body_style:
        url = 'https://www.autolist.com/listings#body_type=%s&location=%s&radius=%d&price_min=%d&price_max=%d&year_min=%d&year_max=%d&%s&mileage=%d&features=&sort_filter=%s&make=%s&model=%s' % (
            style, location, search_radius, price_min, price_max, year_min, year_max, condition, miles, sort, make, md
        )
        r = requests.get(url)
        alcom = r.content
        html = etree.HTML(alcom)
        list_cars = html.xpath('//div[@class="col-lg-8 col-md-8 col-sm-7 col-xs-12"]/div[2]/div/div[2]/div')
        for cars in list_cars:
            list = {}
            car = cars.xpath('./a/div[@class="details"]/h3/div[@class="description"]/div[@class="headline"]/text()')

        print url
        print alcom