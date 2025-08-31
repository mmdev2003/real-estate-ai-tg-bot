import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from aiogram import Dispatcher
from aiogram.filters import Command

from internal import model, interface, common


def NewTg(
        db: interface.IDB,
        dp: Dispatcher,
        worker: interface.IStatisticWorker,
        http_middleware: interface.IHttpMiddleware,
        tg_middleware: interface.ITelegramMiddleware,
        tg_webhook_controller: interface.ITelegramWebhookController,
        estate_search_callback_controller: interface.IEstateSearchCallbackController,
        wewall_expert_callback_controller: interface.IWewallExpertCallbackController,
        command_controller: interface.ICommandController,
        message_controller: interface.IMessageController
):
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        daily_worker_task = asyncio.create_task(worker.collect_daily_stats())
        monthly_worker_task = asyncio.create_task(worker.collect_monthly_stats())
        try:
            yield
        finally:
            daily_worker_task.cancel()
            monthly_worker_task.cancel()
            try:
                await daily_worker_task
            except asyncio.CancelledError:
                print("Daily statistics worker cancelled", flush=True)

            try:
                await monthly_worker_task
            except asyncio.CancelledError:
                print("Monthly statistics worker cancelled", flush=True)
    app = FastAPI(lifespan=lifespan)
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
    include_callback_handler(
        dp,
        wewall_expert_callback_controller,
        estate_search_callback_controller,
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
    dp.update.middleware(tg_middleware.check_subscribe_middleware04)
    dp.update.middleware(tg_middleware.get_state_middleware05)
    dp.update.middleware(tg_middleware.count_message_middleware06)
    dp.update.middleware(tg_middleware.send_contact_message_to_amocrm_middleware07)


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
        common.PREFIX + "/post-short-link/create",
        tg_webhook_controller.create_post_short_link,
        methods=["POST"]
    )
    app.add_api_route(
        common.PREFIX + "/message/send",
        tg_webhook_controller.send_message_to_user,
        methods=["POST"]
    )
    app.add_api_route(
        common.PREFIX + "/state/delete",
        tg_webhook_controller.delete_state,
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

    dp.message.register(
        command_controller.estate_search_handler,
        Command("estate_search")
    )

    dp.message.register(
        command_controller.finance_model_handler,
        Command("finance_model")
    )

    dp.message.register(
        command_controller.news_handler,
        Command("news")
    )

    dp.message.register(
        command_controller.manager_handler,
        Command("manager")
    )


def include_message_handler(
        dp: Dispatcher,
        message_controller: interface.IMessageController
):
    dp.message.register(
        message_controller.message_handler,
    )


def include_callback_handler(
        dp: Dispatcher,
        wewall_expert_callback_controller: interface.IWewallExpertCallbackController,
        estate_search_callback_controller: interface.IEstateSearchCallbackController
):
    dp.callback_query.register(
        wewall_expert_callback_controller.wewall_expert_callback,
        lambda callback: callback.data.startswith("wewall_expert:")
    )

    dp.callback_query.register(
        estate_search_callback_controller.estate_search_callback,
        lambda callback: callback.data.startswith("estate_search:")
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
