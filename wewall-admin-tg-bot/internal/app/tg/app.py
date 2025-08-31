from fastapi import FastAPI

from aiogram import Dispatcher
from aiogram.filters import Command

from internal import model, interface, common


def NewTg(
        db: interface.IDB,
        dp: Dispatcher,
        http_middleware: interface.IHttpMiddleware,
        tg_middleware: interface.ITelegramMiddleware,
        tg_webhook_controller: interface.ITelegramWebhookController,
        command_controller: interface.ICommandController,
        message_controller: interface.IMessageController
):
    app = FastAPI()
    include_tg_middleware(dp, tg_middleware)
    include_http_middleware(app, http_middleware)

    include_db_handler(app, db)
    include_tg_webhook(app, tg_webhook_controller)
    include_command_handlers(
        dp,
        command_controller
    )
    include_message_handler(
        dp,
        message_controller
    )

    return app


def include_http_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_tg_middleware(
        dp: Dispatcher,
        tg_middleware: interface.ITelegramMiddleware,
):
    dp.update.middleware(tg_middleware.trace_middleware01)
    dp.update.middleware(tg_middleware.metric_middleware02)
    dp.update.middleware(tg_middleware.logger_middleware03)
    dp.update.middleware(tg_middleware.get_state_middleware04)


def include_tg_webhook(
        app: FastAPI,
        tg_webhook_controller: interface.ITelegramWebhookController,
):
    app.add_api_route(
        common.PREFIX + "/update",
        tg_webhook_controller.bot_webhook,
        methods=["POST"]
    )
    app.add_api_route(
        common.PREFIX + "/webhook/set",
        tg_webhook_controller.bot_set_webhook,
        methods=["POST"]
    )


def include_command_handlers(
        dp: Dispatcher,
        command_controller: interface.ICommandController,
):
    dp.message.register(
        command_controller.start_handler,
        Command("start")
    )


def include_message_handler(
        dp: Dispatcher,
        message_controller: interface.IMessageController
):
    dp.message.register(
        message_controller.message_handler,
    )


def include_db_handler(app: FastAPI, db: interface.IDB):
    app.add_api_route(common.PREFIX + "/table/create", create_table_handler(db), methods=["GET"])
    app.add_api_route(common.PREFIX + "/table/drop", drop_table_handler(db), methods=["GET"])


def create_table_handler(db: interface.IDB):
    async def create_table():
        try:
            await db.multi_query(model.create_queries)
        except Exception as err:
            raise err

    return create_table


def drop_table_handler(db: interface.IDB):
    async def delete_table():
        try:
            await db.multi_query(model.drop_queries)
        except Exception as err:
            raise err

    return delete_table
