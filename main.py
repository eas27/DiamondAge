from datetime import datetime
from datetime import timedelta
from fpdf import FPDF
import GenerateLanguageData
import WebsiteSearcher
import DBrunner
import logging
import os
import defs
from pandas import DataFrame
import itertools
import ArticleParser
from os import listdir
from os.path import isfile, join
import test
import sys
from PyQt5.QtWidgets import *
from tei_reader import TeiReader
import googletrans
import WordMoviesUI
import WordMoviesUIClass
import AV_Generation

def current_test():
    RunUIWordExtractor ()
    #AV = AV_Generation.AV_Generation (logger)
    #AV.FixMovie ('/Users/eric/PycharmProjects/DiamondAge/Results/German/Eric100WordsGerman.mp4')

def RunUIWordExtractor ():
    app = QApplication(sys.argv)
    gallery = WordMoviesUI.Ui_MainWindow ()
    window = WordMoviesUIClass.WordMoviesUIClass(gallery, logger, app)
    gallery.setupUi(window)
    window.show()
    sys.exit(app.exec_())

def make_movie_from_csv ():
    f = open ('/Users/eric/PycharmProjects/DiamondAge/data/German/ArticleGermanWords.csv')
    filetext = f.read ()
    f.close ()
    lines = filetext.splitlines ()
    wdict = {}
    for l in lines[1:]:
        w_d = l.split (',')
        wdict [w_d [1]] = w_d [0]
    print (wdict)
    GLD = GenerateLanguageData.GLD (logger)
    GLD.CreateAVMovie('/Users/eric/PycharmProjects/DiamondAge/results/German/ArticleGermanWords.mp4', wdict, 'de','en', True)



def gradelevelwordstest ():
    DB= DBrunner.DBrunner ()
    DB.ConnectToDB('DiamondAgeDB', 'eric', input('DB Pass:'))
    wordlist = DB.Get_EN_GradeLevelList ()
    print (wordlist [0])
    grade1 = list(filter(lambda x: x[1] == 1, wordlist))
    GLD = GenerateLanguageData.GLD(logger)
    enfrdict = GLD.Read_TextDictionary ('/Users/eric/PycharmProjects/DiamondAge/data/French/thevore.com_FreeDict_EnglishToFrench.txt', '\t')
    csvlist = ''
    for entry in list(grade1):
        if csvlist != '':
            csvlist += ','
        csvlist += entry [0]
        trans1 = googletrans.Translator()
    #res = trans1.translate(text=csvlist, dest='fr')

    f = open ('/Users/eric/PycharmProjects/DiamondAge/Results/frenchlist_GL.txt', 'a')
    f.write (str(csvlist))
    f.close ()

        # if entry [0] in enfrdict:
        #     print (entry [0] + ':' + enfrdict [entry[0]])
        # else:
        #     print (entry [0] + ': NO DEF')
    # GLD.CreateAVMovie('/Users/eric/PycharmProjects/DiamondAge/Results/1000GermanWords/', allwords, 'de')


def testtrans ():
    trans1 = googletrans.Translator()
    res = trans1.translate(text='bien, jamais, rien', dest = 'en')
    print (res)

def LoadToDB():
    dbr = DBrunner.DBrunner()
    dbr.ConnectToDB('DiamondAgeDB', 'eric', input('DB Pass:'))
    # dbr.Upload_ToWordListTable('\"DA_Dictionaries\"', 'da_de_wordlist', '/Users/eric/PycharmProjects/DiamondAge/data/German/deutsch.txt', 4)
    dbr.Upload_ToFreqTable('\"DA_Dictionaries\"', 'da_word_freq', 'ja',
                           '/Users/eric/PycharmProjects/DiamondAge/data/Frequencies_HermitDave/content/2018/ja/ja_full.txt',5)

def PArseArticle2 ():
    fpdf = FPDF()
    fpdf.add_font('ArialUnicode', fname='/Users/eric/Library/Fonts/Arial-Unicode-Regular.ttf', uni=True)
    fpdf.set_font('ArialUnicode', '', 14)
    onlypdffiles = [f for f in listdir('/Users/eric/Desktop/Articles/') if
                    ".pdf" in f and isfile(join('/Users/eric/Desktop/Articles/', f))]
    print(onlypdffiles)
    aparser = ArticleParser.ArticleParser()
    for fname in onlypdffiles[0:10]:
        print(fname)
        aparser.Get_MainText('/Users/eric/Desktop/Articles/' + fname, fpdf)
    today = datetime.now()
    #fpdf.set_compression(0)
    fpdf.output("Results/articles" + str(today.year) + str(today.month) + str(today.day) + ".pdf")


