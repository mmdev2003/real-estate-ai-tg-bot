create_rent_offer = """
INSERT INTO rent_offers (estate_id, link, name, square, price_per_month, design, floor, type, location, image_urls, offer_readiness, readiness_date, description)
VALUES (:estate_id, :link, :name, :square, :price_per_month, :design, :floor, :type, :location, :image_urls, :offer_readiness, :readiness_date, :description)
RETURNING id;
"""

rent_offer_by_id = """
SELECT * FROM rent_offers
WHERE id = :rent_offer_id
"""

all_rent_offer = """
SELECT * FROM rent_offers
"""

update_location = """
UPDATE rent_offers 
SET location = :location
WHERE id = :rent_offer_id
"""