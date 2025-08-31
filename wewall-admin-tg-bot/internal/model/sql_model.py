create_state_table = """
CREATE TABLE IF NOT EXISTS states (
    id SERIAL PRIMARY KEY,
    tg_chat_id BIGINT DEFAULT NULL,
    
    status TEXT DEFAULT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

create_post_short_link_table = """
CREATE TABLE IF NOT EXISTS post_short_links (
    id SERIAL PRIMARY KEY,
    tg_chat_id BIGINT,

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

drop_state_table = """
DROP TABLE IF EXISTS states;
"""

drop_post_short_link_table = """
DROP TABLE IF EXISTS post_short_links;
"""

create_queries = [create_state_table, create_post_short_link_table, on_update_table_query1, on_update_table_query2]
drop_queries = [drop_state_table, drop_post_short_link_table]
