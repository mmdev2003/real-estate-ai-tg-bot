from fastapi import FastAPI

from internal import model, interface


def NewHTTP(
        db: interface.IDB,
        rent_offer_controller: interface.IRentOfferController,
        sale_offer_controller: interface.ISaleOfferController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI()
    include_middleware(app, http_middleware)
    include_db_handler(app, db, prefix)

    include_sale_offer_handlers(app, sale_offer_controller, prefix)
    include_rent_offer_handlers(app, rent_offer_controller, prefix)

    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_rent_offer_handlers(
        app: FastAPI,
        rent_offer_controller: interface.IRentOfferController,
        prefix: str
):
    app.add_api_route(
        prefix + "/rent",
        rent_offer_controller.estate_search_rent,
        methods=["POST"],
        tags=["Estate search rent knn"],
    )


def include_sale_offer_handlers(
        app: FastAPI,
        sale_offer_controller: interface.ISaleOfferController,
        prefix: str
):
    app.add_api_route(
        prefix + "/sale",
        sale_offer_controller.estate_search_sale,
        methods=["POST"],
        tags=["Estate search sale knn"],
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
