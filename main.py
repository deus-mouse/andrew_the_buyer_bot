import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
import config

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

categories = ['🧥 Верхняя одежда', '👟 👜 Обувь/аксессуары', '👕 👖 Одежда']
keyboard = [[obj] for obj in categories]

delivery = {'Верхняя одежда': 3000,
            'Обувь': 3500,
            'Одежда': 2500,}

custom_ratio = 0.15
profit_ratio = 1.15


def start(update: Update, context: CallbackContext) -> None:
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Привет! Выберите категорию товара и отправьте мне цену в юанях, и я посчитаю стоимость с доставкой в Москву в рублях.',
                              reply_markup=reply_markup)


class Calculator:
    def __init__(self):
        self.start_yen_amount = 0
        self.cost_of_custom_house = 0
        self.result_in_rub = 0
        self.delivery_cost = 0

    @staticmethod
    def convert_yen_to_rub(yen) -> float:
        return yen * currency.rub_per_yen

    def get_cost_of_custom_house(self, yen_amount: int) -> float:
        # таможенный сбор
        usd = yen_amount * currency.usd_per_yen
        if usd > 190:
            self.cost_of_custom_house = yen_amount * custom_ratio
        return self.cost_of_custom_house

    def cost_calculation(self, yen_amount, category) -> float:  # returns RUBs
        self.start_yen_amount = yen_amount
        self.get_cost_of_custom_house(yen_amount)
        print(f'{self.cost_of_custom_house=}')
        yen_amount = (yen_amount + self.cost_of_custom_house) * profit_ratio
        print(f'{yen_amount=}')
        print(f'{category=}')
        self.delivery_cost = delivery.get(category)
        print(f'{self.delivery_cost=}')
        self.result_in_rub = self.convert_yen_to_rub(yen_amount) + self.delivery_cost
        print(f'{self.result_in_rub=}')

        return self.result_in_rub


class Currency:
    def __init__(self):
        self.rub_per_yen: float = 0
        self.usd_per_yen: float = 0
        self.init()

    def init(self):
        # Получение текущего курса йены к рублю / к usd
        response = requests.get('https://api.exchangerate-api.com/v4/latest/CNY')
        rates = response.json()['rates']
        self.rub_per_yen = rates['RUB']
        self.usd_per_yen = rates['USD']


def handle_message(update: Update, context: CallbackContext) -> None:
    category = update.message.text
    if category in categories:
        update.message.reply_text(f'Вы выбрали категорию [{category}]. Теперь отправьте мне сумму в юанях.')
        context.user_data['category'] = category

    else:
        try:
            calculator = Calculator()
            yen_amount = float(update.message.text)
            cost = calculator.cost_calculation(yen_amount, context.user_data['category'])

            update.message.reply_text(
                f'Cтоимость с доставкой в Москву {cost} рублей.\n\n'
                f'Cамовывоз г. Москва ЖК Матч Поинт или доставка СДЭК 500р.\n\n'
                f'Среднее время доставки до Москвы 3 недели.\n\n'
                f'Для заказа напиши https://t.me/andrewthebuyer')

            # mention = '[andrewthebuyer](tg://user?id=251890418)'
            # update.message.reply_text(mention, parse_mode='Markdown')

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
    currency = Currency()
    main()
