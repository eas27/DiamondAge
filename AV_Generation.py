import os
import defs
import subprocess
import sys
import time
from pydub import AudioSegment
import png
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import textwrap
import pyttsx3
import glob
import shutil
import logging
from gtts import gTTS


class AV_Generation:
    engine:pyttsx3.Engine
    logger:logging.Logger

    def __init__(self, logger):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 400)
        self.logger = logger
        return

    def MovieFrom_pngList (self, fpath, outpath):
        if outpath.find('.mp4') < 0:
            'error--incomplete file specification: ' + outpath
            return
        cmd = ["ffmpeg",
               "-y",
               "-i", fpath + '%05d.png',
               "-c:v", "libx264",
               "-framerate", "30000/1001",
 #              "-r", "1",
               "-pix_fmt", "yuv420p",
               outpath
               ]


        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        f_out = p.stdin
        f_out.close()
        p.wait()
        print('append complete: ' + outpath + 'full_move.mp4')
        lenfac = 16
        self.stretch_mp4 (outpath, outpath.replace(".mp4", ".lenX" + str(lenfac) + ".mp4", lenfac), lenfac)

    def MakeMP4_from_PngFiles (self, pngpath):
        outpath = pngpath.replace('png', 'temp_mp4') + "movie"".mp4"
        print (outpath)
        cmd = ["ffmpeg",
               "-y",
               "-i", '%s' % (pngpath + '%05d.png'),
               "-c:v", "libx264",
             #   "-framerate", "30000/1001",
             #  "-r", "1",
               "-pix_fmt", "yuv420p",
               outpath
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        f_out = p.stdin
        f_out.close()
        p.wait()
        return outpath

    def MakeMP4_from_Png (self, pngpath, entrynum):
        outpath = pngpath.replace ('png', 'temp_mp4') + "movie" + str (entrynum) + ".mp4"

        cmd = ["ffmpeg",
               "-hide_banner",
               "-loglevel","error",
               "-y",
               "-framerate",
               "1/4",
               "-i", pngpath + str(entrynum).zfill (5) + '.png',
               "-c:v", "libx264",
               "-pix_fmt", "yuv420p",
               outpath
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        f_out = p.stdin
        f_out.close()
        p.wait()
        return outpath

    def stretch_mp4 (self, mp4, outmp4, lenfac):
        cmd = ["ffmpeg",
               "-y",
               "-i",
               mp4,
               "-filter:v",
               "setpts=" + str(lenfac) + "*PTS",
               outmp4
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        fout = p.stdin
        fout.close()
        p.wait()

    def SaveDictWordsToAudioFile(self, outpath, words:dict, inlang:str, outlang:str, currnum:int):
        combind:AudioSegment
        # def getvoice(argument):
        #     switcher = {
        #         'en': 'com.apple.speech.synthesis.voice.Alex',
        #         'es': 'com.apple.speech.synthesis.voice.monica',
        #         'fr': 'com.apple.speech.synthesis.voice.thomas',
        #         'de': 'com.apple.speech.synthesis.voice.anna'
        #     }
        #     return switcher.get(argument, "nothing")

        files = glob.glob(outpath + 'mp3/*')
        for f in files:
            os.remove(f)

        #v1 = getvoice (outlang)
        #v2 = getvoice (inlang)
        entryct = 0

        sys.path.append(defs.FFPROBE_LOC)
        path_to_save = outpath + 'word.mp3'
        path_to_save2 = outpath + 'def.mp3'
        mp3path3 = outpath + 'conv_exp_combo' + str (currnum) + '.mp3'

        self.engine = {}

        for w in words:
            print(w)
            entryct += 1
            tts = gTTS(text=w, lang=inlang)
            tts.save(path_to_save)
            tts = gTTS(text=words [w], lang=outlang)
            tts.save(path_to_save2)

        try:
            combined = AudioSegment.empty()
            combined = combined.append(AudioSegment.silent (duration=700), crossfade=0)
            combined = combined.append(AudioSegment.from_mp3(path_to_save), crossfade=0)
            combined = combined.append(AudioSegment.silent(duration=300), crossfade=0)
            combined = combined.append(AudioSegment.from_mp3(path_to_save2), crossfade=0)
            padlen = 4000 - len(combined)
            combined = combined.append(AudioSegment.silent(duration=padlen), crossfade=0)
            combined.export(mp3path3, format="mp3", codec='mp3')
        except:
            print ('ERROR: SaveDictWordsToAudioFile')
            print(sys.exc_info()[1])

        return mp3path3

    def CreateDictPNGFiles (self, words: dict, outpath,  startnum = 0):
        width = 640
        height = 480
        entryct = startnum
        img = []
        for y in range(height):
            row = ()
            for x in range(width):
                row = row + (255, 255, 255)
            img.append(row)
        if not os.path.exists (defs.DATA_PATH + 'white.png'):
            with open(defs.DATA_PATH + 'white.png', 'wb') as f:
                w = png.Writer(width, height, greyscale=False)
                w.write(f, img)
                f.close()


        for w in words:
            img = Image.open(defs.DATA_PATH + 'white.png')
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
            img.save(outpath + title + '.png')
            entryct += 1
        return outpath, entryct

    def LookAtVoices(self):
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

    def ReadWords(self, lang, words: dict):
        def getvoice(argument):
            switcher = {
                'en': 'com.apple.speech.synthesis.voice.Alex',
                'es': 'com.apple.speech.synthesis.voice.monica',
                'fr': 'com.apple.speech.synthesis.voice.thomas',
                'de': 'com.apple.speech.synthesis.voice.anna'
            }
            return switcher.get(argument, "nothing")
        entryct = 0
        self.engine.setProperty('rate', 300)
        for w in words:
            try:
                self.engine.setProperty('voice', getvoice ('de'))
                self.engine.say(w)
                self.engine.setProperty('voice', getvoice ('en'))
                self.engine.say(words[w])
                self.engine.runAndWait()
            except:
                self.logger.info('--ERROR' + str(sys.exc_info()[0]))
            entryct += 1
        self.engine.runAndWait()

    def CombineAudioVideo (self, vpath, apath, outpath):

        cmd = ["ffmpeg",
               "-y",
               "-hide_banner",
               "-loglevel",
               "error",
               "-i",
               vpath,
               "-i",
               apath,
               #"-c:v", "copy",
               #"-c:a",
               #"aac",
               #"-af", "apad",
               "-filter_complex",  "[1:0]apad",
               "-shortest",
               outpath
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        fout = p.stdin
        fout.close()
        p.wait()
        return outpath

    def append_videos (self, mp4list_path, outpath):
        if outpath.find ('.mp4') < 0:
            'error--incomplete file specification: ' + outpath
            return
        print (outpath + 'full_movie.mp4')
        cmd = ["ffmpeg",
               "-y",
               "-f",
               "concat",
               "-safe",
               "0",
               "-loglevel",
               "error",
               "-i",
               "%s" % mp4list_path,
               "-c",
               "copy",
               "%s" % outpath
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        f_out = p.stdin
        f_out.close()
        p.wait()
        print ('append complete: ' + outpath + 'full_movie.mp4')
        return outpath

    def ClearAVFolders(self, outpath):
        def clearAVtype (t):
            files = glob.glob(outpath + t)
            for f in files:
                if os.path.isdir(f):
                    shutil.rmtree(f)
        clearAVtype('frames')

    def FixMovie (self, moviepath):
        cmd = ["ffmpeg",
               "-y",
               "-i",
               moviepath,
               "-b:v",
               "1M",
               "-b:a",
               "192k",
               "-max_muxing_queue_size",
               "9999",
               moviepath + '_resampled.mp4'
               ]

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        f_out = p.stdin
        f_out.close()
        p.wait()
        #ffmpeg  -i witness.mov -af asetrate=48018 resampled.mkv

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