create_chat = """
INSERT INTO chats (tg_chat_id)
VALUES (:tg_chat_id)
RETURNING id;
"""

chat_by_tg_chat_id = """
SELECT * FROM chats
WHERE tg_chat_id = :tg_chat_id;
"""

create_message = """
INSERT INTO messages (chat_id, text, role)
VALUES (:chat_id, :text, :role)
RETURNING id;
"""

message_by_chat_id = """
SELECT * FROM messages
WHERE chat_id = :chat_id
ORDER BY created_at ASC;
"""

delete_all_message = """
DELETE FROM messages
WHERE chat_id = :chat_id;
"""