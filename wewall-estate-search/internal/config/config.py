import os

class Config:
    db_pass: str = os.environ.get('WEWALL_ESTATE_SEARCH_POSTGRES_PASSWORD')
    db_user: str = os.environ.get('WEWALL_ESTATE_SEARCH_POSTGRES_USER')
    db_name: str = os.environ.get('WEWALL_ESTATE_SEARCH_POSTGRES_DB_NAME')
    db_host: str = os.environ.get('WEWALL_ESTATE_SEARCH_POSTGRES_CONTAINER_NAME')
    db_port: str = "5432"

    http_port: int = int(os.environ.get('WEWALL_ESTATE_SEARCH_PORT'))
    prefix = os.environ.get('WEWALL_ESTATE_SEARCH_PREFIX')
    service_name = "wewall-estate-search"

    root_path = "/app"
    service_version = "0.0.1"
    otlp_host: str = os.environ.get("WEWALL_OTEL_COLLECTOR_CONTAINER_NAME")
    otlp_port: int = os.environ.get("WEWALL_OTEL_COLLECTOR_GRPC_PORT")


    wewall_estate_calculator_host: str = os.environ.get('WEWALL_ESTATE_CALCULATOR_CONTAINER_NAME')
    wewall_estate_calculator_port: int = int(os.environ.get('WEWALL_ESTATE_CALCULATOR_PORT'))

    m2data_building_url: str = os.environ.get('M2DATA_BUILDING_URL')

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