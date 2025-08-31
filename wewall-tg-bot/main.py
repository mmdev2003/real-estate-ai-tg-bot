import asyncio

import uvicorn

from aiogram import Bot, Dispatcher

from infrastructure.pg.pg import PG
from infrastructure.telemetry.telemetry import Telemetry, AlertManager
from infrastructure.weedfs.weedfs import Weed

from pkg.worker.statistic_worker import StatisticWorker
from pkg.client.external.openai.client import GPTClient
from pkg.client.internal.wewall_chat.client import WewallChatClient
from pkg.client.internal.wewall_estate_expert.client import WewallEstateExpertClient
from pkg.client.internal.wewall_estate_search.client import WewallEstateSearchClient
from pkg.client.internal.wewall_estate_calculator.client import WewallEstateCalculatorClient

from internal.controller.tg.middleware.middleware import TgMiddleware
from internal.controller.http.middlerware.middleware import HttpMiddleware
from internal.controller.http.webhook.handler import TelegramWebhookController
from internal.controller.tg.callback.estate_search.handler import EstateSearchCallbackController
from internal.controller.tg.callback.wewall_expert.handler import WewallExpertCallbackController
from internal.controller.tg.command.handler import CommandController
from internal.controller.tg.message.handler import MessageController

from internal.service.user.service import UserService
from internal.service.state.service import StateService
from internal.service.post_short_link.service import PostShortLinkService
from internal.service.estate_expert.message_service import EstateExpertMessageService
from internal.service.estate_search.message_service import EstateSearchMessageService
from internal.service.wewall_expert.message_service import WewallExpertMessageService
from internal.service.amocrm_manager.message_service import AmocrmManagerMessageService
from internal.service.contact_collector.message_service import ContactCollectorMessageService
from internal.service.estate_finance_model.message_service import EstateFinanceModelMessageService

from internal.service.estate_search.callback_service import EstateSearchCallbackService
from internal.service.wewall_expert.callback_service import WewallExpertCallbackService

from internal.repo.user.repo import UserRepo
from internal.repo.state.repo import StateRepo
from internal.repo.estate_search_state.repo import EstateSearchStateRepo
from internal.repo.post_short_link.repo import PostShortLinkRepo

from internal.keyboard.estate_search.inline import EstateSearchInlineKeyboardGenerator
from internal.keyboard.wewall_expert.inline import WewallExpertInlineKeyboardGenerator
from internal.keyboard.post_short_link.inline import PostShortLinkInlineKeyboardGenerator

from internal.app.tg.app import NewTg
from internal.app.spam.app import spam

from internal.config.config import Config
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
storage = Weed(cfg.weed_master_host, cfg.weed_master_port)

bot = Bot(cfg.tg_token)
dp = Dispatcher()

llm_client = GPTClient(cfg.openai_api_key)
chat_client = WewallChatClient(tel, cfg.wewall_chat_host, cfg.wewall_chat_port)
estate_expert_client = WewallEstateExpertClient(tel, cfg.wewall_estate_expert_host, cfg.wewall_estate_expert_port)
estate_search_client = WewallEstateSearchClient(tel, cfg.wewall_estate_search_host, cfg.wewall_estate_search_port)
estate_calculator_client = WewallEstateCalculatorClient(tel, cfg.wewall_estate_calculator_host,
                                                        cfg.wewall_estate_calculator_port)

estate_search_inline_keyboard_generator = EstateSearchInlineKeyboardGenerator()
wewall_expert_inline_keyboard_generator = WewallExpertInlineKeyboardGenerator()
post_short_link_inline_keyboard_generator = PostShortLinkInlineKeyboardGenerator()

state_repo = StateRepo(tel, db)
user_repo = UserRepo(tel, db)
post_short_link_repo = PostShortLinkRepo(tel, db)
estate_search_state = EstateSearchStateRepo(tel, db)

