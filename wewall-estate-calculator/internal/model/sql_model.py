create_metro_stations_table = """
CREATE TABLE IF NOT EXISTS metro_stations (
    id SERIAL PRIMARY KEY ,
    
    name TEXT NOT NULL,
    price_a INTEGER NOT NULL,
    price_b INTEGER NOT NULL,
    rent_a INTEGER NOT NULL,
    rent_b INTEGER NOT NULL,
    average_cadastral_value INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_metro_distance_coeffs_table = """
CREATE TABLE IF NOT EXISTS metro_distance_coeffs (
    id SERIAL PRIMARY KEY,
    min_distance INTEGER NOT NULL,
    max_distance INTEGER NOT NULL,
    coeff FLOAT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_square_coeffs_table = """
CREATE TABLE IF NOT EXISTS square_coeffs (
    id SERIAL PRIMARY KEY,
    
    min_square INTEGER NOT NULL,
    max_square INTEGER NOT NULL,
    coeff FLOAT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
BEFORE UPDATE ON metro_stations
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

drop_metro_stations_table = """
DROP TABLE IF EXISTS metro_stations
"""

drop_metro_distance_coeffs_table = """
DROP TABLE IF EXISTS metro_distance_coeffs
"""

drop_square_coeffs_table = """
DROP TABLE IF EXISTS square_coeffs
"""

create_queries = [create_metro_stations_table, create_metro_distance_coeffs_table, create_square_coeffs_table,
                  on_update_table_query1, on_update_table_query2]

drop_queries = [drop_metro_stations_table, drop_metro_distance_coeffs_table, drop_square_coeffs_table]