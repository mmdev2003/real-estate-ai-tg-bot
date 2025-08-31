create_news = """
INSERT INTO news (news_name, news_summary)
VALUES (:news_name, :news_summary)
RETURNING id;
"""

all_news = """
SELECT * FROM news;
"""