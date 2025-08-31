from fastapi import FastAPI

from internal import model, interface

PREFIX = "/api/chat"


def NewHTTP(
        db: interface.IDB,
        amocrm_chat_controller: interface.IAmocrmChatController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI()
    include_middleware(app, http_middleware)

    include_db_handler(app, db, prefix)
    include_chat_handlers(app, amocrm_chat_controller, prefix)
    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)

def include_chat_handlers(
        app: FastAPI,
        amocrm_chat_controller: interface.IAmocrmChatController,
        prefix: str
):
    app.add_api_route(
        prefix + "/connect",
        amocrm_chat_controller.connect_channel_to_account,
        methods=["GET"],
    )

    app.add_api_route(
        prefix + "/lead/edit",
        amocrm_chat_controller.edit_lead,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/amocrm/webhook/subscribe",
        amocrm_chat_controller.subscribe_to_event_webhook,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/contact/delete",
        amocrm_chat_controller.delete_contact,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/lead/delete",
        amocrm_chat_controller.delete_lead,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/create/tg/amocrm",
        amocrm_chat_controller.create_chat_with_amocrm_manager_from_tg,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/message/send/tg/amocrm",
        amocrm_chat_controller.send_message_from_tg_to_amocrm,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/message/import/tg/amocrm",
        amocrm_chat_controller.send_message_from_bot_to_amocrm,
        methods=["POST"],
    )

    app.add_api_route(
        prefix + "/message/send/amocrm/tg/{scope_id}",
        amocrm_chat_controller.send_message_from_amocrm_to_tg,
        methods=["POST"],
    )


def include_db_handler(app: FastAPI, db: interface.IDB, prefix: str):
    app.add_api_route(prefix + "/table/create", create_table_handler(db), methods=["GET"])
    app.add_api_route(prefix + "/table/drop", drop_table_handler(db), methods=["GET"])


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
