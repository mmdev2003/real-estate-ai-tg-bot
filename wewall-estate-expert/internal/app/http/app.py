from fastapi import FastAPI

from internal import interface
from internal import model


def NewHTTP(
        db: interface.IDB,
        chat_controller: interface.IChatController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI()
    include_middleware(app, http_middleware)

    include_db_handler(app, db, prefix)
    include_chat_handlers(app, chat_controller, prefix)

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
        chat_controller: interface.IChatController,
        prefix: str
):
    app.add_api_route(
        prefix + "/message/create",
        chat_controller.add_message_from_llm,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/message/send/tg/wewall-expert",
        chat_controller.send_message_to_wewall_expert_by_tg,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/message/send/tg/estate-expert",
        chat_controller.send_message_to_estate_expert_by_tg,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/message/send/tg/estate-search-expert",
        chat_controller.send_message_to_estate_search_expert_by_tg,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/message/send/tg/estate-calculator-expert",
        chat_controller.send_message_to_estate_calculator_by_tg,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/message/send/tg/contact-collector",
        chat_controller.send_message_to_contact_collector_by_tg,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/tg/summary",
        chat_controller.get_chat_summary,
        methods=["POST"],
    )
    app.add_api_route(
        prefix + "/message/delete/all",
        chat_controller.delete_all_message,
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
