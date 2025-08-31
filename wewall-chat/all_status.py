import asyncio
from internal.config.config import Config
from infrastructure.telemetry.telemetry import Telemetry
from pkg.client.external.amocrm.client import AmocrmClient

cfg = Config()

tel = Telemetry(
    cfg.log_level,
    cfg.root_path,
    cfg.environment,
    cfg.service_name,
    cfg.service_version,
    cfg.otlp_host,
    cfg.otlp_port,
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

if __name__ == "__main__":
    main_pipeline_id = 9839286
    appeal_pipeline_id = 9839298

    asyncio.run(amocrm.all_status_by_pipeline_id(main_pipeline_id))
    asyncio.run(amocrm.all_status_by_pipeline_id(appeal_pipeline_id))