state_service = StateService(tel, state_repo)
user_service = UserService(tel, user_repo)
post_short_link_service = PostShortLinkService(
    tel,
    post_short_link_repo,
    storage,
    post_short_link_inline_keyboard_generator
)
amocrm_manager_message_service = AmocrmManagerMessageService(
    tel,
    state_repo,
    chat_client,
    estate_expert_client,
    wewall_expert_inline_keyboard_generator
)
estate_expert_message_service = EstateExpertMessageService(
    tel,
    state_repo,
    estate_expert_client,
    chat_client,
    wewall_expert_inline_keyboard_generator,
    cfg.amocrm_appeal_pipeline_id,
    cfg.amocrm_pipeline_status_chat_with_manager,
)
estate_search_message_service = EstateSearchMessageService(
    tel,
    state_repo,
    estate_search_state,
    chat_client,
    estate_expert_client,
    estate_search_client,
    estate_calculator_client,
    estate_search_inline_keyboard_generator,
    wewall_expert_inline_keyboard_generator,
    llm_client,
    cfg.amocrm_main_pipeline_id,
    cfg.amocrm_appeal_pipeline_id,
    cfg.amocrm_pipeline_status_chat_with_manager,
    cfg.amocrm_pipeline_status_high_engagement,
    cfg.amocrm_pipeline_status_active_user
)
wewall_expert_message_service = WewallExpertMessageService(
    tel,
    state_repo,
    estate_expert_client,
    chat_client,
    wewall_expert_inline_keyboard_generator,
    cfg.amocrm_main_pipeline_id,
    cfg.amocrm_appeal_pipeline_id,
    cfg.amocrm_pipeline_status_chat_with_manager,
)
contact_collector_message_service = ContactCollectorMessageService(
    tel,
    state_repo,
    estate_expert_client,
    chat_client,
    wewall_expert_inline_keyboard_generator,
    cfg.amocrm_appeal_pipeline_id,
    cfg.amocrm_pipeline_status_chat_with_manager,
)
estate_finance_model_message_service = EstateFinanceModelMessageService(
    tel,
    state_repo,
    estate_expert_client,
    estate_calculator_client,
    chat_client,
    wewall_expert_inline_keyboard_generator,
    cfg.amocrm_main_pipeline_id,
    cfg.amocrm_appeal_pipeline_id,
    cfg.amocrm_pipeline_status_chat_with_manager,
    cfg.amocrm_pipeline_status_high_engagement,
    cfg.amocrm_pipeline_status_active_user
)

estate_search_callback_service = EstateSearchCallbackService(
    tel,
    state_repo,
    estate_search_state,
    estate_expert_client,
    estate_calculator_client,
    estate_search_inline_keyboard_generator,
    chat_client,
    llm_client
)
wewall_expert_callback_service = WewallExpertCallbackService(
    tel,
    state_repo,
    estate_expert_client,
    chat_client,
    wewall_expert_inline_keyboard_generator,
    cfg.amocrm_appeal_pipeline_id,
    cfg.amocrm_pipeline_status_chat_with_manager,
)
tg_middleware = TgMiddleware(
    tel,
    bot,
    state_service,
    estate_expert_client,
    chat_client,
    wewall_expert_inline_keyboard_generator,
    cfg.wewall_tg_channel_login,
    cfg.amocrm_main_pipeline_id,
    cfg.amocrm_pipeline_status_high_engagement,
    cfg.amocrm_pipeline_status_active_user,
)
http_middleware = HttpMiddleware(
    tel,
    cfg.prefix,
)
tg_webhook_controller = TelegramWebhookController(
    tel,
    dp,
    bot,
    state_service,
    post_short_link_service,
    cfg.domain,
    cfg.prefix,
)

wewall_expert_callback_controller = WewallExpertCallbackController(
    tel,
    dp,
    wewall_expert_callback_service,
)

estate_search_callback_controller = EstateSearchCallbackController(
    tel,
    dp,
    estate_search_callback_service,
)

command_controller = CommandController(
    tel,
    dp,
    bot,
    state_service,
    user_service,
    post_short_link_service,
    estate_expert_client,
    wewall_expert_message_service,
    estate_search_message_service,
    estate_finance_model_message_service,
    estate_expert_message_service,
    chat_client,
    amocrm_manager_message_service,
    cfg.amocrm_appeal_pipeline_id,
    cfg.amocrm_pipeline_status_chat_with_manager,
)

message_controller = MessageController(
    tel,
    amocrm_manager_message_service,
    wewall_expert_message_service,
    estate_expert_message_service,
    estate_search_message_service,
    estate_finance_model_message_service,
    contact_collector_message_service,
)

worker = StatisticWorker(
    tel,
    user_service,
    cfg.statistic_tg_chat_ids,
    cfg.statistic_tg_chat_thread_ids,
    cfg.alert_tg_bot_token
)

if __name__ == '__main__':
    args = parser.parse_args()

    if args.app == 'http':
        tg_app = NewTg(
            db,
            dp,
            worker,
            http_middleware,
            tg_middleware,
            tg_webhook_controller,
            estate_search_callback_controller,
            wewall_expert_callback_controller,
            command_controller,
            message_controller
        )
        uvicorn.run(tg_app, host='0.0.0.0', port=cfg.http_port, loop='asyncio', access_log=False)

    if args.app == 'newsletter':
        asyncio.run(spam(
            bot,
            user_service,
            post_short_link_inline_keyboard_generator,
            chat_client
        ))



