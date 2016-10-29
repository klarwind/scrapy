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
		'''获取贴吧名'''
		kw_long = sel.xpath('//*[@class="card_title_fname"]/@href').extract()
		for k in kw_long:
			kw = k
		kw = re.findall(r"kw=(.*)&",kw)[0]

		
		'''获取相册ID'''
		tid = response.url
		tid = re.findall(r"/(\d{10})",tid)[0]

		'''合成请求地址'''
		furl = "http://tieba.baidu.com/photo/g/bw/picture/list?kw="+kw+"&alt=jview&rn=200&tid="+tid+"&pn=1&ps=1&pe=200"
		
		'''调用下面一个解析函数解析页面数据'''
		yield Request(furl,callback=self.re_parse)
	
	def re_parse(self,response):
		item = TietuItem()		
		content = json.loads(response.body)
		
		'''获取总页数'''
		page = content["data"]["total_page"]
		
		'''获取当前页数'''
		now_page = re.findall(r"pn=(\d{1,2})&",response.url)[0]
		#print now_page
		
		'''获取每个图的URL'''
		for tid in content["data"]["pic_list"]:
			item['image_url']= ["http://imgsrc.baidu.com/forum/pic/item/"+tid['pic_id']+".jpg"]
			yield item
		
		'''如果有后一页，修改请求网址，递归当前函数'''
		if page > int(now_page):
			next_page = str(int(now_page)+1)
			li = response.url.split('pn='+now_page)
			next_url = li[0]+"pn="+next_page+li[1]
			yield Request(next_url,callback=self.re_parse)