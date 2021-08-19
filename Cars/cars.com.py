#coding:utf8
import datetime
import time
import logging
import requests
from lxml import etree
import pymysql as mysql
import traceback
from time import sleep

# --------------------------------------------------------------------------------------------------------------------------------

# No Preference
any = ''

# Body style
SUV = 20217
Sedan = 20211
Regular_Cab_Pickup = 20210
Extended_Cab_Pickup = 20209
Crew_Cab_Pickup = 20218
Convertible = 20202
Coupe = 20203
Hatchback = 20206
Wagon = 20216
Minivan = 20220
Passenger_Van = 20212
Cargo_Van = 20214

# Sort by
price_highest = 'price-highest'
price_lowest = 'price-lowest'
mileage_highest = 'mileage-highest'
mileage_lowest = 'mileage-lowest'
year_newest = 'year-newest'
year_oldest = 'year-oldest'
distance_nearest = 'distance-nearest'
photos_most = 'photos-most'
newest_date_listed = 'listed-newest'

'''Mileage
10,000mi = 28868
20,000mi = 28867
30,000mi = 28866
40,000mi = 28865
50,000mi = 28864
60,000mi = 28863
70,000mi = 28862
80,000mi = 28861
90,000mi = 28860
100,000mi = 28859
100,000mi+ = 28858
Enter the corresponding values into variable "mileage"
'''

# Seller Type
dealer = 28878
individual = 28879

# --------------------------------------------------------------------------------------------------------------------------------

'''
Search Criteria ------------------------------------------------------------------------------------------------------------------
'''

price_min = 0
price_max = 11000
sort_by = newest_date_listed
search_radius = 75
zip_code = 27514
body_style = [Convertible, Sedan, Coupe]
body_style.sort()
miles = 28866
seller_type = dealer

'''
----------------------------------------------------------------------------------------------------------------------------------
'''

logging.basicConfig(filename = 'cars.log', level = logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger('python-logstash-logger')

logger.info(logger.info("start job, time = %s" % datetime.datetime.now()))

bs = ''
for each in body_style:
    ind = 'bsId=%d&' % each
    bs = bs + ind

logger.info('entering website')

url = 'https://www.cars.com/for-sale/searchresults.action/?%smlgId=%d&page=1&perPage=50&prMn=%d&prMx=%d&rd=%d&searchSource=SORT&slrTypeId=%d&sort=%s&stkTypId=28881&zc=%d'\
      % (bs, miles, price_min, price_max, search_radius, seller_type, sort_by, zip_code)
ccon = requests.get(url)
a = ccon.content
html = etree.HTML(a)
list_cars = html.xpath('//div[@id="srp-listing-rows-container"]/div') # [@class="shop-srp-listings__listing"]

db = mysql.connect(
    user = 'root',
    password = 'sword',
    host = '127.0.0.1',
    database = 'cars',
    charset = 'utf8')
cursor = db.cursor()

car_info = []

for cars in list_cars[:5]:
    list = {}
    a = cars.xpath('./div')[0]
    phone_number = a.xpath('./div[@class="listing-row__dealer-info-mobile"]/div/a/@href')[0]
    phone_number = phone_number.replace('tel:', '')
    car = a.xpath('./div[@class="listing-row__details"]/h2/a/text()')[0]
    car = car.replace('\n', '').replace('  ', '')
    price = a.xpath('./div[@class="listing-row__details"]/span[@class="listing-row__price"]/text()')[0]
    price = price.replace(',', '')
    mileage = a.xpath('./div[@class="listing-row__details"]/span[@class="listing-row__mileage"]/text()')[0]
    mileage = mileage[mileage.find(': ') + 2:].replace(',', '')
    owner = a.xpath('./div[@class="listing-row__details"]/span[@class="listing-row__dealer-name listing-row__dealer-name-mobile"]/a/span/text()')[0]
    location = a.xpath('./div[@class="listing-row__details"]/span[@class="listing-row__dealer-name listing-row__dealer-name-mobile"]/span/text()')[0]
    location = location.replace('\n', '').replace('  ', '')
    market = 'Need Car Fax, wait until back to America'
    date = time.strftime('%Y-%m-%d')
    try:
        review = a.xpath('./div[@class="listing-row__details"]/span[@class="listing-row__dealer-name listing-row__dealer-name-mobile"]/span/div[@class="dealer-rating-stars"]/text()')[0]
        review = review.replace('\n', '').replace('  ', '')
    except:
        review = 'No review available'
    try:
        color = a.xpath('./div[@class="listing-row__details"]/p[1]/span/text()')[0]
    except:
        color = 'No color available'
    try:
        interior = a.xpath('./div[@class="listing-row__details"]/p[1]/span[2]/text()')[0]
    except:
        interior = 'No interior available'
    try:
        drive = a.xpath('./div[@class="listing-row__details"]/p[2]/span[2]/text()')[0]
    except:
        drive = 'Drive not available'
    info = a.xpath('./div[@class="listing-row__details"]/h2/a/@href')[0]
    info = 'https://www.cars.com' + info

    u = requests.get(info)
    specs = u.content
    w = etree.HTML(specs)
    # comparison = w.xpath('//div[@class="vdp-pricing-compare__summary-chart-wrapper"]/div[@class="vdp-pricing-compare__summary-chart-data"]/span[@class="vdp-pricing-compare__summary-chart-data__diff-from-avg summary-detail"]/text()')

    list['phone_number'] = phone_number
    list['car'] = car
    list['price'] = price
    list['mileage'] = mileage
    list['owner'] = owner
    list['location'] = location
    list['review'] = review
    list['color'] = color
    list['interior'] = interior
    list['drive'] = drive
    list['info'] = info
    list['date'] = date
    list['market'] = market
    car_info.append(list)

    try:
        sql = 'INSERT INTO car_info(date, car, price, market, mileage, owner, phone, location, color, interior, drive, info, review) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (str(date), car, str(price), market, str(mileage), owner, phone_number, location, color, interior, drive, info, review))
        db.commit()
        logger.info('successfully loaded data into mysql server')
        logger.error('new car: car = %s, price = %s, market = %s, mileage = %s, location = %s, info = %s' % (car, price, market, mileage, location, info))

    except:
        logger.debug('unable to load data into mysql server')
        logger.debug(traceback.format_exc())

    time.sleep(5)
