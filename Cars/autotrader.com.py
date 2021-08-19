# coding:utf-8
import logging
import datetime
import time
from time import sleep
import requests
from lxml import etree
import pymysql as mysql
import traceback

# https://www.autotrader.com/cars-for-sale/Used+Cars/Convertible/BMW/Chapel+Hill+NC-27514?zip=27514&showcaseOwnerId=68422&startYear=2008&filterName=LISTING_TYPES&numRecords=25
# &vehicleStyleCodes=CONVERT%2CSEDAN%2CCOUPE%2CHYBEL%2CAWD4WD%2CSUVCROSS&endYear=2018
# &makeCodeList=BMW%2CCHEV%2CDODGE&sellerTypes=d%2Cp&listingTypes=used%2Ccertified%2Cnew&sortBy=distanceASC&maxPrice=12000&firstRecord=0&searchRadius=25



# Sort by
year_newest = 'yearDESC'
year_oldest = 'yearASC'
price_highest = 'derivedpriceDESC'
price_lowest = 'derivedpriceASC'
mileage_lowest = 'mileageASC'
mileage_highest = 'mileageDESC'
distance_closest = 'distanceASC'
distance_farthest = 'distanceDESC'

# Body style
Sedan = 'sedan'
Coupe = 'coupe'
Convertible = 'convert'
HybridElectric = 'hybel' # Hybrid/Electric
AWD = 'awd4wd' # All wheel drive/4 wheel drive
SUV = 'suvcross' # SUV/Crossover

'''
Make : Use the names in the parenthesis for make name, otherwise, use normal name inside ''

Chevrolet = 'chev'
Porche = 'por'
Benz = 'mb'
Volkswagen = 'volks'
'''

# Seller type
dealer = 'd'
private = 'p'

# Sell tyle
Used = 'used'
Certified = 'certified'
New = 'new'

'''
Search Criteria ------------------------------------------------------------------------------------------------------------------
'''

make = ['']
body_style = [Sedan, Coupe, Convertible]
zip_code = 27514
city = 'Chapel Hill'
state = 'NC'
year_min = 2008
year_max = 2018
price_max = 12000
seller_type = [dealer, private]
radius = 75
type = [Used, Certified]
sort_by = year_newest

'''
----------------------------------------------------------------------------------------------------------------------------------
'''

city = city.replace(' ', '+')
place = city + '+' + state + '-' + str(zip_code)

# ----------------------------------------------
for index, a in enumerate(body_style):
    b = a.upper()
    body_style[index] = b
bodystyle = body_style.sort()

body = ''
for bs in body_style:
    body += '%2C' + bs

body = body[body.find('%2C') + 3:]

# ----------------------------------------------
for index, c in enumerate(make):
    d = c.upper()
    make[index] = d

mk = ''
for m in make:
    mk += '%2C' + m

mk = mk[mk.find('%2C') + 3:]

# ----------------------------------------------
st = ''
for s in seller_type:
    st += '%2C' + s

st = st[st.find('%2C') + 3:]

# ----------------------------------------------
lt = ''
for l in type:
    lt += '%2C' + l

lt = lt[lt.find('%2C') + 3:]

# ----------------------------------------------
url = 'https://www.autotrader.com/cars-for-sale/Used+Cars/%s?zip=%s&showcaseOwnerId=68422&startYear=%s&filterName=LISTING_TYPES&numRecords=25&vehicleStyleCodes=%s&endYear=%s' \
'&makeCodeList=%s&sellerTypes=%s&listingTypes=%s&sortBy=%s&maxPrice=%s&firstRecord=0&searchRadius=%s' % (place, zip_code, year_min, body, year_max, mk, st, lt, sort_by, price_max, radius)
r = requests.get(url)
atcom = r.text

# https://www.autotrader.com/cars-for-sale/vehicledetails.xhtml?listingId=456937074&zip=27514&referrer=%2Fcars-for-sale%2Fsearchresults.xhtml%3Fzip%3D27514%26showcaseOwnerId%3D68422%26startYear%3D2008%26vehicleStyleCodes%3DCONVERT%252CCOUPE%252CSEDAN%26incremental%3Dall%26endYear%3D2018%26makeCodeList%3DBMW%252CCHEV%252CPOR%252CFORD%26sellerTypes%3Dd%252Cp%26listingTypes%3Dused%252Ccertified%26sortBy%3DyearDESC%26maxPrice%3D12000%26firstRecord%3D0%26searchRadius%3D75&sellerTypes=d%2Cp&listingTypes=used%2Ccertified&startYear=2008&numRecords=25&maxPrice=12000&vehicleStyleCodes=CONVERT%2CCOUPE%2CSEDAN&firstRecord=0&endYear=2018&makeCodeList=BMW%2CCHEV%2CPOR%2CFORD&searchRadius=75&makeCode1=CHEV&modelCode1=SONIC
