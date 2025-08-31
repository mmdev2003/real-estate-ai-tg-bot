create_estate_table = """
CREATE TABLE IF NOT EXISTS estates(
    id SERIAL PRIMARY KEY,
    
    link TEXT NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    address TEXT NOT NULL,
    metro_stations JSONB[] NOT NULL,
    coords JSONB NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_rent_offer_table = """
CREATE TABLE IF NOT EXISTS rent_offers(
    id SERIAL PRIMARY KEY,
    estate_id INTEGER NOT NULL,
    
    link TEXT NOT NULL,
    name TEXT NOT NULL,
    square FLOAT NOT NULL,
    price_per_month INTEGER NOT NULL,
    design INTEGER NOT NULL,
    floor INTEGER NOT NULL,
    type INTEGER NOT NULL,
    location TEXT NOT NULL,
    image_urls TEXT[] NOT NULL,
    offer_readiness INTEGER NOT NULL,
    readiness_date TEXT NOT NULL,
    description TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_sale_offer_table = """
CREATE TABLE IF NOT EXISTS sale_offers(
    id SERIAL PRIMARY KEY,
    estate_id INTEGER NOT NULL,
    
    link TEXT NOT NULL,
    name TEXT NOT NULL,
    square FLOAT NOT NULL,
    price BIGINT NOT NULL,
    price_per_meter BIGINT NOT NULL,
    design INTEGER NOT NULL,
    floor INTEGER NOT NULL,
    type INTEGER NOT NULL,
    location TEXT NOT NULL,
    image_urls TEXT[] NOT NULL,
    irr FLOAT DEFAULT 0,
    offer_readiness INTEGER NOT NULL,
    readiness_date TEXT NOT NULL,
    description TEXT NOT NULL,
    
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
BEFORE UPDATE ON estates
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

drop_estate_table = """
DROP TABLE IF EXISTS estates;
"""

drop_rent_offer_table = """
DROP TABLE IF EXISTS rent_offers;
"""

drop_sale_offer_table = """
DROP TABLE IF EXISTS sale_offers;
"""

create_queries = [
    create_estate_table,
    create_rent_offer_table,
    create_sale_offer_table,
    on_update_table_query1,
    on_update_table_query2
]

drop_queries = [drop_estate_table, drop_rent_offer_table, drop_sale_offer_table]
