create_state_table = """
CREATE TABLE IF NOT EXISTS states (
    id SERIAL PRIMARY KEY,
    tg_chat_id BIGINT DEFAULT NULL,
    
    status TEXT DEFAULT NULL,
    is_transferred_to_manager BOOLEAN DEFAULT FALSE,
    
    count_estate_search INTEGER DEFAULT 0,
    count_estate_calculator INTEGER DEFAULT 0,
    count_message INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_user_table = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_chat_id BIGINT NOT NULL,
    
    source_type TEXT NOT NULL,
    is_bot_blocked BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_post_short_link_table = """
CREATE TABLE IF NOT EXISTS post_short_links (
    id SERIAL PRIMARY KEY,

    name TEXT DEFAULT NULL,
    description TEXT DEFAULT NULL,
    
    image_name TEXT DEFAULT '',
    image_fid TEXT DEFAULT '',
    
    file_name TEXT DEFAULT '',
    file_fid TEXT DEFAULT '',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_estate_search_state_table = """
CREATE TABLE IF NOT EXISTS estate_search_states (
    id SERIAL PRIMARY KEY,
    state_id INTEGER NOT NULL,
    
    current_estate_id INTEGER DEFAULT 0,
    current_offer_id INTEGER DEFAULT 0,
    
    offers JSONB[] NOT NULL,
    estate_search_params jsonb NOT NULL,
    
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
$$ LANGUAGE 'plpgsql';
"""

on_update_table_query2 = """
CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON states
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

on_update_table_query3 = """
CREATE TRIGGER update_шыукы_at_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

drop_state_table = """
DROP TABLE IF EXISTS states;
"""

drop_state_table = """
DROP TABLE IF EXISTS users;
"""

drop_estate_search_state_table = """
DROP TABLE IF EXISTS estate_search_states;
"""


create_queries = [create_state_table, create_user_table, create_post_short_link_table, create_estate_search_state_table, on_update_table_query1,
                  on_update_table_query2, on_update_table_query3]
drop_queries = [drop_state_table, drop_state_table, drop_estate_search_state_table]
