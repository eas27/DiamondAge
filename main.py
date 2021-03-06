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

print(os.getcwd())
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s',filename='/Users/eric/PycharmProjects/DiamondAge/Results/scraper.log')
logger = logging.getLogger()


logger.info('Start logging')
pdf = FPDF()
pdf.set_font("Arial", size = 15)

earlydate = datetime.now()-timedelta(days=365)
print(earlydate)

# WSS.searchArXiv('all:machine%20AND%20learning', earlydate, pdf)
# WSS.searchArXiv('all:deep%20AND%20learning', earlydate, pdf)
# WSS.searchArXiv('au:bengio+AND+yoshua', earlydate, pdf)
#WSS.searchArXiv('ti:machine%20AND%20learning%20AND%20review', earlydate, pdf)
#WSS.searchArXiv('ti:deep%20AND%20learning%20AND%20review', earlydate, pdf)
#WSS.searchWikipedia ('Cancer')
#WSS.searchGoogleScholar('q=Deep Learning', 10)
#WSS.searchBioRxiv('transcription AND factor')

#pdf.output("Results/2021_03_01_reviews_"+str(datetime.now().year)+str(datetime.now().month)+str(datetime.now().day)+".pdf")


#GLD = GenerateLanguageData.GLD ()
#text = WSS.GetYahooNews('es')
#wordlist = GLD.GenerateWordList(text)
#words = GLD.GetDefs(wordlist)
#GLD.ReadWords(words)
#GLD.SaveWordsToAudioFile(words)
#GLD.CreatePNGFiles (dict)

WSS = WebsiteSearcher.WebsiteSearcher ()
GLD = GenerateLanguageData.GLD ()
# dict = GLD.Read_Dictionary()
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

freq = GLD.ReadFrequencies('fr')
outdict = GLD.Read_Dictionary_dictcc ('fr')
defsdict= GLD.lookupWords(freq.keys(), outdict)
#outdict = GLD.TranslateList('fr', list(freq.keys()))
#GLD.generate_dictionary_file(defs.RESULTS_PATH + 'fr_freq_w2w_dict.txt', outdict)
words = dict(itertools.islice(defsdict.items(), 1000))
for w in words:
    if defsdict [w] == 'no dictionary entry':
        print (w + ':' + defsdict [w] )
        GLD.Lemmatize_word (w)






#GLD.CreateAVMovie(words, 'fr')

logger.info ('End logging')
exit()


