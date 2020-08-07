import googletrans
import DBController as dbController
# A speech Recognition library
import speech_recognition as sr
# Audio file conversion
import ftransc.core as ft
import logging as logger
import os

def langCodes():
    LANGUAGES = googletrans.LANGUAGES
    LANGCODES = dict(map(reversed, LANGUAGES.items()))
    return LANGCODES

def langNames():
    return googletrans.LANGUAGES

def updateLanguageTranslation(user, language):
    boolInsert = dbController.insertNewUser(user, "en", language)
    if not boolInsert:
        dbController.updateUser(user, language, True)

def updateLanguageInputDefault(user, language):
    boolInsert = dbController.insertNewUser(user, language, "es")
    if not boolInsert:
        dbController.updateUser(user, language, False)

def audioConversionToText(voice, langCode, user):
    ft.transcode(voice.download('file{}.ogg'.format(user)), 'wav')

    # extract voice from the audio file
    r = sr.Recognizer()
    with sr.WavFile('file{}.wav'.format(user)) as source:
        #r.adjust_for_ambient_noise(source) # Optional
        audio = r.record(source)


    os.remove('file{}.ogg'.format(user))
    os.remove('file{}.wav'.format(user))
    translator = Translator()
    # Convert voice to text
    try:
        txt = r.recognize_google(audio, language=langCode)
        logger.info(txt)
    except sr.UnknownValueError:
        logger.warn('Speech to Text could not understand audio')
        return "errorAudio"
    except sr.RequestError as e:
        logger.warn('Could not request results from Speech to Text service; {0}'.format(e))
        return "errorService"

    return txt
