from aiogram import Bot
from aiogram.types import InputFile, BufferedInputFile

from internal import interface


async def spam(
        bot: Bot,
        user_service: interface.IUserService,
        keyboard_generator: interface.IPostShortLinkInlineKeyboardGenerator,
        chat_client: interface.IWewallChatClient
):
    print("spam", flush=True)
    formatted_text = """
🔥<b>Легендарная ПРАВДА готовится к старту продаж</b>

Это не только новая архитектурная звезда на карте Москвы, но впечатляющий по удобству и роскошеству проект – общая площадь офисов <b>13000 м²</b>, а <b>более 50%</b> составляют общественные пространства.

Все что есть в самых современных премиальных проектах и сервисных офисах – безусловно есть в «Доме Правды» и намного больше. Например, сигарный клуб и уникальное пространство для мероприятий в историческом Васильковом зале – есть только в «Правде».

К проекту приковано внимание СМИ и в нашем <a href="https://t.me/wewall_ru/1297">недавнем посте</a> мы рассказывали о репортаже от Корреспондента «России 1» Ильи Филиппова, который эксклюзивно снял интересные кадры исторического здания и частично раскрыл будущее «Дома Правды».

💡Если вам интересен «Дом Правды», свяжитесь с нами. Станьте одним из первых собственников Правды!

<b>Дом Правды: все – и ничего кроме.</b>
"""

    with open("Pravda_View040004.jpg", "rb") as f:
        data = f.read()
    photo = BufferedInputFile(data, filename="Pravda_View040004.jpg")
    keyboard = await keyboard_generator.start()

    users = await user_service.all_user()
    for user in users:
        try:
            await bot.send_photo(user.tg_chat_id, photo=photo, caption=formatted_text, parse_mode="HTML", reply_markup=keyboard)
            await chat_client.import_message_to_amocrm(user.tg_chat_id, formatted_text)

        except Exception as e:
            print(f"Ошибка при отправке сообщения для {user.tg_chat_id}: {e}", flush=True)
            await user_service.update_is_bot_blocked(user.id)
            await chat_client.import_message_to_amocrm(user.tg_chat_id, "Пользователь заблокировал бота")
