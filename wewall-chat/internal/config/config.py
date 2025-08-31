import os

class Config:
    db_pass: str = os.environ.get("WEWALL_CHAT_POSTGRES_PASSWORD")
    db_user: str = os.environ.get("WEWALL_CHAT_POSTGRES_USER")
    db_name: str = os.environ.get("WEWALL_CHAT_POSTGRES_DB_NAME")
    db_host: str = os.environ.get("WEWALL_CHAT_POSTGRES_CONTAINER_NAME")
    db_port: str = "5432"

    http_port: int = int(os.environ.get("WEWALL_CHAT_PORT"))
    root_path = "/app"
    service_version = "0.0.1"
    prefix = os.environ.get("WEWALL_CHAT_PREFIX")
    service_name = "wewall-chat"

    otlp_host: str = os.environ.get("WEWALL_OTEL_COLLECTOR_CONTAINER_NAME")
    otlp_port: int = os.environ.get("WEWALL_OTEL_COLLECTOR_GRPC_PORT")

    wewall_tg_host: str = os.environ.get("WEWALL_TG_BOT_CONTAINER_NAME")
    wewall_tg_port: int = int(os.environ.get("WEWALL_TG_BOT_PORT"))

    messenger = "Telegram"
    amocrm_token = os.environ.get("AMOCRM_TOKEN")
    amocrm_subdomain = os.environ.get("AMOCRM_SUBDOMAIN")
    amocrm_api_platform_base_url = os.environ.get("AMOCRM_API_PLATFORM_BASE_URL")
    amocrm_api_chats_url = os.environ.get("AMOCRM_API_CHATS_BASE_URL")
    amocrm_bot_name = os.environ.get("AMOCRM_BOT_NAME")
    amocrm_bot_id: str = os.environ.get("AMOCRM_BOT_ID")
    amocrm_channel_secret: str = os.environ.get("AMOCRM_CHANNEL_SECRET")
    amocrm_channel_id: str = os.environ.get("AMOCRM_CHANNEL_ID")
    amocrm_channel_code: str = os.environ.get("AMOCRM_CHANNEL_CODE")
    amocrm_scope_id: str = os.environ.get("AMOCRM_SCOPE_ID")
    amocrm_contact_custom_fields = {
        "tg_username_field_id": int(os.environ.get("AMOCRM_TG_USERNAME_FIELD_ID"))
    }
    amocrm_lead_custom_fields = {
        "lead_source_field_id": int(os.environ.get("AMOCRM_LEAD_SOURCE_FIELD_ID"))
    }

    environment = os.environ.get("ENVIRONMENT")
    log_level = os.environ.get("LOG_LEVEL")

    alert_tg_bot_token: str = os.environ.get('WEWALL_ALERT_TG_BOT_TOKEN')
    alert_tg_chat_id: int = int(os.environ.get('WEWALL_ALERT_TG_CHAT_ID'))
    alert_tg_chat_thread_id: int = int(os.environ.get('WEWALL_ALERT_TG_CHAT_THREAD_ID'))
    grafana_url: str = os.environ.get('WEWALL_GRAFANA_URL')


    monitoring_redis_host: str = os.environ.get('WEWALL_MONITORING_REDIS_CONTAINER_NAME')
    monitoring_redis_port: int = int(os.environ.get('WEWALL_MONITORING_REDIS_PORT'))
    monitoring_redis_db: int = int(os.environ.get('WEWALL_MONITORING_DEDUPLICATE_ERROR_ALERT_REDIS_DB'))
    monitoring_redis_password: str = os.environ.get('WEWALL_MONITORING_REDIS_PASSWORD')
