from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from internal import interface, common


class PostShortLinkInlineKeyboardGenerator(interface.IPostShortLinkInlineKeyboardGenerator):

    async def start(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(
                text="Связаться с менеджером",
                callback_data=common.WewallExpertKeyboardCallbackData.to_manager
            )],
            [InlineKeyboardButton(
                text="Функции бота",
                callback_data=common.WewallExpertKeyboardCallbackData.start
            )],
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard)

        return keyboard
