import asyncio
import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager

from pkg.parser.m2data_parser import M2DataParser
from pkg.parser.trend_agent_parser import TrendAgentParser
from pkg.client.internal.wewall_estate_calculator.client import WewallEstateCalculatorClient

from internal.controller.http.handler.sale_offer.handler import SaleOfferController
from internal.controller.http.handler.rent_offer.handler import RentOfferController
from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.config.config import Config

from internal.repo.estate.repo import EstateRepo
from internal.repo.sale_offer.repo import SaleOfferRepo
from internal.repo.rent_offer.repo import RentOfferRepo

from internal.service.estate.service import EstateService
from internal.service.sale_offer.service import SaleOfferService
from internal.service.rent_offer.service import RentOfferService

from internal.app.http.app import NewHTTP
from internal.app.parsing.app import M2DataParsing
from internal.app.parsing.app import TrendAgentParsing
from internal.app.calc_sale_offer_irr.app import CalcSaleOfferIRR

import argparse

parser = argparse.ArgumentParser(description='For choice app')
parser.add_argument(
    'app',
    type=str,
    help='Option: "http, parsing"'
)
cfg = Config()
alert_manager = AlertManager(
    cfg.alert_tg_bot_token,
    cfg.service_name,
    cfg.alert_tg_chat_id,
    cfg.alert_tg_chat_thread_id,
    cfg.grafana_url,
    cfg.monitoring_redis_host,
    cfg.monitoring_redis_port,
    cfg.monitoring_redis_db,
    cfg.monitoring_redis_password
)

tel = Telemetry(
    cfg.log_level,
    cfg.root_path,
    cfg.environment,
    cfg.service_name,
    cfg.service_version,
    cfg.otlp_host,
    cfg.otlp_port,
    alert_manager
)

db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)

m2data_parser = M2DataParser(cfg.m2data_building_url)
trend_agent_parser = TrendAgentParser()
estate_calculator_client = WewallEstateCalculatorClient(tel, cfg.wewall_estate_calculator_host,
                                                        cfg.wewall_estate_calculator_port)

estate_repo = EstateRepo(tel, db)
rent_offer_repo = RentOfferRepo(tel, db)
sale_offer_repo = SaleOfferRepo(tel, db)

estate_service = EstateService(tel, estate_repo)
rent_offer_service = RentOfferService(tel, estate_repo, rent_offer_repo)
sale_offer_service = SaleOfferService(tel, estate_repo, sale_offer_repo, estate_calculator_client)

rent_offer_controller = RentOfferController(tel, rent_offer_service)
sale_offer_controller = SaleOfferController(tel, sale_offer_service)

http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == '__main__':
    args = parser.parse_args()

    if args.app == "http":
        app = NewHTTP(
            db,
            rent_offer_controller,
            sale_offer_controller,
            http_middleware,
            cfg.prefix
        )
        uvicorn.run(app, host='0.0.0.0', port=cfg.http_port, loop='asyncio', access_log=False)

    if args.app == "parsing_m2data":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            M2DataParsing(
                db,
                estate_service,
                rent_offer_service,
                sale_offer_service,
                m2data_parser
            )
        )
    if args.app == "parsing_trend_agent":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            TrendAgentParsing(
                estate_service,
                sale_offer_service,
                trend_agent_parser
            )
        )
    if args.app == "calc_sale_offer_irr":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            CalcSaleOfferIRR(
                sale_offer_repo,
                sale_offer_service,
            )
        )
