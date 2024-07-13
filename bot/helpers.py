

import requests
from typing import Union
from bot.instances import custom_ratio, profit_ratio
import config
import math


class Currency:
    def __init__(self):
        self.rub_per_yen: float = 0
        self.usd_per_yen: float = 0
        self.euro_per_yen: float = 0
        self.init()

    def init(self):
        # Получение текущего курса йены к рублю / к usd
        response = requests.get('https://api.exchangerate-api.com/v4/latest/CNY')
        rates = response.json()['rates']
        self.rub_per_yen = rates['RUB']
        self.usd_per_yen = rates['USD']
        self.euro_per_yen = rates['EUR']


class Calculator:
    def __init__(self, currency: Currency):
        self.currency = currency
        self.start_yen_amount = 0
        self.cost_of_custom_house = 0
        self.result_in_rub = 0
        self.delivery_cost = 0
        self.profit = 0
        self.delivery_prices = {'Верхняя одежда': 3000,
                                'Обувь': 3500,
                                'Одежда': 2500, }

    def convert_yen_to_rub(self, yen) -> float:
        return yen * self.currency.rub_per_yen

    def get_cost_of_custom_house(self, yen_amount: int) -> float:
        # таможенный сбор
        if self.over_limit(yen_amount, self.currency.euro_per_yen):
            self.cost_of_custom_house = yen_amount * custom_ratio
        return self.cost_of_custom_house

    def get_delivery_cost(self, category):
        for key in self.delivery_prices:
            if key in category:
                self.delivery_cost = self.delivery_prices[key]
        return self.delivery_cost

    def cost_calculation(self, context, yen_amount, category) -> float:  # returns RUBs
        self.start_yen_amount = yen_amount
        self.get_cost_of_custom_house(yen_amount)

        yen_amount = (yen_amount + self.cost_of_custom_house)  # yen_amount + custom

        self.profit = int(self.convert_yen_to_rub(yen_amount * profit_ratio))
        self.delivery_cost = self.get_delivery_cost(category)

        result_in_rub = self.convert_yen_to_rub(yen_amount) + self.delivery_cost + self.profit
        self.result_in_rub = self.round_up(result_in_rub)

        return self.result_in_rub

    @staticmethod
    def round_up(value: Union[int, float]) -> int:
        return math.ceil(value / 100) * 100

    def over_limit(self, yen_amount, currency):
        limit = 190
        total = yen_amount * currency
        if total > limit:
            return True
        else:
            return False


def message_handler(username, user_id, calculator: Calculator):
    message = ''.join([f'User: {username}', '\n',
                       f'ID: {user_id}', '\n',
                       # f'[Ссылка на профиль](tg://user?id={user_id})', '\n',
                       f'Запрошенная сумма в CYN: {calculator.start_yen_amount}', '\n',
                       # f'Категория: {category}', '\n',
                       f'Таможенный сбор: {calculator.cost_of_custom_house}', '\n',
                       # f'Profit: {calculator.profit} ₽', '\n',
                       f'Доставка: {calculator.delivery_cost}', '\n',
                       f'Итого: {calculator.result_in_rub} ₽', '\n',
                       ])
    return message


def push(context, username, user_id, calculator):
    message = message_handler(username, user_id, calculator)
    for subscriber in config.subscribers:
        context.bot.send_message(chat_id=subscriber, text=message)
