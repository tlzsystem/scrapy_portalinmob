# -*- coding: utf-8 -*-
import scrapy
import json
import urllib.parse as urlparse
import logging
from datetime import date


class ListadoSpider(scrapy.Spider):
    name = 'listado'
    allowed_domains = ['portalinmobiliario.com']
    BASE_URL = 'https://www.portalinmobiliario.com'
    fi = ''
    ff = ''

    def __init__(self, inicial='',fi='',ff='', **kwargs):
        self.start_urls = [inicial]
        self.fi = fi
        self.ff = ff
        super().__init__(**kwargs)

    def parse(self, response):

        evaluaUltimo = response.css("li.ultima a::attr(href)") #Verificamos si es multiresultados

        if len(evaluaUltimo)==0: #No es multiple
            paginacion = response.css('div#PaginacionSuperior ul li')
            if len(paginacion) == 0: #tiene solo una pagina
                logging.info("TIENE UNA SOLA PAGINA")
                lista = response.css('div.product-item-data')
                for item in lista:
                    link = item.css('div.product-item-summary h4 a::attr(href)').extract_first()
                    yield scrapy.Request(self.BASE_URL+link, callback = self.procesa)
            else:# Tiene entre 1 y 3 paginas
                logging.info("TIENE ENTRE 1 YY 3 PAGINAS")
                for i in paginacion:
                    link = i.css('li a::attr(href)').extract_first()
                    logging.info("Siguiendo el LINK: << "+str(link)+" >>")
                    yield scrapy.Request(self.BASE_URL+link, callback = self.inicia)
        else:
            logging.info("ES MULTIPAGINA")
            urlUltimo = response.css("li.ultima a::attr(href)").extract_first()
            parsed = urlparse.urlparse(urlUltimo)
            query = urlparse.parse_qs(parsed.query)
            if query.get("pg"): 
                for i in range(1,int(query.get("pg")[0])+1):
                    logging.info("Siguiendo el LINK: "+response.url+"&pg="+str(i))
                    yield scrapy.Request(response.url+"&pg="+str(i), callback = self.inicia)

    def inicia(self, response):
        logging.info("SE INICIA LA BUSQUEDA DE ELEMENTOS")
        lista = response.css('div.product-item-data')
        for item in lista:
            link = item.css('div.product-item-summary h4 a::attr(href)').extract_first()
            yield scrapy.Request(self.BASE_URL+link, callback = self.procesa)
        
            
    def procesa(self, response):

        if len(response.css("p.operation-owner-logo"))==0:

            fechaSelector = response.css('div.content-panel').css('.small-content-panel p')[1]
            fechaValor = fechaSelector.css('p.operation-internal-code strong::text').extract_first()
            xfecha = fechaValor.split(':')[1].strip().split('-')
            xFi = self.fi.split('-')
            xFf = self.ff.split('-')
            fechaInicial = date(int(xFi[2]),int(xFi[1]),int(xFi[0])) 
            fechaFinal = date(int(xFf[2]),int(xFf[1]),int(xFf[0])) 
            fecha = date(int(xfecha[2]),int(xfecha[1]),int(xfecha[0]))
            logging.info("LA FECHA ES: "+str(fecha))
            logging.info("LA FECHA INICIAL ES: "+str(fechaInicial))
            logging.info("LA FECHA FINAL ES: "+str(fechaFinal))
            if fechaInicial<= fecha <=fechaFinal:
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
                    "Fecha Publicación": str(fecha),
                }
            else:
                pass
        else:
            logging.info(response.url+" ES EMPRESA")
            pass