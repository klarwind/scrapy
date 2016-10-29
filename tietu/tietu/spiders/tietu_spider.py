# -*- coding: utf-8 -*-

from scrapy.spider import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from tietu.items import TietuItem
import re
import json

class tietuspider(Spider):
	name = "tietu"
	allowed_domains = ["tieba.baidu.com"]
	start_urls = [
		"http://tieba.baidu.com/p/4248175234"
	]
	
	
	def parse(self,response):
		sel = Selector(response)
				##change kw##
		kw_long = sel.xpath('//*[@class="card_title_fname"]/@href').extract()
		for k in kw_long:
			kw = k
		kw = re.findall(r"kw=(.*)&",kw)[0]

		
				##change tid##
		tid = response.url
		tid = re.findall(r"/(\d{10})",tid)[0]


		furl = "http://tieba.baidu.com/photo/g/bw/picture/list?kw="+kw+"&alt=jview&rn=200&tid="+tid+"&pn=1&ps=1&pe=200"
		yield Request(furl,callback=self.re_parse)
	
	def re_parse(self,response):
		item = TietuItem()		
		content = json.loads(response.body)
		page = content["data"]["total_page"]

		now_page = re.findall(r"pn=(\d{1,2})&",response.url)[0]
		print now_page
		
		for tid in content["data"]["pic_list"]:
			item['image_url']= ["http://imgsrc.baidu.com/forum/pic/item/"+tid['pic_id']+".jpg"]
			yield item
	
		if page > int(now_page):
			next_page = str(int(now_page)+1)
			li = response.url.split('pn='+now_page)
			next_url = li[0]+"pn="+next_page+li[1]
			yield Request(next_url,callback=self.re_parse)