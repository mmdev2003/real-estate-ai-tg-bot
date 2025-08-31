from internal import interface
from pkg.logger.logger import logger


async def TgNewsParsing(
        news_service: interface.INewsService,
        tg_news_parsing: interface.ITgNewsParsing,
        channel_names: list,
):
    for channel_name in channel_names:
        news = await tg_news_parsing.parse(channel_name)
        await news_service.create_news(channel_name, news)
        logger.info(f"{channel_name} parsed")
