from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from internal import interface, common


class WewallExpertInlineKeyboardGenerator(interface.IWewallExpertInlineKeyboardGenerator):
    def __init__(self):
        pass

    async def start(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="Подбор недвижимости",
                                  callback_data=common.WewallExpertKeyboardCallbackData.to_estate_search)],
            [InlineKeyboardButton(text="Оценка доходности",
                                  callback_data=common.WewallExpertKeyboardCallbackData.to_estate_finance_model)],
            [InlineKeyboardButton(text="Тренды и новости",
                                  callback_data=common.WewallExpertKeyboardCallbackData.to_estate_expert)],
            [InlineKeyboardButton(text="Связаться с менеджером",
                                  callback_data=common.WewallExpertKeyboardCallbackData.to_manager)],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

        return keyboard

    async def check_subscribe(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться", url="https://t.me/wewall_ru")],
            [InlineKeyboardButton(text="Проверить подписку",
                                  callback_data=common.WewallExpertKeyboardCallbackData.check_subscribe)],
        ])
        return keyboard
