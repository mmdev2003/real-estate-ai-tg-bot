create_user = """
INSERT INTO users (tg_chat_id, source_type)
VALUES (:tg_chat_id, :source_type)
RETURNING id;
"""

user_by_tg_chat_id = """
SELECT * FROM users 
WHERE tg_chat_id = :tg_chat_id;
"""

all_user = """
SELECT * FROM users;
"""

update_is_bot_blocked = """
UPDATE users
SET is_bot_blocked = :is_bot_blocked
WHERE id = :user_id
"""
