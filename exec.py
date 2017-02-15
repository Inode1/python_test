from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, ConversationHandler, Job
from telegram import InlineQueryResultArticle, ChatAction, InputTextMessageContent, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardHide
from uuid import uuid4
import subprocess
import time
import logging
# password qwerty
import crypt

PASSWORDHASH = '$6$i1GrpmnGDHgRljE.$JH84qrxZZAgWMqhtjXNQlczDRIU/kiIq98204qjt0Z5i85j0LKx.V/ApzPpgw8MijyPXWrOAXhc1vFlbdDLoO.'

STOPSERVICE      = "Stop service"
STARTSERVICE     = "Start service"
SHOWSTATUS       = "Show status"
ADMINMODEDISABLE = "Disable admin mode"

message_id = 0

EXECUTE = 1

def alarm(bot, job):
    """Function to send the alarm message"""
    bot.sendMessage(job.context, text='Test job schedule')

def start(bot, update, chat_data, job_queue):
    command = update.message.text

    checkPasswordList = command.split()

    if (len(checkPasswordList) < 2):
        bot.sendMessage(chat_id=update.message.chat_id, text="second argument is password")
        return ConversationHandler.END


    if crypt.crypt(checkPasswordList[1], PASSWORDHASH) != PASSWORDHASH:
        bot.sendMessage(chat_id=update.message.chat_id, text="Wrong password")
        return ConversationHandler.END

    bot.sendChatAction(chat_id=update.message.chat_id,
                       action=ChatAction.TYPING)
    bot.sendMessage(chat_id=update.message.chat_id, text="Admin mode enable")

    update.message.reply_text("Set Job")
    job = Job(alarm, 5, context=update.message.chat_id)
    chat_data['job'] = job
    job_queue.put(job)

    keyboard = [[InlineKeyboardButton(STARTSERVICE),
                 InlineKeyboardButton(STOPSERVICE)],

                [InlineKeyboardButton(SHOWSTATUS)],

                [InlineKeyboardButton(ADMINMODEDISABLE)]]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    return EXECUTE

def changeMarkup(bot, update):
    update.message.reply_text("", reply_markup=ReplyKeyboardHide());

def execute(bot, update, chat_data):
    try:
        user_id = update.message.from_user.id
        command = update.message.text
        inline = False
    except AttributeError:
        # Using inline
        user_id = update.inline_query.from_user.id
        command = update.inline_query.query
        inline = True

    if command == ADMINMODEDISABLE:
        update.message.reply_text("Admin mode disable", reply_markup=ReplyKeyboardHide())
        job = chat_data['job']
        job.schedule_removal()
        del chat_data['job']
        update.message.reply_text("Job is die")
        return cancel(bot, update)
    elif command == STOPSERVICE:
        pass
    elif command == STARTSERVICE:
        pass
    elif command == SHOWSTATUS:
        pass
    else:
        return EXECUTE

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
    o = execute(query, update)
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

def startService(bot, update):
    print "option"
    return ConversationHandler.EXECUTE

def stopService(bot, update):
    print "stat"
    return ConversationHandler.EXECUTE

def showStatus(bot, update):
    print "restart"
    return ConversationHandler.EXECUTE

def main():
    token = '284260959:AAGGCPph9pwGw_U468Ny2IcsqyQCpwTxTe8'

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start,
                                     pass_chat_data=True,
                                     pass_job_queue=True)],

        states={
            EXECUTE: [CommandHandler('start', start),
                      CommandHandler('startService', startService),
                      CommandHandler('stopService', stopService),
                      CommandHandler('status', showStatus),
                      MessageHandler(Filters.text, execute, pass_chat_data=True)],
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