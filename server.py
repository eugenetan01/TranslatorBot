import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
import os
from googletrans import Translator
import Controller as controller
import DBController as dbController
from gtts import gTTS

changetranslationlanguage = 0
setdefaultlanguage = 0

PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi! I'm TranslatorBot! What would you like me to translate today?")

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def languageButtons(update, context):
    placeholder = "Please choose any of the following languages you would like to change to: "
    languages = controller.langCodes()

    keyboard = []
    for key in languages:
        keyboard.append([InlineKeyboardButton(key, callback_data=languages[key])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(placeholder, reply_markup=reply_markup)

    if(update.message.text == "/changetranslationlanguage"):
        return changetranslationlanguage
    else:
        return setdefaultlanguage

def buttonTranslateChange(update, context):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text="Language translation changed to: {}".format(controller.langNames()[query.data]))
    #global language
    #language = query.data
    controller.updateLanguageTranslation(update.callback_query.from_user['username'], query.data)
    return ConversationHandler.END

def buttonInputChange(update, context):
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text="Default Language changed to: {}".format(controller.langNames()[query.data]))
    #global language
    #language = query.data
#    print("im here")
    controller.updateLanguageInputDefault(update.callback_query.from_user['username'], query.data)
    return ConversationHandler.END

def translate(update, context):
    """Translate the user message."""
    defaultLanguage = dbController.getUserDefaultInputLanguage(update.message.from_user['username'])
    language = dbController.getUserDefaultLanguage(update.message.from_user['username'])
    translator = Translator()

    if update.message.voice is not None:
        voice = context.bot.getFile(update.message.voice.file_id)
        toTranslate = controller.audioConversionToText(voice, defaultLanguage, update.message.from_user['username'])
    else:
        toTranslate = update.message.text

    if toTranslate == "errorAudio" :
        update.message.reply_text(translator.translate("Could not understand audio, please send another voice recording please.",src="en", dest=defaultLanguage).text)
    elif toTranslate == "errorService":
        update.message.reply_text(translator.translate("Speech input translation service is down. Please try again later.",src="en", dest=defaultLanguage).text)
    else:
        result = translator.translate(toTranslate, src=defaultLanguage, dest=language)
        update.message.reply_text(result.text)
        if result.pronunciation is not None and result.pronunciation != toTranslate and result.pronunciation != result.text:
                update.message.reply_text(result.pronunciation)

    #else:
    #    errorText = "No text pronunciation available"
    #    update.message.reply_text(translator.translate(errorText, src="en", dest=defaultLanguage).text)

    #send text to speech translation
    try:
        tts = gTTS(result.text, lang=language)
        placeholderEn = "Click here for audio pronunciation in {}: ".format(controller.langNames()[language])
        update.message.reply_text(translator.translate(placeholderEn, src = "en", dest = defaultLanguage).text + tts.get_urls()[0])
    except:
        pass


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    with open('config.json') as config_file:
        data = json.load(config_file)

    TOKEN = data['TOKEN']

    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('setdefaultlanguage', languageButtons)],
        states={
            setdefaultlanguage: [CallbackQueryHandler(buttonInputChange)]
        },
        fallbacks=[CommandHandler('setdefaultlanguage', languageButtons)]
    ))

    dp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('changetranslationlanguage', languageButtons)],
        states={
            changetranslationlanguage: [CallbackQueryHandler(buttonTranslateChange)]
        },
        fallbacks=[CommandHandler('changetranslationlanguage', languageButtons)]
    ))

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.voice, translate))
    dp.add_handler(MessageHandler(Filters.text, translate))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    #updater.start_webhook(listen="0.0.0.0",
    #                      port=int(PORT),
    #                      url_path=TOKEN)
    #updater.bot.setWebhook('https://herokuappname.herokuapp.com/' + TOKEN)


    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
