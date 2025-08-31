create_metro_station = """
INSERT INTO metro_stations (name, price_A, price_B, rent_A, rent_B, average_cadastral_value)
VALUES (:name, :price_A, :price_B, :rent_A, :rent_B, :average_cadastral_value)
RETURNING id
"""

create_metro_distance_coeff = """
INSERT INTO metro_distance_coeffs (min_distance, max_distance, coeff)
VALUES (:min_distance, :max_distance, :coeff)
RETURNING id
"""

create_square_coeff = """
INSERT INTO square_coeffs (min_square, max_square, coeff)
VALUES (:min_square, :max_square, :coeff)
RETURNING id
"""

metro_station_by_name = """
SELECT * FROM metro_stations 
WHERE name = :name
"""

all_metro_distance_coeff = """
SELECT * FROM metro_distance_coeffs
"""

all_square_coeff = """
SELECT * FROM square_coeffs
"""