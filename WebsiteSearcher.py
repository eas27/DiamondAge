import urllib
import xml.etree.ElementTree as ET
from datetime import datetime
from fpdf import FPDF
import wikipedia
from fp.fp import FreeProxy
from scholarly import scholarly
from scholarly import ProxyGenerator
import requests
from bs4 import BeautifulSoup
import os.path
from os import path
import logging


class WebsiteSearcher:
    ns = None
    reflist = []
    def __init__ (self):
        print('WSS initiating')
        self.ns = {'arxivns': 'http://www.w3.org/2005/Atom'}
        self.reflist = []
        self.logger = logging.getLogger()

    def abstracttopdf (self, entry, earlyDate, pdf):
        width = 195
        link = entry.find('.//arxivns:id', self.ns)
        published = entry.find('.//arxivns:published', self.ns)
        datetime_object = datetime.strptime(published.text, '%Y-%m-%dT%H:%M:%SZ')
        if datetime_object < earlyDate:
            return -1
        pubdate = str(datetime_object.year) + '-' + str(datetime_object.month) + '-' + str(datetime_object.day)
        if link.text in self.reflist:
            print("Element Exists")
            return
        else:
            self.reflist.append(link.text)
            pdf.add_page()
            authors = entry.findall('.//arxivns:author', self.ns)
            authlist = ''
            for author in authors:
                for name in author:
                    if authlist != '':
                        authlist = authlist + ', '
                    authlist = authlist + name.text
            pdf.multi_cell(width, 10, txt=str(authlist.encode('latin-1', 'replace').decode('latin-1')) )
            title = entry.find('.//arxivns:title', self.ns)
            pdf.multi_cell(width, 10, txt=title.text)
            pdf.multi_cell(width, 10, txt=pubdate)
            summary = entry.find('.//arxivns:summary', self.ns)
            pdf.multi_cell(width, 10, txt=summary.text)
            pdf.cell(width, 10, txt=link.text, link=link.text)

    def searchArXiv (self, query, earlyDate, pdf:FPDF):
        url = 'http://export.arxiv.org/api/query?search_query='+query+'&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending'
        data = urllib.request.urlopen(url).read()
        root = ET.fromstring(data)
        entrylist = root.findall('.//arxivns:entry', self.ns)
        for entry in entrylist:
            retval = self.abstracttopdf(entry,earlyDate, pdf)
            if retval == -1:
                break

    def searchWikipedia (self, query):
        print(wikipedia.search(query))
        print(wikipedia.page('breast cancer').content)

    # def searchACS (self)
    #     resp = requests.get("http://api.elsevier.com/content/author?author_id=7004212771&view=metrics",
    #                         headers={'Accept': 'application/json',
    #                                  'X-ELS-APIKey': MY_API_KEY})
    #     json.dumps(resp.json(),
    #                sort_keys=True,
    #                indent=4, separators=(',', ': '))


    def searchGoogleScholar(self, query, resct):

        pg = ProxyGenerator()
        proxy = FreeProxy(rand=True, timeout=1, country_id='CA').get()
        pg.SingleProxy(http=proxy, https=proxy)
        scholarly.use_proxy(pg)
        scholarly.set_retries(10)
        search_query = scholarly.search_pubs(query=query)
        width = 195
        resct = 0
        for i in range(1,10):
            try:
                result= next(search_query)
            except:
                break
            bib = result['bib']['abstract']
            pdf.add_page()
            pdf.multi_cell (width, 10, txt=str(bib.encode('latin-1', 'replace').decode('latin-1')))
            resct = resct + 1
    def searchBioRxiv (self, query):
       # url='https://www.biorxiv.org/search/'+query+'%20numresults%3A100'
        #       'text_abstract_title_flags%3Amatch-all%20jcode%3Abiorxiv%20numresults%3A10%20sort%3Arelevance-rank%20format_result%3Astandard'
       # data = urllib.request.urlopen(url).read()
       # print (data)
       # root = ET.fromstring(data)
       # entrylist = root.findall('.//arxivns:entry', ns)
        from biorxiv_retriever import BiorxivRetriever
        br = BiorxivRetriever(search_engine='rxivist', search_url='https://api.rxivist.org/v1/papers?q={}&timeframe=alltime&metric=downloads&page_size=100&page={}')
        papers = br.query('transcription factor', metadata=True, full_text=False, num_pages = 1)
        for paper in papers:
           pdf.add_page()
           pdf.multi_cell(190, 10, txt=paper["abstract"].encode('latin-1', 'replace').decode('latin-1'))

    def GetYahooNews (self, language):
        soup = None
        if language == 'es':
            if not path.exists("data/es-yn.txt"):
                f = open('data/es-yn.txt', 'w')
                url = 'http://espanol.yahoo.com'
                soup = BeautifulSoup(requests.get(url).text, 'html.parser')
                f.write(soup.prettify())
                f.close()
            else:
                self.logger.info('file found, using cached data')
                f = open('data/es-yn.txt', 'r')
                soup = BeautifulSoup(f.read(), 'html.parser')
                f.close()
        if not soup == None:
            if not path.exists("data/es-yn.articles.txt"):
                f = open('data/es-yn.articles.txt', 'w')
                for link in soup.findAll('a', attrs={'class':'js-content-viewer rapidnofollow'}):
                    url = 'https://espanol.yahoo.com/'  + link.get('href')
                    artsoup = BeautifulSoup(requests.get(url).text, 'html.parser')
                    f.write('||ARTICLE||:\n')
                    f.write(artsoup.prettify())
                f.close()
        f = open('data/es-yn.articles.txt', 'r')
        articles = f.read ().split('||ARTICLE||')
        alltext = ''
        for article in articles:
            artsoup = BeautifulSoup(article, 'html.parser')
            ps= artsoup.find_all('p')
            for p in ps:
                alltext += p.text
        return alltext


