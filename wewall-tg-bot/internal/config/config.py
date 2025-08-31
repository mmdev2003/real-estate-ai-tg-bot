import os

class Config:
    db_pass: str = os.environ.get('WEWALL_TG_BOT_POSTGRES_PASSWORD')
    db_user: str = os.environ.get('WEWALL_TG_BOT_POSTGRES_USER')
    db_name: str = os.environ.get('WEWALL_TG_BOT_POSTGRES_DB_NAME')
    db_host: str = os.environ.get('WEWALL_TG_BOT_POSTGRES_CONTAINER_NAME')
    db_port: str = "5432"

    domain: str = os.environ.get("WEWALL_DOMAIN")
    http_port: int = int(os.environ.get("WEWALL_TG_BOT_PORT"))
    service_name = "wewall-tg-bot"
    root_path = "/app"
    service_version = "0.0.1"
    prefix = os.environ.get("WEWALL_TG_BOT_PREFIX")

    weed_master_host: str = os.environ.get("WEWALL_WEED_MASTER_CONTAINER_NAME")
    weed_master_port: str = os.environ.get("WEWALL_WEED_MASTER_PORT")

    wewall_chat_host: str = os.environ.get("WEWALL_CHAT_CONTAINER_NAME")
    wewall_chat_port: int = int(os.environ.get("WEWALL_CHAT_PORT"))

    wewall_estate_calculator_host: str = os.environ.get("WEWALL_ESTATE_CALCULATOR_CONTAINER_NAME")
    wewall_estate_calculator_port: int = int(os.environ.get("WEWALL_ESTATE_CALCULATOR_PORT"))

    wewall_estate_expert_host: str = os.environ.get("WEWALL_ESTATE_EXPERT_CONTAINER_NAME")
    wewall_estate_expert_port: int = int(os.environ.get("WEWALL_ESTATE_EXPERT_PORT"))

    wewall_estate_search_host: str = os.environ.get("WEWALL_ESTATE_SEARCH_CONTAINER_NAME")
    wewall_estate_search_port: int = int(os.environ.get("WEWALL_ESTATE_SEARCH_PORT"))

    wewall_tg_channel_login: str = os.environ.get("WEWALL_TG_CHANNEL_LOGIN")

    amocrm_main_pipeline_id: int = int(os.environ.get("AMOCRM_MAIN_PIPELINE_ID"))
    amocrm_appeal_pipeline_id: int = int(os.environ.get("AMOCRM_APPEAL_PIPELINE_ID"))

    amocrm_pipeline_status_chat_with_bot: int = int(os.environ.get("AMOCRM_PIPELINE_STATUS_CHAT_WITH_BOT"))
    amocrm_pipeline_status_high_engagement: int = int(os.environ.get("AMOCRM_PIPELINE_STATUS_HIGH_ENGAGEMENT"))
    amocrm_pipeline_status_active_user: int = int(os.environ.get("AMOCRM_PIPELINE_STATUS_ACTIVE_USER"))
    amocrm_pipeline_status_chat_with_manager: int = int(os.environ.get("AMOCRM_PIPELINE_STATUS_CHAT_WITH_MANAGER"))

    tg_token: str = os.environ.get("WEWALL_TG_BOT_TOKEN")
    openai_api_key: str = os.environ.get("OPENAI_API_KEY")

    otlp_host: str = os.environ.get("WEWALL_OTEL_COLLECTOR_CONTAINER_NAME")
    otlp_port: int = int(os.environ.get("WEWALL_OTEL_COLLECTOR_GRPC_PORT"))

    environment = os.environ.get('ENVIRONMENT')
    log_level = os.environ.get('LOG_LEVEL')

    alert_tg_bot_token: str = os.environ.get('WEWALL_ALERT_TG_BOT_TOKEN')
    alert_tg_chat_id: int = int(os.environ.get('WEWALL_ALERT_TG_CHAT_ID'))
    alert_tg_chat_thread_id: int = int(os.environ.get('WEWALL_ALERT_TG_CHAT_THREAD_ID'))

    statistic_tg_chat_ids: list[int] = [int(os.environ.get('WEWALL_STATISTIC_TG_CHAT_ID')), int(os.environ.get('STIT_STATISTIC_TG_CHAT_ID'))]
    statistic_tg_chat_thread_ids: list[int] = [int(os.environ.get('WEWALL_STATISTIC_TG_CHAT_THREAD_ID')), int(os.environ.get('STIT_STATISTIC_TG_CHAT_THREAD_ID'))]

    grafana_url: str = os.environ.get('WEWALL_GRAFANA_URL')

    monitoring_redis_host: str = os.environ.get('WEWALL_MONITORING_REDIS_CONTAINER_NAME')
    monitoring_redis_port: int = int(os.environ.get('WEWALL_MONITORING_REDIS_PORT'))
    monitoring_redis_db: int = int(os.environ.get('WEWALL_MONITORING_DEDUPLICATE_ERROR_ALERT_REDIS_DB'))
    monitoring_redis_password: str = os.environ.get('WEWALL_MONITORING_REDIS_PASSWORD')
