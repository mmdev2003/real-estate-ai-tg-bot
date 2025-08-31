import uvicorn
import asyncio
import argparse

from infrastructure.pg.pg import PG
from pkg.client.external.openai.client import GPTClient
from pkg.tg_news_parser.tg_news_parser import TgNewsParser

from infrastructure.telemetry.telemetry import Telemetry, AlertManager

from internal.controller.http.middlerware.middleware import HttpMiddleware

from internal.controller.http.handler.chat.handler import ChatController

from internal.service.chat.service import ChatService
from internal.service.news.service import NewsService
from internal.service.prompt.service import PromptService
from internal.service.analysis.service import AnalysisService

from internal.repo.news.repo import NewsRepo
from internal.repo.wewall.repo import WewallRepo
from internal.repo.chat.repo import ChatRepository
from internal.repo.analysis.repo import AnalysisRepo

from internal.app.parsing.tg_news.app import TgNewsParsing
from internal.app.parsing.pdf_analysis.app import PdfAnalysisParsing
from internal.app.http.app import NewHTTP

from internal.config.config import Config

parser = argparse.ArgumentParser(description='For choice app')
parser.add_argument(
    'app',
    type=str,
    help='Option: "http, estate_pdf_analyze"'
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

gpt_client = GPTClient(tel, cfg.openai_api_key)
tg_news_parser = TgNewsParser(tel, cfg.tg_phone_number, cfg.tg_api_id, cfg.tg_api_hash)

news_repo = NewsRepo(tel, db)
analysis_repo = AnalysisRepo(tel, db)
wewall_repo = WewallRepo(tel, db)
chat_repository = ChatRepository(tel, db)

prompt_service = PromptService(
    tel,
    news_repo,
    analysis_repo,
    wewall_repo
)

chat_service = ChatService(tel, chat_repository, gpt_client, prompt_service)
news_service = NewsService(tel, news_repo)
analysis_service = AnalysisService(tel, analysis_repo, gpt_client)

chat_controller = ChatController(tel, chat_service)
http_middleware = HttpMiddleware(tel, cfg.prefix)

if __name__ == '__main__':
    args = parser.parse_args()
    http_port = int(Config.http_port)

    if args.app == "http":
        app = NewHTTP(
            db,
            chat_controller,
            http_middleware,
            cfg.prefix
        )
        uvicorn.run(app, host="0.0.0.0", port=cfg.http_port, access_log=False)

    if args.app == "tg_news_parsing":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            TgNewsParsing(
                news_service,
                tg_news_parser,
                cfg.tg_news_channels
            )
        )
    if args.app == "pdf_analysis":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            PdfAnalysisParsing(
                analysis_service,
            )
        )
