import scrapy
import json

from scrapy import Spider
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
from scrapy import Request
from likefolio.items import MentionsMongoItem
from datetime import datetime

class MentionsMongoSpider(scrapy.Spider):
    name = "mentions_mongo"
    allowed_domains = ["dashboard.likefolio.com"]
    start_urls = ["https://dashboard.likefolio.com/users/sign_in"]

    def parse(self, response):
        token = response.xpath('//*[@name="authenticity_token"]/@value').extract_first()
        return FormRequest.from_response(
            response,
            formdata={
                "authenticity_token": token,
                "user[email]": "tonymoo90@gmail.com",
                "user[password]": "discoveredlit",
            },
            callback=self.navigate,
        )

    def navigate(self, response):
        baseurl = "https://dashboard.likefolio.com/"
        pagelist = [
            # "companies/1986/daily_pi.json?apply_corrections=yes&avg_size=90&display_avg=yes&display_daily=no&display_price=yes&period=all&show_annotations=no",
            # "companies/1986/daily_sentiment.json?apply_corrections=yes&avg_size=90&display_avg=yes&display_daily=no&display_price=yes&period=all&show_annotations=no",
            "companies/1986/daily_mentions.json?apply_corrections=yes&avg_size=90&display_avg=yes&display_daily=no&display_price=yes&period=all&show_annotations=no",
        ]
        for page in pagelist:
            yield Request(url=baseurl + page, callback=self.scrape_pages)

#this code worked to create pop-up likefolio json file
#    def scrape_pages(self, response):
#        open_in_browser(response)
#        test = response.xpath("/html/body/pre/text()").get_all()
#        return test

    def scrape_pages (self, response):
        mentionsItem = MentionsMongoItem()
        data = []
        body = json.loads(response.body)
#        return body
        for value in body['data']:
            dt = datetime(
                int(value['date'].split('-')[0]),
                int(value['date'].split('-')[1]),
                int(value['date'].split('-')[2])
            ).timestamp()
            ms = dt * 1000
            data.append([ms, value['value']])
        mentionsItem['internalName'] = 'daily_mentions'
        mentionsItem['name'] = 'Twitter Mentions'
        mentionsItem['total'] = value['value']
        mentionsItem['change'] = '3%'
        mentionsItem['frequency'] = 'Daily'
        mentionsItem['expectations'] = 'null'
        mentionsItem['visualizationType'] = 'xy'
        mentionsItem['visualizationData'] = data
        mentionsItem['topic'] = 'Tesla'

        yield mentionsItem