create_chat_table = """
CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    tg_chat_id BIGINT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_message_table = """
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    
    role TEXT NOT NULL,
    text TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_analysis_table = """
CREATE TABLE IF NOT EXISTS analysis (
    id SERIAL PRIMARY KEY,
    analysis_name TEXT NOT NULL,
    analysis_summary TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_news_table = """
CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    news_name TEXT NOT NULL,
    news_summary TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

on_update_table_query1 = """
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';
"""

on_update_table_query2 = """
CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON chats
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

drop_chat_table = """
DROP TABLE IF EXISTS chats;
"""

drop_message_table = """
DROP TABLE IF EXISTS messages;
"""

drop_analysis_table = """
DROP TABLE IF EXISTS analysis;
"""

drop_news_table = """
DROP TABLE IF EXISTS news;
"""

create_queries = [
    create_chat_table,
    create_analysis_table,
    create_news_table,
    create_message_table,
    on_update_table_query1,
    on_update_table_query2
]
drop_queries = [drop_chat_table, drop_message_table, drop_analysis_table, drop_news_table]
