# -*- coding: utf-8 -*-
import scrapy


class PortalSpider(scrapy.Spider):
    name = 'portal'
    allowed_domains = ['portalinmobiliario.com']
    start_urls = ['https://www.portalinmobiliario.com/venta/casa/puente-alto-metropolitana/4294676-los-chercanes-puente-alto-casa-3870-uda']

    def parse(self, response):
        
        pass
