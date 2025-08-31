from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from internal import interface, common


class EstateSearchInlineKeyboardGenerator(interface.IEstateSearchInlineKeyboardGenerator):
    def __init__(self):
        pass

    async def middle_offer(self, current_offer_id: int) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(
                text="Записаться на просмотр",
                callback_data=common.EstateSearchKeyboardCallbackData.like_offer+f":{current_offer_id}"
            )],
            [InlineKeyboardButton(
                text="Следующее предложение",
                callback_data=common.EstateSearchKeyboardCallbackData.next_offer+f":{current_offer_id}"
            )],
            [InlineKeyboardButton(
                text="Другой объект",
                callback_data=common.EstateSearchKeyboardCallbackData.next_estate + f":{current_offer_id}"
            )],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

        return keyboard

    async def last_estate(self, current_offer_id: int) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(
                text="Записаться на просмотр",
                callback_data=common.EstateSearchKeyboardCallbackData.like_offer+f":{current_offer_id}"
            )],
            [InlineKeyboardButton(
                text="Следующее предложение",
                callback_data=common.EstateSearchKeyboardCallbackData.next_offer+f":{current_offer_id}"
            )],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

        return keyboard
    async def last_offer(self, current_offer_id: int) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(
                text="Записаться на просмотр",
                callback_data=common.EstateSearchKeyboardCallbackData.like_offer+f":{current_offer_id}"
            )],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

        return keyboard
