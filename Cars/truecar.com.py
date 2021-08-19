# coding:utf-8
import datetime
import time
import requests
import logging
import pymysql as mysql
from lxml import etree
import traceback

'''
Search Criteria ------------------------------------------------------------------------------------------------------------------
'''

make = ['']
body_style = ['sedan', 'coupe', 'convertible']
zip_code = 27514
search_radius = 50
miles = 50000
price_min = 0
price_max = 11000
year_min = 2008
year_max = 2018

'''
----------------------------------------------------------------------------------------------------------------------------------
'''

logging.basicConfig(filename = 'cars.log', level = logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger('python-logstash-logger')

logger.info(logger.info("start job, time = %s" % datetime.datetime.now()))

db = mysql.connect(
    user = 'root',
    password = 'sword',
    database = 'cars',
    host = '127.0.0.1',
    charset = 'utf8'
)
cursor = db.cursor()

car_info = []

for make in make:
    if len(make) > 0:
        make = '/' + make
    else:
        make = ''

    for style in body_style:
        url = 'https://www.truecar.com/used-cars-for-sale/listings%s/body-%s/location-%d/price-%d-%d/year-%d-%d/?mileageHigh=%d&searchRadius=%d' % (
            make, style, zip_code, price_min, price_max, year_min, year_max, miles, search_radius
        )
        r = requests.get(url)
        tccom = r.content
        html = etree.HTML(tccom)
        list_cars = html.xpath('//div[@class="col col-sm-9 no-right-padding"]/span/div/div/div[@data-qa="VehicleCard"]')

        for cars in list_cars[:5]:
            list = {}
            date = time.strftime('%Y-%m-%d')
            car_first = cars.xpath('./div/div[2]/div/div/p/a/span[1]/text()')[0]
            car_latter = cars.xpath('./div/div[2]/div/div/p/a/span[2]/text()')[0]
            car = car_first + car_latter
            color = cars.xpath('./div/div[2]/div/div/ul/li[3]/text()')[1]
            mileage = cars.xpath('./div/div[2]/div/div/ul/li[1]/text()')[1]
            mileage = mileage[:mileage.find('mi')].replace(',', '')
            price = cars.xpath('./div/div[2]/div[2]/div/p[@class="price"]/text()')[0]
            price = price[price.find('$') + 1:].replace(',', '')

            try:
                compare = cars.xpath('./div/div[2]/div[2]/div/p[@class="market-difference hidden-xs"]/text()')[0]
                money = cars.xpath('./div/div[2]/div[2]/div/p[@class="market-difference hidden-xs"]/strong/text()')[0]
                market = money + compare
            except:
                market = 'No market comparison available'
            location = cars.xpath('./div/div[2]/div/div/ul/li[2]/text()')[1]

            try:
                var_interior = cars.xpath('./div/div[2]/div/div/ul/li[4]/text()')[1]
                if var_interior.isalpha():
                    interior = var_interior
                else:
                    interior = 'No interior preview available'

            except:
                interior = 'No interior preview available'

            try:
                review = cars.xpath('./div/div[2]/div[2]/div/p/em/text()')[0]
            except:
                review = 'No review available'

            info = cars.xpath('./div/div[2]/div/div/p/a/@href')[0]
            info = 'https://www.truecar.com' + info

            c = requests.get(info)
            individual = c.content
            specs = etree.HTML(individual)
            drive = specs.xpath('//div[@data-qa="VehicleDetails"]/div/div/div/div[2]/div[2]/ul/li[2]/text()')[1]
            owner = 'Owner not available, see info'
            phone = '0'

            list['date'] = date
            list['car'] = car
            list['price'] = price
            list['market'] = market
            list['mileage'] = mileage
            list['owner'] = owner
            list['phone'] = phone
            list['location'] = location
            list['color'] = color
            list['interior'] = interior
            list['drive'] = drive
            list['info'] = info
            list['review'] = review
            car_info.append(list)

            try:
                sql = 'INSERT INTO car_info(date, car, price, market, mileage, owner, phone, location, color, interior, drive, info, review) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (str(date), car, str(price), market, str(mileage), owner, phone, location, color, interior, drive, info, review))
                db.commit()
                logger.info('successfully loaded data into mysql server')
                logger.error('new car: car = %s, price = %s, market = %s, mileage = %s, location = %s, info = %s' % (car, price, market, mileage, location, info))

            except:
                logger.debug(traceback.format_exc())
                logger.debug('unable to load data into mysql server')

            time.sleep(5)
