create_estate = """
INSERT INTO estates (link, name, category, address, metro_stations, coords)
VALUES (:link, :name, :category, :address, :metro_stations, :coords)
RETURNING id;
"""

estate_by_id = """
SELECT * FROM estates
WHERE id = :estate_id
"""

all_estate = """
SELECT * FROM estates
"""