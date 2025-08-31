import uvicorn

from aiogram import Bot, Dispatcher

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager
from infrastructure.weedfs.weedfs import Weed

from pkg.client.internal.wewall_tg_bot.client import WewallTgBotClient

from internal.repo.post_short_link.repo import PostShortLinkRepo
from internal.repo.state.repo import StateRepo

from internal.service.post_short_link.service import PostShortLinkService
from internal.service.state.service import StateService

from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.controller.http.webhook.handler import TelegramWebhookController

from internal.controller.tg.middleware.middleware import TgMiddleware
from internal.controller.tg.message.handler import MessageController
from internal.controller.tg.command.handler import CommandController

from internal.app.tg.app import NewTg

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

db = PG(tel, cfg.db_user, cfg.db_pass, cfg.db_host, cfg.db_port, cfg.db_name)

storage = Weed(cfg.weed_master_host, cfg.weed_master_port)

bot = Bot(cfg.tg_bot_token)
dp = Dispatcher()

wewall_tg_bot_client = WewallTgBotClient(tel, cfg.wewall_tg_bot_host, cfg.wewall_tg_bot_port)

post_short_link_repo = PostShortLinkRepo(tel, db)

state_repo = StateRepo(tel, db)
state_service = StateService(tel, state_repo)

post_short_link_service = PostShortLinkService(tel, storage, state_service, post_short_link_repo, wewall_tg_bot_client,
                                               cfg.bot_link)

tg_middleware = TgMiddleware(
    tel,
    state_service,
    bot,
)
http_middleware = HttpMiddleware(
    tel,
    cfg.prefix,
)
tg_webhook_controller = TelegramWebhookController(
    tel,
    dp,
    bot,
    cfg.domain,
    cfg.prefix,
)

message_controller = MessageController(bot, tel, post_short_link_service, state_service, storage)
command_controller = CommandController(tel, dp, bot, state_service, post_short_link_service)

if __name__ == '__main__':
    tg_app = NewTg(
        db,
        dp,
        http_middleware,
        tg_middleware,
        tg_webhook_controller,
        command_controller,
        message_controller,
    )
    uvicorn.run(tg_app, host='0.0.0.0', port=cfg.http_port, loop='asyncio', access_log=False)
