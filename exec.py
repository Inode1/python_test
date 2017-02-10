from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, ConversationHandler
from telegram import InlineQueryResultArticle, ChatAction, InputTextMessageContent, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardHide
from uuid import uuid4
import subprocess
import time
import logging

EXECUTE = 1

message_id = 0

def start(bot, update):
    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id, text="Admin mode enable")

    keyboard = [[InlineKeyboardButton("Show filter options", callback_data='/option'),
                 InlineKeyboardButton("Show filter status", callback_data='/stat')],

                [InlineKeyboardButton("Restart filter", callback_data='/restart')],

                [InlineKeyboardButton("Disable admin mode", callback_data='/stop')]]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    print "update.message.message_id: ", update.message.message_id

    message = update.message.reply_text('Please choose:', reply_markup=reply_markup)

    message_id = message.message_id

    print message_id, '\n'

    return EXECUTE

def changeMarkup(bot, update):
    update.message.reply_text("", reply_markup=ReplyKeyboardHide());

def execute(bot, update, direct=True):
    try:
        user_id = update.message.from_user.id
        command = update.message.text
        inline = False
    except AttributeError:
        # Using inline
        user_id = update.inline_query.from_user.id
        command = update.inline_query.query
        inline = True

    if command == "Disable admin mode":
        update.message.reply_text("Admin mode disable", reply_markup=ReplyKeyboardHide())
        return cancel(bot, update)

    if command == "Change Screen":
        changeMarkup(bot, update)
        return EXECUTE
    #if user_id == int(config['ADMIN']['id']):
    if not inline:
        bot.sendChatAction(chat_id=update.message.chat_id,
                           action=ChatAction.TYPING)
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = output.stdout.read().decode('utf-8')
    output = '`{0}`'.format(output)

    if not inline:
        bot.sendMessage(chat_id=update.message.chat_id,
                    text=output, parse_mode="Markdown")
        return EXECUTE
    else:
        return output
def stat(bot, update):
    try:
        user_id = update.message.from_user.id
        command = update.message.text
        inline = False
    except AttributeError:
        # Using inline
        user_id = update.inline_query.from_user.id
        command = update.inline_query.query
        inline = True

    output = "Status message"

    if not inline:
        bot.sendMessage(chat_id=update.message.chat_id,
                    text=output, parse_mode="Markdown")
        return EXECUTE
    else:
        return output


def inlinequery(bot, update):
    query = update.inline_query.query
    o = execute(query, update, direct=False)
    results = list()

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title=query,
                                            description=o,
                                            input_message_content=InputTextMessageContent(
                                                '*{0}*\n\n{1}'.format(query, o),
                                                parse_mode="Markdown")))

    bot.answerInlineQuery(update.inline_query.id, results=results, cache_time=10)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def cancel(bot, update):
    print "cancel"
    return ConversationHandler.END

def option(bot, update):
    print "option"
    return ConversationHandler.EXECUTE

def stat(bot, update):
    print "stat"
    return ConversationHandler.EXECUTE

def restart(bot, update):
    print "restart"
    return ConversationHandler.EXECUTE

def main():
    token = '284260959:AAGGCPph9pwGw_U468Ny2IcsqyQCpwTxTe8'

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            EXECUTE: [CommandHandler('option', option),
                      CommandHandler('stat', stat),
                      CommandHandler('restart', restart),
                      MessageHandler(Filters.text, execute)],
        },

        fallbacks=[CommandHandler('stop', cancel)]
    )

    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()