def TeiRead ():
    reader = TeiReader()
    corpora = reader.read_file('/Users/eric/PycharmProjects/DiamondAge/data/dictionaries-master/eng-gle/eng-gle.tei', )
    print(corpora.text)

def ArticleParserTest ():
    fpdf = FPDF()
    fpdf.add_font('ArialUnicode', fname='/Users/eric/Library/Fonts/Arial-Unicode-Regular.ttf', uni=True)
    fpdf.set_font('ArialUnicode', '', 11)
    aparser = ArticleParser.ArticleParser()
    #pagetext = aparser.ParseScientificArticle('/Users/eric/Desktop/Articles/BERT.1810.04805.pdf', None, ['abstract', 'references'])
    pagetext = aparser.ParseScientificArticle('/Users/eric/Desktop/Articles/1912.02292.pdf', fpdf, ['abstract', 'references'])
    today = datetime.now()
    fpdf.set_compression(0)
    fpdf.output("Results/articles" + str(today.year) + str(today.month) + str(today.day) + ".pdf")

def PYQT_Test ():
    class testWindow(QMainWindow):
        def __init__(self, parent=None):
            super().__init__(parent)
        def testbutton_pressed (self):
            print ('test pressed')
        def pushButton_released (self):
            print('Push_Button Released')
    app = QApplication(sys.argv)
    window = testWindow ()
    gallery = test.Ui_MainWindow()
    gallery.setupUi(window)
    window.show ()
    sys.exit(app.exec_())

def Make_1000GermanWords ():
    d = open('/Users/eric/PycharmProjects/DiamondAge/data/German/1000GermanWords.txt')
    wordlist = d.read ()
    lines = wordlist.splitlines ()
    wFound = False
    startdef = False
    allwords = {}
    for l in lines:
        if l.isnumeric():
            startdef = True
        elif startdef == True:
            w = l
            startdef = False
            wFound = True
        elif wFound == True:
            wFound = False
            allwords [w] = l
    GLD = GenerateLanguageData.GLD(logger)
    GLD.CreateAVMovie( '/Users/eric/PycharmProjects/DiamondAge/Results/1000GermanWords/', allwords, 'de', 'en' , True)


