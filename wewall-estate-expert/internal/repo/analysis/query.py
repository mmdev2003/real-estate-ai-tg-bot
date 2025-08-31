create_analysis = """
INSERT INTO analysis (analysis_name, analysis_summary)
VALUES (:analysis_name, :analysis_summary)
RETURNING id;
"""

all_analysis = """
SELECT * FROM analysis;
"""