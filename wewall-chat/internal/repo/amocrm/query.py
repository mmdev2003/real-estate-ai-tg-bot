# INSERT
create_contact = """
INSERT INTO amocrm_contacts (amocrm_contact_id, name, tg_chat_id)
VALUES (:amocrm_contact_id, :name, :tg_chat_id)
RETURNING amocrm_contact_id;
"""
create_amocrm_lead = """
INSERT INTO amocrm_leads (amocrm_lead_id, amocrm_contact_id, amocrm_pipeline_id)
VALUES (:amocrm_lead_id, :amocrm_contact_id, :amocrm_pipeline_id)
RETURNING amocrm_lead_id;
"""

create_amocrm_chat = """
INSERT INTO amocrm_chats (amocrm_chat_id, amocrm_conversation_id, amocrm_lead_id)
VAlUES (:amocrm_chat_id, :amocrm_conversation_id, :amocrm_lead_id)
RETURNING amocrm_chat_id;
"""

create_amocrm_message = """
INSERT INTO amocrm_messages (amocrm_message_id, amocrm_chat_id, text, role)
VALUES (:amocrm_message_id, :amocrm_chat_id, :text, :role)
RETURNING amocrm_message_id;
"""

# SELECT
contact_by_id = """
SELECT * FROM amocrm_contacts
WHERE amocrm_contact_id = :amocrm_contact_id;
"""

contact_by_tg_chat_id = """
SELECT * FROM amocrm_contacts
WHERE tg_chat_id = :tg_chat_id;
"""

lead_by_id = """
SELECT * FROM amocrm_leads
WHERE amocrm_lead_id = :amocrm_lead_id
"""

lead_by_amocrm_contact_id = """
SELECT * FROM amocrm_leads 
WHERE amocrm_contact_id=:amocrm_contact_id;
"""

chat_by_id = """
SELECT * FROM amocrm_chats 
WHERE amocrm_chat_id=:amocrm_chat_id;
"""

chat_by_amocrm_lead_id = """
SELECT * FROM amocrm_chats 
WHERE amocrm_lead_id=:amocrm_lead_id;
"""

# DELETE
delete_amocrm_contact_by_id = """
DELETE FROM amocrm_contacts
WHERE amocrm_contact_id=:amocrm_contact_id
"""

delete_amocrm_lead_by_id = """
DELETE FROM amocrm_leads
WHERE amocrm_lead_id=:amocrm_lead_id
"""

delete_amocrm_chat_by_id = """
DELETE FROM amocrm_chats
WHERE amocrm_chat_id=:amocrm_chat_id
"""