create_estate_search_state_query = """
INSERT INTO estate_search_states (state_id, offers, estate_search_params)
VALUES (:state_id, :offers, :estate_search_params)
RETURNING id; 
"""

change_current_offer_by_state_id_query = """
UPDATE estate_search_states
SET current_offer_id = :current_offer_id
WHERE state_id = :state_id;
"""

change_current_estate_by_state_id_query = """
UPDATE estate_search_states
SET current_estate_id = :current_estate_id
WHERE state_id = :state_id;
"""

estate_search_state_by_state_id_query = """
SELECT * FROM estate_search_states
WHERE state_id = :state_id;
"""

delete_estate_search_state_by_state_id_query = """
DELETE FROM estate_search_states
WHERE state_id = :state_id;
"""