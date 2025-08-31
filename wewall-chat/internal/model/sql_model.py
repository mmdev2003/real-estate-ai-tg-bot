create_amocrm_contact_table = """
CREATE TABLE IF NOT EXISTS amocrm_contacts (
    amocrm_contact_id BIGINT PRIMARY KEY,
    
    name TEXT NOT NULL,
    tg_chat_id BIGINT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_amocrm_lead_table = """
CREATE TABLE IF NOT EXISTS amocrm_leads (
    amocrm_lead_id BIGINT PRIMARY KEY,
    
    amocrm_contact_id BIGINT NOT NULL,
    amocrm_pipeline_id BIGINT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_amocrm_chat_table = """
CREATE TABLE IF NOT EXISTS amocrm_chats (
    amocrm_chat_id TEXT PRIMARY KEY,

    amocrm_lead_id BIGINT NOT NULL,
    amocrm_conversation_id TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_amocrm_message_table = """
CREATE TABLE IF NOT EXISTS amocrm_messages (
    amocrm_message_id TEXT PRIMARY KEY,

    amocrm_chat_id TEXT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

on_update_table_query1 = """
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE "plpgsql";
"""

drop_amocrm_contact_table = """
DROP TABLE IF EXISTS amocrm_contacts;
"""

drop_amocrm_lead_table = """
DROP TABLE IF EXISTS amocrm_leads;
"""

drop_amocrm_chat_table = """
DROP TABLE IF EXISTS amocrm_chats;
"""

drop_amocrm_message_table = """
DROP TABLE IF EXISTS amocrm_messages;
"""

create_queries = [
    create_amocrm_contact_table,
    create_amocrm_lead_table,
    create_amocrm_chat_table,
    create_amocrm_message_table,
    on_update_table_query1,
]

drop_queries = [
    drop_amocrm_contact_table,
    drop_amocrm_lead_table,
    drop_amocrm_chat_table,
    drop_amocrm_message_table,
]