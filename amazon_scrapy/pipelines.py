# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import winreg,os,csv


# 写入到csv文件中
class AmazonScrapyPipeline(object):
    def __init__(self):
        self.csvFile = open(os.path.join(self.getDesktop(),'csvFile.csv'),'w',newline='')
        self.writer = csv.writer(self.csvFile)
        # self.writer.writerow(['Marketplace Name','ASIN','是否下架','评论数量','星星','链接','is_404','is_robot'])
        self.writer.writerow(['Marketplace Name','ASIN','标题','品牌','is_404','is_robot'])

    def getDesktop(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return winreg.QueryValueEx(key, "Desktop")[0]

    def process_item(self, item, spider):
        row_data = []
        row_data.append(item['Marketplace_Name'][0])
        row_data.append(item['ASIN'][0])
        row_data.append(item['title'][0])
        row_data.append(item['brand'][0])
        # row_data.append(item['lower_frame'][0])
        # row_data.append(item['comment_num'][0])
        # row_data.append(item['stars'][0])
        row_data.append(item['url'][0])
        row_data.append(item['is_404'][0])
        row_data.append(item['is_robot'][0])
        self.writer.writerow(row_data)
        return item

    def close_spider(self,spider):
        self.csvFile.close()