def PDFParseTest ():
    fpdf = FPDF()
    fpdf.add_font('ArialUnicode', fname='/Users/eric/Library/Fonts/Arial-Unicode-Regular.ttf', uni=True)
    fpdf.set_font('ArialUnicode', '', 11)
    onlypdffiles = [f for f in listdir('/Users/eric/Desktop/Articles/') if ".pdf" in f and isfile(join('/Users/eric/Desktop/Articles/', f))]
    print (onlypdffiles)
    aparser = ArticleParser.ArticleParser()
    for fname in onlypdffiles[0:10]:
        print (fname)
        aparser.ParseScientificArticle('/Users/eric/Desktop/Articles/' + fname, fpdf, None)
    today = datetime.now()
    fpdf.set_compression(0)
    fpdf.output("Results/articles" + str(today.year) + str(today.month) + str(today.day) + ".pdf")






    #aparser.ParseScientificArticle('/Users/eric/Desktop/Articles/acs.jcim.8b00706.pdf')
    #db = DBrunner.DBConnector ()
    #db.test_docker()

    # pdf = FPDF()
    # pdf.set_font("Arial", size=15)
    #
    # earlydate = datetime.now() - timedelta(days=365)
    # print(earlydate)
    # GLD = GenerateLanguageData.GLD()
    # freq = GLD.ReadFrequencies('de')
    # outdict = GLD.Read_TextDictionary('/Users/eric/PycharmProjects/DiamondAge/data/German/de-en.txt', '::')
    #
    # filtered_freq = {k: v for (k, v) in freq.items() if int(v) > 10000}
    # df = DataFrame(columns=('word', 'def', 'freq'))
    # for w in outdict:
    #     if w in freq:
    #         freqct = freq[w]
    #     else:
    #         freqct = -1
    #     df.loc[len(df)] = [w, outdict[w], freqct]
    #     print(len(df))
    # for i, r in df.iterrows():
    #     print(r['word'] + ':' + r['def'])

    # WSS.searchArXiv('all:machine%20AND%20learning', earlydate, pdf)
    # WSS.searchArXiv('all:deep%20AND%20learning', earlydate, pdf)
    # WSS.searchArXiv('au:bengio+AND+yoshua', earlydate, pdf)
    # WSS.searchArXiv('ti:machine%20AND%20learning%20AND%20review', earlydate, pdf)
    # WSS.searchArXiv('ti:deep%20AND%20learning%20AND%20review', earlydate, pdf)
    # WSS.searchWikipedia ('Cancer')
    # WSS.searchGoogleScholar('q=Deep Learning', 10)
    # WSS.searchBioRxiv('transcription AND factor')

    # pdf.output("Results/2021_03_01_reviews_"+str(datetime.now().year)+str(datetime.now().month)+str(datetime.now().day)+".pdf")

    # GLD = GenerateLanguageData.GLD ()
    # text = WSS.GetYahooNews('es')
    # wordlist = GLD.GenerateWordList(text)
    # words = GLD.GetDefs(wordlist)
    # GLD.ReadWords(words)
    # GLD.SaveWordsToAudioFile(words)
    # GLD.CreatePNGFiles (dict)

    # GLD = GenerateLanguageData.GLD ()
    # freqdict = GLD.ReadFrequencies('es')
    # #WSS = WebsiteSearcher.WebsiteSearcher ()
    # in_dict = GLD.Read_Dictionary()
    # freqdefs = GLD.GetDefs(freqdict)
    # #GLD.CreateDictMovie(freqdefs)
    # GLD.CreateAVMovie(dict(itertools.islice(freqdefs.items(), None)), 'es')

    # freqdict = GLD.ReadFrequencies()
    # text = WSS.GetYahooNews('es')
    # wordlist = GLD.GenerateWordList(text)
    # words = GLD.GetDefs(wordlist)
    #
    # wfreq = [[w, words [w], int(freqdict [w])] for w in words]
    # df = DataFrame (wfreq, columns = ['word', 'def', 'freq'])
    # df = df.sort_values (by='freq', ascending=False)
    # sortedwords = df.set_index('word').T.to_dict('records')[0]
    #
    # GLD.CreatePNGFiles (sortedwords)

    # freq = GLD.ReadFrequencies('fr')
    # outdict = GLD.Read_Dictionary_dictcc('fr')
    # defsdict= GLD.lookupWords(freq.keys(), outdict)
    # outdict = GLD.TranslateList('fr', list(freq.keys()))
    # GLD.generate_dictionary_file(defs.RESULTS_PATH + 'fr_freq_w2w_dict.txt', outdict)

    # words = dict(itertools.islice(defsdict.items(), 1000))
    # for w in words:
    #     if defsdict[w] == 'no dictionary entry':
    #         lemma = GLD.Lemmatize_word('fr', w)
    #         if lemma is not None:
    #             if lemma in outdict:
    #                 lemmadef = outdict[lemma]
    #                 defsdict[w] = lemmadef
    #             else:
    #                 print(w + ':' + lemma)
    #         else:
    #             print (w + ':' + 'no lemma')

    import nltk
    import nltk.corpus
    import transforms
    from nltk.stem import WordNetLemmatizer
    # from nltk.corpus import wordnet as wn
    # res = wn.synsets('bank')[0].lemma_names('spa')
    # print (res)

    # nltk.download('averaged_perceptron_tagger')
    # nltk.download('omw')

    # stem = stemmer.stem('parler')
    # lemma = lemmatizer.lemmatize('parle', 'v')
    # synsets=wn.synsets('gouvernement',lang=u'fre')
    # synsets = wn.synsets('parles',pos='v',lang='fr')
    # GLD.CreateAVMovie(words, 'fr')

    # lemmatizer = WordNetLemmatizer()
    # stemmer = nltk.stem.snowball.FrenchStemmer()
    # stemdict = {}
    # for w in outdict:
    #     stemdict[stemmer.stem(w)] = outdict[w]

    # print('parles' + ':' + stemdict [stemmer.stem('parles') ])
    import pattern3.text.fr as lemFre
    # import pattern3.text.en as lemEng

    # print(lemEng.parse('I ate many pizzas', lemmata=True).split(' '))
    # x = lemFre.Parser()
    # f = lemFre.Sentence(lemFre.parse('tu es ici', lemmata=True)).lemmata
    # print (f)
    # import spacy
    # nlp = spacy.load("es_core_news_sm")

    # import AV_Generation
    # av = AV_Generation.AV_Generation ()
    # av.MovieFrom_pngList ('/Users/eric/PycharmProjects/DiamondAge/Results/png/', '/Users/eric/PycharmProjects/DiamondAge/Results/mp4/fullmovie_noaudio.mp4')
    # logger.info ('End logging')
    # exit()

print(os.getcwd())
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s',filename='/Users/eric/PycharmProjects/DiamondAge/Results/scraper.log')
logger = logging.getLogger()
logger.info('Start logging')
current_test()



