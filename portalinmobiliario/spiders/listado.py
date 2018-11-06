# -*- coding: utf-8 -*-
import scrapy
import json
import urllib.parse as urlparse
import logging


class ListadoSpider(scrapy.Spider):
    name = 'listado'
    allowed_domains = ['portalinmobiliario.com']
    BASE_URL = 'https://www.portalinmobiliario.com'

    def __init__(self, inicial='', **kwargs):
        self.start_urls = [inicial]
        super().__init__(**kwargs)

    def parse(self, response):

        urlUltimo = response.css("li.ultima a::attr(href)").extract_first()
        parsed = urlparse.urlparse(urlUltimo)

        query = urlparse.parse_qs(parsed.query)
        if query.get("pg"):
            for i in range(1,int(ultimo[0])+1):
                logging.info("Siguiendo el LINK: "+response.url+"&pg="+str(i))
                yield scrapy.Request(response.url+"&pg="+str(i), callback = self.inicia)
        else:
            logging.info("Solo una pagina, se inicia el proceso")
            lista = response.css('div.product-item-data')
            for item in lista:
                link = item.css('div.product-item-summary h4 a::attr(href)').extract_first()
                yield scrapy.Request(self.BASE_URL+link, callback = self.procesa)
    def inicia(self, response):
        logging.info("SE INICIA LA BUSQUEDA DE ELEMENTOS")
        lista = response.css('div.product-item-data')
        for item in lista:
            link = item.css('div.product-item-summary h4 a::attr(href)').extract_first()
            yield scrapy.Request(self.BASE_URL+link, callback = self.procesa)
        
            
    def procesa(self, response):

        if len(response.css("p.operation-owner-logo"))==0:
            datos = response.xpath("//script[contains(.,'datosContacto')]/text()")
            precio_ref = response.css("span.price-reference::text").extract_first()
            precio_real = response.css("span.price-real::text").extract_first()
            txt = datos.extract_first()
            start = txt.find('datosContacto') + 16
            end = len(txt)
            json_string = txt[start:end]
            json_string = json_string.replace("\r","")
            json_string = json_string.replace("\n","")
            json_string = json_string.replace(";","")
            json_string = json_string.replace("nombreVendedor","\"nombreVendedor\"")
            json_string = json_string.replace("telefonosVendedor","\"telefonosVendedor\"")
            json_string = json_string.replace("emailVendedor","\"emailVendedor\"")
            json_string = json_string.replace("faxVendedor","\"faxVendedor\"")
            json_string = json_string.replace("&nbsp","")
            json_string = json_string.replace("<span itemprop=\'telephone\'>","")
            json_string = json_string.replace("</span>","")
            data = json.loads(json_string)

            yield {
                "url":response.url,
                "Nombre Vendedor":data.get("nombreVendedor","S/I"),
                "Telefono":data.get("telefonosVendedor","0"),
                "Fax":data.get("faxVendedor","0"),
                "Mail":data.get("emailVendedor","S/I"),
                "Precio Referencia": precio_ref,
                "Precio Real": precio_real,
            }
        else:
            logging.info(response.url+" ES EMPRESA")
            pass