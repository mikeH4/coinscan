from db import CreateSQLTables

a = CreateSQLTables("db.db")

a += """
CREATE TABLE posts (
    id PRIMARY KEY NOT NULL ,
    title TEXT NOT NULL ,
    name TEXT NOT NULL ,
    created_utc INTEGER NOT NULL ,
    selftext TEXT NOT NULL ,
    selftext_html TEXT NOT NULL ,
    num_comments INTEGER NOT NULL,
    over_18 TEXT NOT NULL ,
    score INTEGER NOT NULL ,
    upvote_ratio FLOAT NOT NULL ,
    is_original_content TEXT NOT NULL ,
    is_self TEXT NOT NULL 
)
"""

a.execute()