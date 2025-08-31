create_post_short_link = """
INSERT INTO post_short_links (id, name, description, image_name, image_fid, file_name, file_fid) 
VALUES (:post_short_link_id, :name, :description, :image_name, :image_fid, :file_name, :file_fid)
RETURNING id;
"""

delete_post_short_link = """
DELETE FROM post_short_links 
WHERE tg_chat_id=:tg_chat_id
"""

post_short_link_by_id = """
SELECT * FROM post_short_links 
WHERE id=:post_short_link_id;
"""