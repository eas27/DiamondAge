import PyPDF2
import string
import fitz
import pyttsx3
import xml.etree.ElementTree as ET
import logging
import sys
import os
from pydub import AudioSegment
import ffmpeg
import png
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import subprocess
import time
from bs4 import BeautifulSoup
import subprocess
from word2word import Word2word
import pickle
import pandas as pd

class GLD:
    data: list
    fulldict: dict
    engine:pyttsx3.Engine

    def __init__(self):
        self.data = []
        self.fulldict = {}
        self.logger = logging.getLogger()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 400)

    def GetTextFromPDF (self, pdfpath):
        #'data/Harry_Potter_y_la_Piedra_Filosofal_01.pdf'
        pdf_file = open(pdfpath, 'rb')
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = read_pdf.getNumPages()
        fullstring = ''
        for i in range (0, number_of_pages):
            page = read_pdf.getPage(i)
            page_content = page.extractText()
            fullstring += ' ' + str(self.RemoveCharacters(page_content))
        return fullstring

    def GenerateWordList (self, fullstring):
        splitall = fullstring.split ()
        wordlist = {}
        for w in splitall:
            w = w.strip().lower()
            if w not in wordlist:
                wordlist [w] = 1
            else:
                wordlist [w] = wordlist [w] + 1
        logging.info('Text Word List Length:' + str(len(wordlist)))
        revsort = dict(reversed(sorted(wordlist.items(), key=lambda item: item[1] )))
        return revsort

    def GetDefs (self, worddict:dict):
        outdict:dict
        outdict = {}
        if len(self.fulldict) == 0:
            self.Read_Dictionary ("/Users/eric/PycharmProjects/DiamondAge/data/es-en.xml")
        for w in worddict:
            if w in self.fulldict:
                outdict[w] = self.fulldict [w]
        return outdict

    def ReadWords (self, words:dict):
        entryct = 0
        for w in words:
            try:
                self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.monica')
                self.engine.say(w)
                self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
                self.engine.say(words[w])
                print(w + ':' + words[w])
                if entryct % 100 == 0:
                    self.engine.runAndWait()
            except:
                self.logger.info('--ERROR'+ str(sys.exc_info()[0]))
            entryct += 1
        self.engine.runAndWait()

    def SaveWordsToAudioFile (self, words:dict):
        # fulltext = ''
        entryct = 0
        sys.path.append('/Users/eric/opt/anaconda3/envs/DSenv/lib/python3.7/site-packages/ffprobe/ffprobe.py')
        path_to_save = os.getcwd() + '/Results/' + 'exp.mp3'
        mp3path = os.getcwd() + '/Results/' + 'converted.mp3'
        self.engine.save_to_file('text to speech  to speech to speech', path_to_save)
        self.engine.runAndWait ()
        self.engine.stop ()

        #fulltext =''
        #tts = self._TTS ()
        #tts.start ('text')

        #for w in words:

        for i in range (0,5):
             w = list (words)[i]
             entryct += 1
             #tts.save_to_file(w)
             self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.monica')
             self.engine.save_to_file(w, path_to_save)
             self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
             self.engine.save_to_file(words[w], path_to_save)
             print ('sleep' + str(i))
             time.sleep(.5)
        self.engine.startLoop()
        self.engine.runAndWait()
        self.engine.stop()
        AudioSegment.from_file(path_to_save).export(mp3path, format="mp3")

    class _TTS:

        engine = None
        rate = None

        def __init__(self):
            self.engine = pyttsx3.init()

        def start(self, text_):
            self.engine.say(text_)
            self.engine.runAndWait()

        def save_to_file (self, text_, fname):
            self.engine.save_to_file(text_, fname)
            self.engine.runAndWait()

    def CreatePNGFiles (self, words: dict):
        width = 640
        height = 480
        entryct = 0
        img = []
        for y in range(height):
            row = ()
            for x in range(width):
                row = row + (255, 255, 255)
            img.append(row)

        with open('data/white.png', 'wb') as f:
            w = png.Writer(width, height, greyscale=False)
            w.write(f, img)
            f.close()


        for w in words:
            entryct += 1
            img = Image.open('data/white.png')
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 40)
            draw.text((30, 25), str(entryct), font=font, fill='#000000')
            draw.text((30, 100), w, font=font, fill='#000000' )
            tw = textwrap.wrap(words[w], 30)
            ct = 0
            for t in tw:
                ct += 1
                draw.text((30, 120 + 40 * ct), t, font=font, fill='#000000')
            title = str(entryct).zfill(5)
            img.save('data/png/' + title + '.png')




        cmd = ["ffmpeg",
               "-i",
               "./data/png/%05d.png",
               "-c:v",
               "libx264",
               "-r",
               "10",
               "-pix_fmt",
               "yuv420p",
               "/Users/eric/PycharmProjects/DiamondAge/movie.mp4"
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        fout = p.stdin
        fout.close()
        p.wait()
        print(p.returncode)

        lenfac = 8
        cmd = ["ffmpeg",
               "-y",
               "-i",
               "/Users/eric/PycharmProjects/DiamondAge/movie.mp4",
               "-filter:v",
               "setpts=" + str(lenfac) + "*PTS",
               "/Users/eric/PycharmProjects/DiamondAge/moviefps.delta" + str(lenfac) + ".mp4"
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        fout = p.stdin
        fout.close()
        p.wait()
        print(p.returncode)
        #
        # cmd = ["ffmpeg",
        #        "-i",
        #        "/Users/eric/PycharmProjects/DiamondAge/movie.mp4",
        #        "-i",
        #        "/Users/eric/PycharmProjects/DiamondAge/converted.mp3",
        #        "-c:v",
        #        "copy",
        #        "-c:a",
        #        "aac",
        #        "/Users/eric/PycharmProjects/DiamondAge/test.mp4"
        #        ]
        #
        # p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        # fout = p.stdin
        # fout.close()
        # p.wait()
        # print(p.returncode)

    def LookAtVoices():
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        newVoiceRate = 150
        engine.setProperty('rate', newVoiceRate)
        for voice in voices:
            print("Voice:")
            print(" - ID: %s" % voice.id)
            print(" - Name: %s" % voice.name)
            print(" - Languages: %s" % voice.languages)
            print(" - Gender: %s" % voice.gender)
            print(" - Age: %s" % voice.age)



    def Read_Dictionary (self):

        dict_document = '/Users/eric/PycharmProjects/DiamondAge/data/es-en.xml'
        tree= ET.parse(dict_document)
        root = tree.getroot()
        list = root.findall('l')
        for l in list:
            for item in l.findall('w'):
                word = item.find('c')
                definition = item.find('d')
                if word.text is not None and definition.text is not None:
                    try:
                        if not word in self.fulldict:
                            self.fulldict[word.text] = definition.text
                        else:
                            self.fulldict[word.text] = self.fulldict[word.text]  + '; ' + definition.text
                    except:
                        self.logger.info('error, loading word')
                        continue
        self.logger.info('Read Dictionary Entries: ' + str(len(self.fulldict)))
        return self.fulldict

    def Read_Dictionary2 (self):
        from bs4 import BeautifulSoup
        dictpath = '/Users/eric/PycharmProjects/DiamondAge/data/spa-eng.tei.freedict.txt'
        with open(dictpath) as f:
            soup = BeautifulSoup(f, 'xml')

        results = soup.find_all('entry')
        for r in results:
            word = r.find('form').find('orth').text
            definition = r.find('sense').find('cit').find('quote').text
            try:
                if not word in self.fulldict:
                    self.fulldict[word] = definition
                else:
                    self.fulldict[word] = self.fulldict[word] + '; ' + definition
            except:
                continue

        self.logger.info('Read Dictionary Entries: ' + str(len(self.fulldict)))
        return self.fulldict

    def Read_Dictionary_Word2Word_Pkl(self):
        unpickled_df = pd.read_pickle('/Users/eric/PycharmProjects/DiamondAge/data/dictionaries/fr-en.pkl')
        print(unpickled_df)

    def Read_DictionaryProto (self):
        engine = pyttsx3.init()
        newVoiceRate = 150
        engine.setProperty('rate', newVoiceRate)
        pdf_document = "/Users/eric/PycharmProjects/DiamondAge/data/Spanish-English_Dictionary.pdf"
        doc = fitz.open(pdf_document)
        print("number of pages: %i" % doc.pageCount)
        print(doc.metadata)
        entryct = 0
        for i in range(13, doc.pageCount):
            page = doc.loadPage(i)
            pagetext = page.get_text ('blocks')
            for block in pagetext:
                if len(block) >= 4:
                    splitdef = block[4].split('\n')
                    if len(splitdef) >= 2:
                        if len (splitdef [0].split('[')) == 2:
                            engine.setProperty('voice', 'com.apple.speech.synthesis.voice.monica')
                            engine.say(str(splitdef[0].split ('[')[0].strip ()) )
                            engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Alex')
                            engine.say(str(splitdef[1]))
                            entryct +=1
                            if entryct % 100== 0:
                                engine.runAndWait()
        print ("ENTRIES:" + str(entryct))




        # pdf_file = open('Spanish-English_Dictionary.pdf','rb')
        # read_pdf = PyPDF2.PdfFileReader(pdf_file)
        # number_of_pages = read_pdf.getNumPages()
        # for i in range(0, number_of_pages):
        #     page = read_pdf.getPage(i)
        #    # page_content = page.extractText()
        #     print(page.Contents)

    def ReadFrequencies (self, lang):
        f = open ('/Users/eric/PycharmProjects/DiamondAge/data/Frequencies/content/2018/' + lang +'/fr_full.txt', 'r')
        list = f.readlines ()
        listentries = [entry.split () for entry in list]
        freqdict = dict (listentries)
        return freqdict

    def RemoveCharacters (self, str):
        str = str.replace ('Š', '')
        str = str.replace('¿', '')
        str= str.translate(str.maketrans('','', string.punctuation))
        remove_digits = str.maketrans('0123456789', '##########')
        str = str.translate(remove_digits)
        str = str.replace('#','')
        str = str.replace('¡', '')
        return str

    # def scrapeForPDFs (self):
    #     url ='http://google.com/search?q=libros+en+espanol+filetype%3Apdf&num=100'
    #     response = requests.get(url)
    #     print(response.headers)
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #     links = soup.find_all('a')
    #     print (links)
    #     for link in links:
    #         current_link = link.get('href')
    #         if '.pdf' in current_link:
    #             print('Tengo un pdf: ')
    #             #print (current_link)
    #             #h = re.search('(.*?)', current_link)
    #             #if (h is not None):
    #
    #              #   print( h.group(0))
    #
    # def text_from_html(self, body):
    #     def tag_visible(element):
    #         if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
    #             return False
    #         if isinstance(element, Comment):
    #             return False
    #         return True
    #     soup = BeautifulSoup(body, 'html.parser')
    #     texts = soup.findAll(text=True)
    #     visible_texts = filter(tag_visible, texts)
    #     return u" ".join(t.strip() for t in visible_texts)
    #
    #

    def TranslateList (self, langcode, inputlist):
        #to download pkl files from word2word
        # bidir = Word2word("ru", "en", custom_savedir='/Users/eric/PycharmProjects/DiamondAge/data/dictionaries')
        langdata = Word2word.load (langcode, 'en', '/Users/eric/PycharmProjects/DiamondAge/data/dictionaries')
        for i in range (1,10):
            print (inputlist[i] + ':' + langdata [inputlist [i] ])
        return