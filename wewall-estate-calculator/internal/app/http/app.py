from fastapi import FastAPI


from internal import model, interface

PREFIX = "/api/estate-calculator"


def NewHttp(
        db: interface.IDB,
        estate_calculator_controller: interface.IEstateCalculatorController,
        http_middleware: interface.IHttpMiddleware,
        prefix: str
):
    app = FastAPI()

    include_middleware(app, http_middleware)
    include_db_handler(app, db, prefix)
    include_estate_calculator_handlers(app, estate_calculator_controller, prefix)

    return app


def include_middleware(
        app: FastAPI,
        http_middleware: interface.IHttpMiddleware
):
    http_middleware.logger_middleware03(app)
    http_middleware.metrics_middleware02(app)
    http_middleware.trace_middleware01(app)


def include_estate_calculator_handlers(
        app: FastAPI,
        estate_calculator_controller: interface.IEstateCalculatorController,
        prefix: str
):
    app.add_api_route(
        prefix + "/finished/office",
        estate_calculator_controller.calc_finance_model_finished_office,
        methods=["POST"],
        tags=["Estate finance model calculator"],
    )

    app.add_api_route(
        prefix + "/finished/retail",
        estate_calculator_controller.calc_finance_model_finished_retail,
        methods=["POST"],
        tags=["Estate finance model calculator"]
    )

    app.add_api_route(
        prefix + "/building/office",
        estate_calculator_controller.calc_finance_model_building_office,
        methods=["POST"],
        tags=["Estate finance model calculator"]
    )

    app.add_api_route(
        prefix + "/building/retail",
        estate_calculator_controller.calc_finance_model_building_retail,
        methods=["POST"],
        tags=["Estate finance model calculator"]
    )

    app.add_api_route(
        prefix + "/finished/office/table",
        estate_calculator_controller.calc_finance_model_finished_office_table,
        methods=["POST"],
        tags=["Estate finance model calculator"]
    )

    app.add_api_route(
        prefix + "/finished/retail/table",
        estate_calculator_controller.calc_finance_model_finished_retail_table,
        methods=["POST"],
        tags=["Estate finance model calculator"]
    )

    app.add_api_route(
        prefix + "/building/office/table",
        estate_calculator_controller.calc_finance_model_building_office_table,
        methods=["POST"],
        tags=["Estate finance model calculator"]
    )

    app.add_api_route(
        prefix + "/building/retail/table",
        estate_calculator_controller.calc_finance_model_building_retail_table,
        methods=["POST"],
        tags=["Estate finance model calculator"]
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