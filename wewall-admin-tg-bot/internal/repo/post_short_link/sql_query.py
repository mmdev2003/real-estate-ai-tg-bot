create_post_short_link = """
INSERT INTO post_short_links (tg_chat_id) 
VALUES(:tg_chat_id)
RETURNING id;
"""
update_post_short_link_name = """
UPDATE post_short_links 
SET name=:name 
WHERE tg_chat_id=:tg_chat_id;
"""

update_post_short_link_description = """
UPDATE post_short_links 
SET description=:description 
WHERE tg_chat_id=:tg_chat_id;
"""

update_post_short_link_image = """
UPDATE post_short_links 
SET image_name=:image_name, image_fid=:image_fid
WHERE tg_chat_id=:tg_chat_id;
"""

update_post_short_link_file = """
UPDATE post_short_links 
SET file_name=:file_name, file_fid=:file_fid
WHERE tg_chat_id=:tg_chat_id;
"""

delete_post_short_link = """
DELETE FROM post_short_links 
WHERE tg_chat_id=:tg_chat_id
"""

post_short_link_by_tg_chat_id = """
SELECT * FROM post_short_links 
WHERE tg_chat_id=:tg_chat_id;
"""