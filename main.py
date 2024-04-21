import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import config
from helpers import Calculator, Currency, message_handler, push
from instances import keyboard, categories

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



def start(update: Update, context: CallbackContext) -> None:
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Привет! Выберите категорию товара и отправьте мне цену в юанях, и я посчитаю стоимость с доставкой в Москву в рублях.',
                              reply_markup=reply_markup)


def handle_message(update: Update, context: CallbackContext) -> None:
    category = update.message.text
    user_id = None
    username = None
    if category in categories:
        update.message.reply_text(f'Вы выбрали категорию [{category}]. Теперь отправьте мне сумму в юанях.')
        context.user_data['category'] = category

    else:
        try:
            user = update.effective_user
            if user:
                user_id = user.id  # ID пользователя
                username = user.username  # Имя пользователя (может быть None)
                # message_text = f"Ваша ссылка: [Ссылка на профиль](tg://user?id={user_id})"

            currency = Currency()
            calculator = Calculator(currency)
            yen_amount = float(update.message.text)
            cost = calculator.cost_calculation(context, yen_amount, context.user_data['category'])

            update.message.reply_text(
                f'Cтоимость с доставкой в Москву {cost} рублей.\n\n'
                f'Cамовывоз г. Москва ЖК Матч Поинт или доставка СДЭК 500р.\n\n'
                f'Среднее время доставки до Москвы 3 недели.\n\n'
                f'Для заказа напиши https://t.me/andrewthebuyer')

            # mention = '[andrewthebuyer](tg://user?id=251890418)'
            # update.message.reply_text(mention, parse_mode='Markdown')

            push(context, username, user_id, calculator)

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
