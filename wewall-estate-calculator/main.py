import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.estate_calculator.handler import EstateCalculatorController

from pkg.estate_calculator.estate_calculator import EstateCalculator

from internal.repo.metro.repo import MetroRepo

from internal.config.config import Config

from internal.app.http.app import NewHttp

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

metro_repo = MetroRepo(db)

estate_calculator = EstateCalculator(tel, metro_repo, cfg.income_tax_share)
estate_calculator_controller = EstateCalculatorController(tel, estate_calculator)

http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == '__main__':
    app = NewHttp(
        db,
        estate_calculator_controller,
        http_middleware,
        cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=cfg.http_port, access_log=False)
