create_sale_offer = """
INSERT INTO sale_offers (estate_id, link, name, square, price, price_per_meter, design, floor, type, location, image_urls, offer_readiness, readiness_date, description)
VALUES (:estate_id, :link, :name, :square, :price, :price_per_meter, :design, :floor, :type, :location, :image_urls, :offer_readiness, :readiness_date, :description)
RETURNING id;
"""

update_sale_offer_irr = """
UPDATE sale_offers 
SET irr = :irr
WHERE id = :sale_offer_id
"""

sale_offer_by_id = """
SELECT * FROM sale_offers
WHERE id = :sale_offer_id
"""

all_sale_offer = """
SELECT * FROM sale_offers
"""

