create_state = """
INSERT INTO states (tg_chat_id)
VALUES (:tg_chat_id)
RETURNING id;
"""

state_by_id = """
SELECT * FROM states
WHERE tg_chat_id = :tg_chat_id;
"""

set_is_transferred_to_manager = """
UPDATE states
SET is_transferred_to_manager = :is_transferred_to_manager
WHERE id = :state_id
"""

increment_message_count = """
UPDATE states
SET count_message = count_message + 1
WHERE id = :state_id
"""

increment_estate_search_count = """
UPDATE states
SET count_estate_search = count_estate_search + 1
WHERE id = :state_id
"""

increment_estate_calculator_count = """
UPDATE states
SET count_estate_calculator = count_estate_calculator + 1
WHERE id = :state_id
"""

update_state_status = """
UPDATE states
SET status = :status
WHERE id = :state_id;
"""

delete_state_by_tg_chat_id = """
DELETE FROM states
WHERE tg_chat_id = :tg_chat_id;
"""
