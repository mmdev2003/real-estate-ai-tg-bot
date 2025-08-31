import os

class Config:
    db_pass: str = os.environ.get('WEWALL_ESTATE_EXPERT_POSTGRES_PASSWORD')
    db_user: str = os.environ.get('WEWALL_ESTATE_EXPERT_POSTGRES_USER')
    db_name: str = os.environ.get('WEWALL_ESTATE_EXPERT_POSTGRES_DB_NAME')
    db_host: str = os.environ.get('WEWALL_ESTATE_EXPERT_POSTGRES_CONTAINER_NAME')
    db_port: str = "5432"

    http_port: int = int(os.environ.get('WEWALL_ESTATE_EXPERT_PORT'))
    prefix = os.environ.get('WEWALL_ESTATE_EXPERT_PREFIX')
    service_name = "wewall-estate-expert"

    root_path = "/app"
    service_version = "0.0.1"
    otlp_host: str = os.environ.get("WEWALL_OTEL_COLLECTOR_CONTAINER_NAME")
    otlp_port: int = os.environ.get("WEWALL_OTEL_COLLECTOR_GRPC_PORT")

    wewall_estate_calculator_host: str = os.environ.get('WEWALL_ESTATE_CALCULATOR_CONTAINER_NAME')
    wewall_estate_calculator_port: int = int(os.environ.get('WEWALL_ESTATE_CALCULATOR_PORT'))

    openai_api_key: str = os.environ.get('WEWALL_OPEN_AI_API_KEY')

    tg_phone_number: str = os.environ.get('TG_NEWS_PHONE_NUMBER')
    tg_api_id: int = os.environ.get('TG_NEWS_API_ID')
    tg_api_hash: str = os.environ.get('TG_NEWS_API_HASH')
    tg_news_channels: list[str] = os.environ.get('TG_NEWS_CHANNELS')

    environment = os.environ.get('ENVIRONMENT')
    log_level = os.environ.get('LOG_LEVEL')

    alert_tg_bot_token: str = os.environ.get('WEWALL_ALERT_TG_BOT_TOKEN')
    alert_tg_chat_id: int = int(os.environ.get('WEWALL_ALERT_TG_CHAT_ID'))
    alert_tg_chat_thread_id: int = int(os.environ.get('WEWALL_ALERT_TG_CHAT_THREAD_ID'))
    grafana_url: str = os.environ.get('WEWALL_GRAFANA_URL')

    monitoring_redis_host: str = os.environ.get('WEWALL_MONITORING_REDIS_CONTAINER_NAME')
    monitoring_redis_port: int = int(os.environ.get('WEWALL_MONITORING_REDIS_PORT'))
    monitoring_redis_db: int = int(os.environ.get('WEWALL_MONITORING_DEDUPLICATE_ERROR_ALERT_REDIS_DB'))
    monitoring_redis_password: str = os.environ.get('WEWALL_MONITORING_REDIS_PASSWORD')