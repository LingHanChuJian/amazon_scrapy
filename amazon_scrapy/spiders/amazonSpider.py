#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: linghanchujian

import os,xlrd,scrapy,winreg,re,redis,hashlib,json
from scrapy.http import Request
from scrapy.loader import  ItemLoader
from amazon_scrapy.items import AmazonScrapyItem
from scrapy.http.cookies import CookieJar

class amazonSpider(scrapy.Spider):
    name = 'amazon_scrapy'

    def __init__(self,*args,**kw):
        super().__init__(*args,**kw)
        self.robotCheck = []
        # self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.cookie_jar = CookieJar() 

    def start_requests(self):
        workbook = xlrd.open_workbook(os.path.join(self.getDesktop(),'stay.xlsx'))
        booksheet = workbook.sheet_by_name('Sheet1')
        for row in range(1,booksheet.nrows):
            row_data = []
            for col in range(booksheet.ncols):
                cel = booksheet.cell(row, col)
                val = cel.value
                try:
                    val = cel.value
                    val = val.strip(' ')
                except:
                    pass
                if type(val) != float:
                    val = str(val)
                row_data.append(val)
            yield Request(url='{}/dp/{}'.format(self.getDomainUrl(row_data[0]),row_data[1]),meta={'row_data':row_data})
        
    def parse(self, response):
        row_data = response.meta['row_data']
        l = ItemLoader(item=AmazonScrapyItem(),response=response)
        item_data = ('Marketplace_Name','ASIN')
        for index in range(len(item_data)):
            l.add_value(item_data[index],row_data[index])
        l.add_value('url',response.url)
        if response.status == 404:
            # l.add_value('lower_frame','是')
            # l.add_value('comment_num',0)
            # l.add_value('stars',0)
            l.add_value('is_404',404)
            l.add_value('is_robot','')
        else:
            robot = response.xpath("//title[@dir='ltr']/text()").extract_first("")
            if robot == 'Robot Check':
                robot_result = '是'
                # availability_result = ''
                reviewCount_result = [0]
                # rating_result = [0]
                title_result = ''
                brand_result = ''
                dimensions_result = ''
                productWeight_result = ''
                shippingWeight_result = ''
                # self.robotCheck.append({'country':row_data[0],'asin':row_data[1]})
                # if len(row_data) == 3:
                    # self.r.lrem(self.hash('cookie'),0,json.dumps(row_data[2]))
                # with open('{}.txt'.format(row_data[1]), 'w') as f:
                #     f.write(response.body.decode("utf-8"))
                # f.close()
            else:
                robot_result =''
                availability = response.xpath("//div[@id='availability']/span/text()").extract_first("")
                if availability:
                    availability_result = re.sub(r'\s+','',availability)
                else:
                    availability_result = ''
                reviewCount = response.xpath("//h2[@data-hook='total-review-count']/text()").extract_first("")
                if reviewCount:
                    reviewCount_result = re.findall(r'[0-9,.]+',reviewCount)
                    if len(reviewCount_result) == 0:
                        reviewCount_result = [0]
                else:
                    reviewCount_result = [0]
                rating = response.xpath("//span[@data-hook='rating-out-of-text']/text()").extract_first("")
                if rating:
                    rating_result = re.findall(r'[0-9,.]+',rating)
                else:
                    rating_result = [0]
                title = response.xpath("//span[@id='productTitle']/text()").extract_first("")
                if title:
                    title_result = title.replace('\n','').strip()
                else:
                    title_result = ''
                brand = response.xpath("//a[@id='bylineInfo']/text()").extract_first("")
                if brand: 
                    brand_result = brand.replace('\n','').strip()
                else:
                    brand_result = ''
                dimensions = response.xpath("//table[@id='productDetails_detailBullets_sections1']/tbody/tr[1]/td/text()").extract_first("")
                if dimensions:
                    dimensions_result = dimensions
                else:
                    dimensions_result = ''

                # if len(row_data) == 2:
                    # print(response.headers.coolie)
                    # cookie = self.cookie_jar.extract_cookies(response,response.request)
                    # print(cookie)
                    # self.r.rpush(self.hash('cookie'),json.dumps(cookie))
            # l.add_value('lower_frame', availability_result)
            # l.add_value('comment_num', reviewCount_result[0])
            # l.add_value('stars', rating_result[0])
            l.add_value('title',title_result)
            l.add_value('brand',brand_result)
            l.add_value('is_404', '')
            l.add_value('is_robot', robot_result)
        amazon_item = l.load_item()
        yield amazon_item
    
    def hash(self,str):
        hash = hashlib.sha1()
        hash.update(str.encode('utf-8'))
        return  hash.hexdigest()

    def getDesktop(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return winreg.QueryValueEx(key, "Desktop")[0]

    def getDomainUrl(self,country):
        amazonUrl =  {
        'CN': { 'domain': 'https://www.amazon.cn', 'pc': 'https://www.amazon.cn/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=cnflex&currentPageURL=https%3A%2F%2Fwww.amazon.cn%2F%3Fref_%3Dnav_custrec_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.cn%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_signin', 'mobile': 'https://www.amazon.cn/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_cn&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.cn%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'JP': { 'domain': 'https://www.amazon.co.jp', 'pc': 'https://www.amazon.co.jp/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=jpflex&currentPageURL=https%3A%2F%2Fwww.amazon.co.jp%2F%3Fref_%3Dnav_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.co.jp%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_signin', 'mobile': 'https://www.amazon.co.jp/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_jp&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.jp%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'US': { 'domain': 'https://www.amazon.com', 'pc': 'https://www.amazon.com/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=usflex&currentPageURL=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_signin', 'mobile': 'https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_us&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fhomepage.html%3F_encoding%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'UK': { 'domain': 'https://www.amazon.co.uk', 'pc': 'https://www.amazon.co.uk/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=gbflex&currentPageURL=https%3A%2F%2Fwww.amazon.co.uk%2F%3Fref_%3Dnav_custrec_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.co.uk%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_signin', 'mobile': 'https://www.amazon.co.uk/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_uk&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.uk%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'FR': { 'domain': 'https://www.amazon.fr', 'pc': 'https://www.amazon.fr/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=frflex&currentPageURL=https%3A%2F%2Fwww.amazon.fr%2F%3Fref_%3Dnav_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.fr%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_signin', 'mobile': 'https://www.amazon.fr/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_fr&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.fr%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'DE': { 'domain': 'https://www.amazon.de', 'pc': 'https://www.amazon.de/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=deflex&currentPageURL=https%3A%2F%2Fwww.amazon.de%2F%3Fref_%3Dnav_custrec_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.de%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_signin', 'mobile': 'https://www.amazon.de/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_de&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.de%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'ES': { 'domain': 'https://www.amazon.es', 'pc': 'https://www.amazon.es/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=esflex&currentPageURL=https%3A%2F%2Fwww.amazon.es%2F%3Fref_%3Dnav_custrec_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.es%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_signin', 'mobile': 'https://www.amazon.es/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_es&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.es%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'IT': { 'domain': 'https://www.amazon.it', 'pc': 'https://www.amazon.it/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=itflex&currentPageURL=https%3A%2F%2Fwww.amazon.it%2F%3Fref_%3Dnav_custrec_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.it%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_signin', 'mobile': 'https://www.amazon.it/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_it&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.it%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'CA': { 'domain': 'https://www.amazon.ca', 'pc': 'https://www.amazon.ca/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=caflex&currentPageURL=https%3A%2F%2Fwww.amazon.ca%2F%3Fref_%3Dnav_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.ca%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_signin', 'mobile': 'https://www.amazon.ca/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_ca&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.ca%2Fgp%2Fhomepage.html%3F_encoding%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'IN': { 'domain': 'https://www.amazon.in', 'pc': 'https://www.amazon.in/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=inflex&currentPageURL=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.in%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_signin', 'mobile': 'https://www.amazon.in/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_in&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'AU': { 'domain': 'https://www.amazon.com.au', 'pc': 'https://www.amazon.com.au/gp/navigation/redirector.html/ref=sign-in-redirect/358-0627257-0110739?ie=UTF8&associationHandle=auflex&currentPageURL=https%3A%2F%2Fwww.amazon.com.au%2F%3Fref_%3Dnav_custrec_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.com.au%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_signin', 'mobile': 'https://www.amazon.com.au/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_au&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com.au%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' },
        'GB': { 'domain': 'https://www.amazon.co.uk', 'pc': 'https://www.amazon.co.uk/gp/navigation/redirector.html/ref=sign-in-redirect?ie=UTF8&associationHandle=gbflex&currentPageURL=https%3A%2F%2Fwww.amazon.co.uk%2F%3Fref_%3Dnav_custrec_signin&pageType=Gateway&switchAccount=&yshURL=https%3A%2F%2Fwww.amazon.co.uk%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_custrec_signin', 'mobile': 'https://www.amazon.co.uk/ap/signin?_encoding=UTF8&openid.assoc_handle=anywhere_v2_uk&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.uk%2F%3Fie%3DUTF8%26ref_%3Dnavm_hdr_signin' }
        }
        return amazonUrl[country]['domain']