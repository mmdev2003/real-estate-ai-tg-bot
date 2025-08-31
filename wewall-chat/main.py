import uvicorn

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager

from pkg.client.internal.wewall_tg_bot.client import WewallTgBotClient
from pkg.client.external.amocrm.client import AmocrmClient

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.amocrm.handler import AmocrmChatController

from internal.service.amocrm.service import AmocrmChatService
from internal.repo.amocrm.repo import AmocrmChatRepo

from internal.app.http.app import NewHTTP

from internal.config.config import Config

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

amocrm = AmocrmClient(
    tel,
    cfg.messenger,
    cfg.amocrm_token,
    cfg.amocrm_subdomain,
    cfg.amocrm_api_platform_base_url,
    cfg.amocrm_api_chats_url,
    cfg.amocrm_bot_name,
    cfg.amocrm_bot_id,
    cfg.amocrm_channel_secret,
    cfg.amocrm_channel_id,
    cfg.amocrm_channel_code,
    cfg.amocrm_scope_id,
    cfg.amocrm_contact_custom_fields,
    cfg.amocrm_lead_custom_fields,
)

db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)
wewall_tg_bot_client = WewallTgBotClient(tel, cfg.wewall_tg_host, cfg.wewall_tg_port)

amocrm_chat_repo = AmocrmChatRepo(tel, db)
amocrm_chat_service = AmocrmChatService(tel, amocrm, amocrm_chat_repo, wewall_tg_bot_client)

amocrm_chat_controller = AmocrmChatController(tel, amocrm_chat_service)

http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == "__main__":
    app = NewHTTP(
        db,
        amocrm_chat_controller,
        http_middleware,
        cfg.prefix,
    )
    uvicorn.run(app, host="0.0.0.0", port=int(cfg.http_port), access_log=False)
