from db import DB
import praw

reddit = praw.Reddit(
    client_id="nlG3egusjeGFsg",
    client_secret="ddLlW9bX_3rAffR_OdY-yXeRe8cTCw",
    password="newfklm0(J092j0rp23mr230rn",
    user_agent="super mikey",
    username="mike-halsey",
)

db = DB("db.db")

i = -1
gen = reddit.subreddit("CryptoMoonShots").search(
    'flair:"Meme/shitcoin"',
    sort="new",
    limit=None
)
for post in gen:
    i += 1
    db.insert("posts", dict(
        id=post.id,
        title=post.title,
        name=post.name,
        created_utc=post.created_utc,
        selftext=post.selftext,
        selftext_html=post.selftext_html,
        num_comments=post.num_comments,
        over_18=post.over_18,
        score=post.score,
        upvote_ratio=post.upvote_ratio,
        is_original_content=post.is_original_content,
        is_self=post.is_self
    ), commit=False)
    if i % 50 == 0 and i > 0:
        db.conn.commit()

db.conn.commit()