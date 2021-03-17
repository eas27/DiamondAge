import pdfminer
from pdfminer.layout import LTTextContainer, LTChar, LTTextBox
from pdfminer.high_level import extract_pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from fpdf import FPDF
import datetime
import math
from PyPDF2 import PdfFileWriter, PdfFileReader
import regex


class ArticleParser:
    def __init__(self):
        return

    def GetDocInfo(self):
        f = open(fpath, 'rb')
        pparser = pdfminer.pdfparser.PDFParser(f)
        pdoc = pdfminer.pdfdocument.PDFDocument(pparser, None)
        print(pdoc.info)
        f.close()
        return

    def Get_ColumnXPositions (self, fpath):
        posdict = {}
        pct = 0
        for page_layout in extract_pages(fpath, maxpages=5):
            print('NEW PAGE')
            pct += 1
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    foundpos = False
                    for p in posdict:
                        if math.fabs(p-element.x0) < .5:
                            posdict[p] = posdict[p] + 1
                            foundpos = True
                            break
                    if foundpos == False:
                         posdict [round(element.x0, 2)] = 1
        posdict = dict(sorted(posdict.items(), key=lambda item: item[1], reverse = True))

        poslist = list(posdict.keys())
        poslist = poslist [0:2]
        return poslist

    def replace_codes (self, code):
        code = code.replace('/F16', '')
        code = code.replace('/F14', 'f')
        code = code.replace('/F4', '')
        code = code.replace('/F1', '')
        code = code.replace('/F15', '?')
        code = code.replace('/F12', '?')
        code = code.replace('/F17', '?')
        code = code.replace('/F6', '')
        code = code.replace('/F2', 'f')
        code = code.replace('/F3', 'e')
        code = code.replace('/F5', '')
        code = code.replace('/F9', '')
        code = code.replace('/F7', '')
        code = code.replace('/F8', '')
        code = code.replace('\x03', 'f')
        code = code.replace('\x01', 'i')
        code = code.replace('\x15', '\x15')
        return code


    def ParseScientificArticle(self, fpath, fpdf:FPDF):
        def is_number (numstr):
            try:
                float (numstr)
                return True
            except:
                return False

        def process_data(object):
            fulltext = ''
            data = object.getData()
            decoded_data = data.decode('UTF-8', errors='ignore')
            ts = regex.findall('(/F[0-9]*)|(\[.*\]T.)|(\(.*\)Tj)', decoded_data)
            allowAddSpace = True
            for t in ts:
                line = ''
                if not t[1] == '':
                    ms = regex.findall('(([0-9,\.]*)(\(([^(]+)\)))', t[1])
                    for m in ms:
                        if allowAddSpace == True:
                            if (is_number(m[1]) and float(m[1]) > 50):
                                line += ' '
                            elif m[1] == '':
                                line += ' '
                            elif not is_number(m[1]):
                                line += ' '
                        line += m[3]
                        allowAddSpace = True
                elif not t[0] == '':
                    addtext = self.replace_codes (str(t[0]).strip())
                    if not addtext == '':
                        if allowAddSpace==True:
                            line += ' '
                        line += addtext
                    allowAddSpace = False
                elif not t[2] == '':
                    ms = regex.findall('\(([^(]+)\)', t[2])
                    if ms and not (str(ms[0])).isnumeric():
                        if allowAddSpace == True:
                            line += ' '
                        line += self.replace_codes(ms[0])
                    allowAddSpace = False
                fulltext += line
            return fulltext


        rdr = PdfFileReader(open(fpath, 'rb'))
        fpdf.add_page()

        for i in range (0,rdr.getNumPages()):
            page = rdr.getPage (i)
            content = page.getContents ()
            if isinstance(content, list):
                for obj in content:
                    streamObj = obj.getObject()
                    pagetext = process_data(streamObj)
                    fpdf.multi_cell(175, 10, txt=pagetext)
            else:
                obj = content
                streamObj = obj.getObject()
                pagetext = process_data(streamObj)
                fpdf.multi_cell(175, 10, txt=pagetext)
        # wrtr = PdfFileWriter()
        # rdr = PdfFileReader (open (fpath, 'rb'))
        # for i in range (0,rdr.getNumPages()):
        #     page = rdr.getPage (i)
        #     content = page.getContents ()
        #     for obj in content:
        #         streamObj = obj.getObject()
        #         pagetext = process_data(streamObj)
        #         outpage = wrtr.addPage()
        #         outpage.addText(outpage)
        # wrtr.write (open("Results/articles_test.pdf", 'wb'))
        # return

        # xposlist = self.Get_ColumnXPositions (fpath)
        #
        # for page_layout in extract_pages(fpath):
        #     textlines = []
        #     col1 = []
        #     col2 = []
        #     print(page_layout)
        #     for element in page_layout:
        #         if isinstance(element, LTTextContainer):
        #             if found_abstract == False and element.get_text().lower().find('abstract') == 0:
        #                 found_abstract = True
        #             refpos = element.get_text().lower().strip().find('references')
        #             if refs_found == False and refpos >= 0 and refpos < 3:
        #                 refs_found = True
        #             if found_abstract and not refs_found:
        #                 print (element)
        #                 if (0 < element.x0 - xposlist [0] < .5):
        #                     linelist = col1
        #                 elif (0 < element.x0 - xposlist [1] < 1):
        #                     linelist = col2
        #                 else:
        #                     linelist = None
        #                 if linelist is not None:
        #                     if element.get_text().find('Figure') == 0 or element.get_text().find('Table') == 0:
        #                         continue
        #                     else:
        #                         line = element.get_text().replace('\n', ' ')
        #                         linelist.append(line)
        #     if (col1 is not None):
        #         textlines.extend(col1)
        #     if (col2 is not None):
        #         textlines.extend(col2)
        #
        #     if currpage == 1:
        #         headerline = textlines[0]
        #     if currpage == 2 and textlines[0] == headerline:
        #         startline = 1
        #     pages.append(textlines)
        #     currpage += 1
        #
        # fpdf = FPDF()
        # fpdf.add_font('ArialUnicode', fname='/Users/eric/Library/Fonts/Arial-Unicode-Regular.ttf', uni=True)
        # fpdf.set_font('ArialUnicode', '', 11)
        # # fpdf.set_font("Arial", "B",  size=15)
        # fpdf.add_page()
        # for p in pages:
        #     if pages.index(p) == 0:
        #         startl = 0
        #     else:
        #         startl = startline
        #     for i in range(startl, len(p)):
        #         print(p[i])
        #         fpdf.multi_cell(175, 10, txt=p[i])
        # today = datetime.datetime.now()
        # fpdf.set_compression(0)
        # fpdf.output("Results/articles" + str(today.year) + str(today.month) + str(today.day) + ".pdf")
