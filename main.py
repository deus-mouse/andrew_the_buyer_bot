import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправьте мне сумму в йенах, и я конвертирую ее в рубли.')


def convert_yen_to_rub(yen):
    # Получение текущего курса йены к рублю
    response = requests.get('https://api.exchangerate-api.com/v4/latest/JPY')
    rates = response.json()['rates']
    rub_per_yen = rates['RUB']

    return yen * rub_per_yen


def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        yen_amount = float(update.message.text)
        rub_amount = convert_yen_to_rub(yen_amount)
        update.message.reply_text(f'{yen_amount} йен это примерно {rub_amount:.2f} рублей.')
    except ValueError:
        update.message.reply_text('Пожалуйста, отправьте число.')


def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(config.BOT_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
