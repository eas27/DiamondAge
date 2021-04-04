from PyQt5.QtWidgets import *
import PyQt5
from PyQt5.QtCore import Qt
from  WordMoviesUI import Ui_MainWindow
import GenerateLanguageData
import regex

class WordMoviesUIClass(QMainWindow):
    app:QApplication

    def __init__(self, ui, logger, app, parent=None):
        super().__init__(parent)
        self.ui = ui
        self.logger = logger
        self.app = app

    def ErrorMsg (self, errormsg):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Unable to Extract Words")
        msg.setInformativeText(errormsg)
        msg.setWindowTitle("Extract Words Error")
        self.app.restoreOverrideCursor()
        retval = msg.exec_()

    def do_ExtractWords(self):
        print('test pressed')

        GLD = GenerateLanguageData.GLD (self.logger)
        worddict = GLD.GenerateWordList(self.ui.InputText.toPlainText ())
        outtext = ''
        self.app.setOverrideCursor (Qt.WaitCursor)

        try:
            lastw = int(self.ui.WordLimitTB.toPlainText ())
        except:
            print ('error')
            self.ErrorMsg("Word Limit must be an integer")
            return

        firstNwords = {k: worddict[k] for k in list(worddict)[:lastw]}
        ct = 0

        inlang = self.ui.InputLangCB.currentText ().split ('-')[0]
        outlang = self.ui.OutputLangCB.currentText().split('-')[0]
        print(inlang)
        if (inlang == '' or inlang == '<None>'):
            self.ErrorMsg("In language not specified")
            return
        print(outlang )
        if (outlang == '' or outlang == '<None>'):
            self.ErrorMsg("Out language not specified")
            return

        for w in firstNwords:
            ct = ct + 1
            try:
                translation = GLD.TranslateWord(w, inlang , outlang)
                line =  str(ct) + ','  + w +  ',' + str(worddict [w]) + ',' + translation.text +  '\n'
                outtext += line
                self.ui.StatusLabel.setText(line)
            except:
                self.ui.StatusLabel.setText (str(ct) + 'error')
                continue
        self.ui.OutputTextEdit.setText(outtext)
        self.app.restoreOverrideCursor()

    def do_MakeMovie (self):
        print('Make Movie')
        fname = self.Run_FileChooser()
        inlang = self.ui.InputLangCB.currentText ().split ('-')[0]
        print(inlang)
        if (inlang == ''):
            print ('Failed: no input language')
            return
        outlang = self.ui.OutputLangCB.currentText().split('-')[0]
        print(outlang)
        if (outlang == ''):
            print('Failed: no output language')
            return

        infirst = self.ui.InputFirstRB.isChecked ()

        filetext = self.ui.OutputTextEdit.toPlainText ()
        lines = filetext.splitlines()
        wdict = {}
        for l in lines:
            w_d = l.split(',')
            print (w_d)
            isword, cleanedword = self.checkword (w_d [1])
            if isword:
                wdict[cleanedword] = w_d[3]
        if wdict != {}:
            GLD = GenerateLanguageData.GLD(self.logger)
            GLD.CreateAVMovie(fname, wdict, inlang, outlang, infirst)
            #'/Users/eric/PycharmProjects/DiamondAge/results/German/newMovie.mp4'

    def checkword (self, w):
        w = w.replace('.','')
        w = w.replace('?', '')
        w = w.replace(':', '')
        w = w.replace('"','')
        x=  regex.search ('[0-9]', w)
        print (x)
        if x is not None:
            return False, None
        else:
            return True, w

    def Run_FileChooser (self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.mp4)", options=options)
        if fileName:
            print(fileName)
            return fileName
        return None