import PyPDF2
import string
import fitz
import pyttsx3
import xml.etree.ElementTree as ET
import logging
import glob
from word2word import Word2word
import pandas as pd
import os
import defs
import AV_Generation
import re
import nltk
from nltk.stem import WordNetLemmatizer
import zipfile
import googletrans

class GLD:
    data: list
    fulldict: dict
    AV:AV_Generation
    logger:logging.Logger
    translator:googletrans.Translator

    def __init__(self, logger):
        self.data = []
        self.fulldict = {}
        self.logger = logging.getLogger()
        self.AV = AV_Generation.AV_Generation(logger)
        self.translator = googletrans.Translator()

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
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:=\-–]')
        for w in splitall:
            skip = False
            w = w.strip().lower()
            for character in w:
                if character.isdigit():
                    skip = True
                elif not regex.search (w) == None:
                    skip = True
            if skip == False:
                if w not in wordlist:
                    wordlist[w] = 1
                else:
                    wordlist[w] = wordlist [w] + 1
        logging.info('Text Word List Length:' + str(len(wordlist)))
        revsort = dict(reversed(sorted(wordlist.items(), key=lambda item: item[1] )))
        return revsort

    def GetDefs (self, worddict:dict):
        outdict:dict
        outdict = {}
        if len(self.fulldict) == 0:
            self.Read_Dictionary (defs.DATA_PATH + "es-en.xml")
        for w in worddict:
            if w in self.fulldict:
                outdict[w] = self.fulldict [w]
        return outdict

    def CreateDictMovie (self, words: dict, outpath):
        self.AV.CreateDictPNGFiles(words, outpath=outpath + 'png/')
        mp4list = glob.glob(outpath +  'png/[0-9]*.png')

        f = open(outpath + 'png/pnglist.txt', 'w')
        for i in sorted(mp4list):
            f.write('file ' + i + '\n')
            print ('file ' + i )
        f.close()
        mp4path = self.AV.MakeMP4_from_PngFiles(outpath + "png/")
        lenfac = 24
        self.AV.stretch_mp4 (mp4path, mp4path.replace(".mp4", ".lenX" + str(lenfac) + ".mp4", lenfac), lenfac)



    def CreateAVMovie (self, outpath, words: dict, inlang:str, outlang:str, inlangFirst=True):
        self.AV.ClearAVFolders(outpath)
        ect = 0
        for w in words:
            print(ect)
            inword = {}
            if inlangFirst:
                inword [w] = words [w]
            else:
                inword[words[w]] = w
            try:
                if inlangFirst:
                    self.add_dict_AV(ect, outpath, inword, inlang, outlang)
                else:
                    self.add_dict_AV(ect, outpath, inword, outlang, inlang)
                ect += 1
            except:
                ect += 1
                continue
        mp4list = glob.glob(outpath + 'frames/frame*/[0-9]*.mp4')
        f = open(outpath + 'frames/mp4list.txt', 'w')
        for i in sorted (mp4list):
             f.write ('file ' + i + '\n')
        f.close()
        avpath = self.AV.append_videos(outpath + 'frames/mp4list.txt', outpath + 'frames/full_movie.mp4')
        return avpath

    def add_dict_AV (self, entrynum, outpath, words:dict, inlang:str, outlang:str):
        def makesubdir (sub):
            path = outpath + sub
            if not os.path.exists(path):
                os.mkdir(path)
            return path
        makesubdir('frames')
        framepath = makesubdir('frames/frame' + str (entrynum).zfill(5) + '/')

        pngpath, nextnum = self.AV.CreateDictPNGFiles(words, framepath, entrynum)
        self.logger.info ('pngs created: ' + framepath)
        mp4path = self.AV.MakeMP4_from_Png(framepath, entrynum)
        self.logger.info('mp4 created: ' + mp4path)
        mp3path = self.AV.SaveDictWordsToAudioFile(framepath, words, inlang, outlang, entrynum)
        self.logger.info('mp3 created: ' + mp3path)
        wordAVmp4path = self.AV.CombineAudioVideo(mp4path, mp3path, framepath + str(entrynum).zfill(5) + '.mp4')
        self.logger.info('Word AV created: ' + wordAVmp4path)
        return

    def Read_Dictionary (self):
        dict_document = defs.DATA_PATH + 'es-en.xml'
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
        dictpath = defs.DATA_PATH + 'spa-eng.tei.freedict.txt'
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

    def dictentry_modify(self, word):
        word = word.lower()
        word = word.replace('qc.', '')
        word = word.replace('{m}', '')
        word = word.replace('{f}', '')
        word = re.sub('\([^\(]+\)', '', word)
        word = re.sub('\{[^\{]+\}', '', word)
        word = re.sub('\[[^\[]+\]', '', word)
        word = word.replace('qn.', '')
        word = word.replace('/', '')
        word = word.strip()
        return word

    def Read_FreeDict (self, inlang, outlang):
        f=open('/Users/eric/PycharmProjects/DiamondAge/data/German/deu-eng/' + inlang +'-' + outlang + '.freedict.txt', 'rb')
        text = f.read().decode ('utf-8')
        f.close()
        lines = text.splitlines ()
        defFound = False
        outdict = {}
        currword = ''
        for l in lines:
            if 'Note:' in l or 'see:' in l or 'Synonym:' in l or l=='\\':
                continue
            else:
                vals = l.split(sep='/')
                if '/' in l:
                    defFound = False
                    currword = vals[0].strip ()
                elif defFound == False:
                    outdict[currword] = vals [0].split(sep=',')[0]
                    defFound = True
        return outdict


    def Read_Dictionary_dictcc(self, lang:str):
        f = open(defs.DATA_PATH + 'dictionaries/' + lang + '.dict.cc.txt')
        text = f.read()
        splitlines = text.splitlines()
        entryct = 0
        pastheader = False
        outdict = {}
        for s in splitlines:
            if not pastheader:
                if s.strip () == '':
                    pastheader = True
                    continue
            else:
                vals = s.split(sep='\t')
                word = self.dictentry_modify (vals [0])
                if not word in outdict:
                    outdict[word] = vals [1]
                else:
                    outdict[word] = outdict [word] + ';' + vals [1]
                entryct += 1
        return outdict

    def Read_DictionaryProto (self):
        engine = pyttsx3.init()
        newVoiceRate = 150
        engine.setProperty('rate', newVoiceRate)
        pdf_document = defs.DATA_PATH  + "Spanish-English_Dictionary.pdf"
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

    def Read_TextDictionary (self, fname, sep):
        f = open(fname, 'r')
        text = f.read()
        splitlines = text.splitlines()
        entryct = 0
        pastheader = False
        outdict = {}
        for s in splitlines:
            if sep in s:
                vals = s.split(sep=sep)
                word = self.dictentry_modify (vals [0])
                if not word in outdict:
                    outdict[word] = vals[1]
                else:
                    outdict[word] = outdict[word] + ';' + vals[1].strip ()
                entryct += 1
        return outdict

    def ReadFrequencies (self, lang):
        f = open(defs.DATA_PATH + 'Frequencies/content/2018/' + lang + '/' + lang + '_full.txt', 'r')
        list = f.readlines()
        listentries = [entry.split() for entry in list]
        freqdict = dict(listentries)
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

    def TranslateListW2W (self, langcode, inputlist):
        langdata = Word2word.load(langcode, 'en', defs.DATA_PATH + 'dictionaries')
        outdict = {}
        for l in inputlist:
            try:
                outdict [l] = langdata(l)[0]
            except:
                continue
        return outdict

    def generate_dictionary_file (self, fpath, inputdict):
        outfile = open (fpath, 'w')
        try:
            for entry in inputdict:
                outfile.write(entry + '\t:\t' + inputdict[entry] + os.linesep)
        finally:
            outfile.close ()

    def lookupWords (self, words: list, in_dict: dict):
        outdict = {}
        failct = 0
        totalct = 0
        for w in words:
            if w in in_dict:
                outdict [w] = in_dict [w]
            else:
                outdict[w] = 'no dictionary entry'
                failct += 1
            totalct += 1
        print (str(failct) + '/' + str (totalct))
        return outdict

    def Lemmatize_word (self, langcode:str,  word:str):
        def getlang (argument):
            switcher = {
                'ar': 'arabic',
                'da': 'danish',
                'nl': 'dutch',
                'fi': 'finnish',
                'de': 'german',
                'hu': 'hungarian',
                'it': 'italian',
                'no': 'norwegian',
                'pt': 'portuguese',
                'ro': 'romanian',
                'ru': 'russian',
                'sv': 'swedish',
                'en': 'english',
                'es': 'spanish',
                'fr': 'french'
            }
            return switcher.get(argument, "nothing")

        lemmatizer = WordNetLemmatizer()
        stemmer = nltk.stem.snowball.SnowballStemmer(getlang(langcode))
        stem = stemmer.stem(word)
        lemma = ( lemmatizer.lemmatize(word))
        return  lemma

    def TranslateWord (self, word, inlang, outlang):
        res = self.translator.translate(text=word, dest=outlang, src= inlang)
        return res
