import googletrans
import DBController as dbController

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
