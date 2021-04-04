from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from fpdf import FPDF
import datetime
import math
from PyPDF2 import PdfFileWriter, PdfFileReader
import regex


class ArticleParser:
    def __init__(self):
        return


    def GetArticleText (self, fpath):
        output_string = StringIO()
        with open(fpath, 'rb') as in_file:
            parser = PDFParser(in_file)
            doc = PDFDocument(parser)
            rsrcmgr = PDFResourceManager()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams(all_texts=False))
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.create_pages(doc):
                interpreter.process_page(page)

        return output_string.getvalue()

    def Get_MainText (self, fpath, fpdf):
        fulltext = self.GetArticleText (fpath)
        intable = False
        modtext = ''
        for l in fulltext.splitlines ():
            if -1 < l.lower().find('table') < 3:
                intable = True
                ws = False
            elif intable:
                if l.strip () == '':
                    ws = True
                if ws and len(l.split ()) > 10:
                    intable = False
            if intable:
                continue
            if -1 < l.lower().find('references') < 10:
                inrefs = True
                break
            if len(l) < 3:
                continue
            modtext += l

        if fpdf is not None:
            fpdf.add_page()
            fpdf.multi_cell(175, 10, txt=modtext)
        return ''
    # def GetDocInfo(self, fpath):
    #     f = open(fpath, 'rb')
    #     pparser = pdfminer.pdfparser.PDFParser(f)
    #     pdoc = pdfminer.pdfdocument.PDFDocument(pparser, None)
    #     print(pdoc.info)
    #     f.close()
    #     return

    # def Get_ColumnXPositions (self, fpath):
    #     posdict = {}
    #     pct = 0
    #     for page_layout in extract_pages(fpath, maxpages=5):
    #         pct += 1
    #         for element in page_layout:
    #             if isinstance(element, LTTextContainer):
    #                 foundpos = False
    #                 for p in posdict:
    #                     if math.fabs(p-element.x0) < .5:
    #                         posdict[p] = posdict[p] + 1
    #                         foundpos = True
    #                         break
    #                 if foundpos == False:
    #                      posdict [round(element.x0, 2)] = 1
    #     posdict = dict(sorted(posdict.items(), key=lambda item: item[1], reverse = True))
    #
    #     poslist = list(posdict.keys())
    #     poslist = poslist [0:2]
    #     return poslist
    #
    # def replace_codes (self, code):
    #     code = code.replace('/F16 ', '')
    #     code = code.replace('/F14 ', 'f')
    #     code = code.replace('/F4 ', '')
    #     code = code.replace('/F1 ', '')
    #     code = code.replace('/F15 ', '?')
    #     code = code.replace('/F12 ', '?')
    #     code = code.replace('/F17 ', '?')
    #     code = code.replace('/F6 ', '')
    #     code = code.replace('/F2 ', 'f')
    #     code = code.replace('/F3 ', 'e')
    #     code = code.replace('/F5 ', '')
    #     code = code.replace('/F9 ', '')
    #     code = code.replace('/F7 ', '')
    #     code = code.replace('/F8 ', '')
    #     code = code.replace('/F48 ', '') #Bold
    #     code = code.replace('/F50 ', '') #Bold
    #     code = code.replace('/F55 ', '') #Ital
    #     code = code.replace('/F51 ', '')
    #     code = code.replace('/F27 ', '')
    #     code = code.replace('\\x03 ', 'f')
    #     code = code.replace('\\x01 ', 'i')
    #     code = code.replace('\\x15 ', '\\x15')
    #     code = code.replace('\\002', 'fi')
    #     code = code.replace('\\050', '(')
    #     code = code.replace('\\051', ')')
    #     code = code.replace('\\223', ' "')
    #     code = code.replace('\\224', '" ')
    #     code = code.replace('\\225', '• ')
    #     code = code.replace('/F63', '')
    #     code = code.replace('/F64', '')
    #     code = code.replace ('/F[0-9]* ', '')
    #     return code
    #
    #
    # def ParseScientificArticle(self, fpath, fpdf:FPDF, sections):
    #     def is_number (numstr):
    #         try:
    #             float (numstr)
    #             return True
    #         except:
    #             return False
    #     def FindLines (text):
    #         linefeeds = regex.split('(-?\d*\.?\d*\s-?\d*\.?\d*\sTd)', text)
    #         inpara = False
    #         paratext = ''
    #         lasty =-1
    #         parsedtxt = ''
    #         holdover = False
    #         splitrec = False
    #         for l in linefeeds:
    #             if 'Td' not in l:
    #                 skipspace = False
    #                 striptxt = self.replace_codes (GetTextFromLine(l).replace('\n', ' ')).strip()
    #                 if (striptxt.endswith('-')):
    #                     holdover = True
    #                     striptxt = striptxt.strip('-')
    #                     skipspace = True
    #                 else:
    #                     holdover = False
    #                 if len(striptxt) == 1 or skipspace ==True:
    #                     paratext += striptxt
    #                 else:
    #                     paratext += striptxt + ' '
    #             else:
    #                 lfinfo = l.split ()
    #                 x= round(float(lfinfo[0]),2)
    #                 y= round(float(lfinfo[1]) ,2)
    #                 tdinfo = '<' + str(lasty) + ':' + str(x) + ','  +str(y) + ':' + str(round(abs(y)-abs(lasty),2))+'>'
    #                 if  (abs(y)-abs(lasty) > 5):
    #                     paratext += '\n<SPLIT ' + tdinfo + '>\n'
    #                     splitrec = True
    #                 if (x == 0 or y == 0 or y == lasty):
    #                     inpara = True
    #                 else:
    #                     inpara = False
    #                     if (holdover):
    #                         parsedtxt += paratext
    #                     else:
    #                         parsedtxt += paratext + ' '
    #                     paratext = ''
    #                 if y != 0:
    #                     lasty = y
    #         parsedtxt +=paratext
    #         return parsedtxt
    #
    #     def GetTextFromLine (text):
    #         linetext = ''
    #         ts = regex.findall('(/F[0-9]*)|(\[.*\]T.)|(\(.*\)Tj)', text)
    #         allowAddSpace = True
    #         for t in ts:
    #             line = ''
    #             if not t[1] == '':
    #                 ms = regex.findall('(([0-9,\.]*)(\(([^(]+)\)))', t[1])
    #                 for m in ms:
    #                     if allowAddSpace == True:
    #                         if (is_number(m[1]) and abs(float(m[1])) > 100):
    #                             line += ' '
    #                         elif m[1] == '':
    #                             line += ' '
    #                         elif not is_number(m[1]):
    #                             line += ' '
    #                     line += m[3]
    #                     if (m[1] != '' or len(m[3].strip()) > 1):
    #                         allowAddSpace = True
    #                     else:
    #                         allowAddSpace = False
    #             elif not t[0] == '':
    #                 addtext = self.replace_codes(str(t[0]).strip())
    #                 if not addtext == '':
    #                     if allowAddSpace == True:
    #                         line += ' '
    #                     line += addtext
    #                 allowAddSpace = False
    #             elif not t[2] == '':
    #                 ms = regex.findall('\(([^(]+)\)', t[2])
    #                 if ms and not (str(ms[0])).isnumeric():
    #                     if allowAddSpace == True:
    #                         line += ' '
    #                     line += self.replace_codes(ms[0])
    #                 allowAddSpace = False
    #             linetext += line + '\n'
    #         return linetext
    #
    #     def process_data(object):
    #         fulltext = ''
    #         data = object.getData()
    #         decoded_data = data.decode('UTF-8', errors='ignore')
    #         fulltext += FindLines(decoded_data)
    #         return fulltext
    #
    #     rdr = PdfFileReader(open(fpath, 'rb'))
    #     if fpdf is not None:
    #         fpdf.add_page()
    #     fulltext = ''
    #
    #     for i in range (0,rdr.getNumPages()):
    #         page = rdr.getPage (i)
    #         content = page.getContents ()
    #         if isinstance(content, list):
    #             for obj in content:
    #                 streamObj = obj.getObject()
    #                 pagetext = process_data(streamObj)
    #                 fulltext += '\n' + pagetext
    #         else:
    #             obj = content
    #             streamObj = obj.getObject()
    #             pagetext = process_data(streamObj)
    #             fulltext += '\n' + pagetext
    #     splits = regex.split('<SPLIT.*>', fulltext)
    #     modtext = ''
    #     for s in splits:
    #         words = s.split ()
    #         if not words == []:
    #             if 'REFERENCES' in words[0].upper():
    #                 break
    #             if 'FIGURE' in words[0].upper ():
    #                 continue
    #             if 'TABLE' in words[0].upper ():
    #                 continue
    #             else:
    #                 modtext += s
    #     if fpdf is not None:
    #         fpdf.multi_cell(175, 10, txt=modtext)
    #     return modtext
    #
    #     # xposlist = self.Get_ColumnXPositions (fpath)
    #     #
    #     # for page_layout in extract_pages(fpath):
    #     #     textlines = []
    #     #     col1 = []
    #     #     col2 = []
    #     #     print(page_layout)
    #     #     for element in page_layout:
    #     #         if isinstance(element, LTTextContainer):
    #     #             if found_abstract == False and element.get_text().lower().find('abstract') == 0:
    #     #                 found_abstract = True
    #     #             refpos = element.get_text().lower().strip().find('references')
    #     #             if refs_found == False and refpos >= 0 and refpos < 3:
    #     #                 refs_found = True
    #     #             if found_abstract and not refs_found:
    #     #                 print (element)
    #     #                 if (0 < element.x0 - xposlist [0] < .5):
    #     #                     linelist = col1
    #     #                 elif (0 < element.x0 - xposlist [1] < 1):
    #     #                     linelist = col2
    #     #                 else:
    #     #                     linelist = None
    #     #                 if linelist is not None:
    #     #                     if element.get_text().find('Figure') == 0 or element.get_text().find('Table') == 0:
    #     #                         continue
    #     #                     else:
    #     #                         line = element.get_text().replace('\n', ' ')
    #     #                         linelist.append(line)
    #     #     if (col1 is not None):
    #     #         textlines.extend(col1)
    #     #     if (col2 is not None):
    #     #         textlines.extend(col2)
    #     #
    #     #     if currpage == 1:
    #     #         headerline = textlines[0]
    #     #     if currpage == 2 and textlines[0] == headerline:
    #     #         startline = 1
    #     #     pages.append(textlines)
    #     #     currpage += 1
    #     #


