import bot
import json
import os
import praw
import re
import sqlite3
import sys
import time
import traceback

WATCHED_SUBREDDIT = 'ienjoytalkingtoyou'  # feel free to use this to test the bot
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDDIT_BOT_USERNAME = 'ienjoytalkingtoyou'
REDDIT_BOT_PASSWORD = os.environ['REDDIT_BOT_PASSWORD']

verbose = False

# Create the PRAW instance
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent='ienjoytalkingtoyou',
                     username=REDDIT_BOT_USERNAME,
                     password=REDDIT_BOT_PASSWORD)

subreddit = reddit.subreddit(WATCHED_SUBREDDIT)

connection = sqlite3.connect('ienjoytalkingtoyou.sqlite')
cursor = connection.cursor()

try:
    # create table words
    cursor.execute('''
        CREATE TABLE words (
            word TEXT UNIQUE
        )''')
    # create table sentences
    cursor.execute('''
        CREATE TABLE sentences (
            sentence TEXT UNIQUE,
            used INT NOT NULL DEFAULT 0
        )''')
    # create association
    cursor.execute('''
        CREATE TABLE associations (
            word_id INT NOT NULL,
            sentence_id INT NOT NULL,
            weight REAL NOT NULL)
    ''')
except:
    pass

sql = sqlite3.connect('sql.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(id TEXT)')

# We'll load the IDs of comments we already replied to from the replied_to.json file on the current working dir
# replied_to_fname = os.path.join(os.getcwd(), 'replied_to.json')
# try:
#     with open(replied_to_fname, 'r') as fd:
#         replied_to = json.load(fd)
# except FileNotFoundError:
#     replied_to = []

# # Build the list of posts and comments
# def posts_and_comments(sub, **kwargs):
#     results = []
#     results.extend(sub.new(limit=1000))
#     results.extend(sub.comments(limit=1000))

#     # Filter out comments we already replied to
#     results = [r for r in results if r.id not in replied_to]
#     results.sort(key=lambda post: post.created_utc, reverse=True)

#     if not results:
#         print('No new posts.')

#     return results

# Build a stream with both posts and comments
def posts_and_comments(sub, **kwargs):
    results = []
    results.extend(sub.new(**kwargs))
    results.extend(sub.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results    

def controller():
    print(f'Replying to new messages on subreddit {WATCHED_SUBREDDIT}...')

    # Instantiate them
    # subs_comments = posts_and_comments(subreddit)

    subs_comments_stream = stream_generator(lambda **kwargs: posts_and_comments(subreddit, **kwargs), skip_existing=True)
    for comment in subs_comments_stream:
        time.sleep(1)

        try:
            # Shouldn't reply to our own comments
            if not isinstance(comment, Submission) and comment.author.name == REDDIT_BOT_USERNAME:
                continue

            # Should reply to new threads
            elif isinstance(comment, Submission):
                if comment.selftext:
                    comment.reply(bot(comment.selftext, comment.title))
                else:
                    comment.reply(bot(comment.title, "Hello"))

                if verbose:
                    print(f'Replying to new thread {comment}')

            # Should reply to top-leveln comments
            elif comment.is_root:
                if hasattr(comment.parent(), 'body'):
                    comment.reply(bot(comment.body, comment.parent().body))
                else:
                    comment.reply(bot(comment.body, comment.parent().selftext))

                if verbose:
                    print(f'Replying to top level comment {comment}')

            # Should reply to replies to the bot
            elif comment.parent().author is not None and comment.parent().author.name == REDDIT_BOT_USERNAME:
                if hasattr(comment.parent(), 'body'):
                    comment.reply(bot(comment.body, comment.parent().body))
                else:
                    comment.reply(bot(comment.body, comment.parent().selftext))
                
                if verbose:
                    print(f'Replying to interaction comment {comment}')

            # Should reply to people's replies on other replies
            else:
                if hasattr(comment.parent(), 'body'):
                    comment.reply(bot(comment.body, comment.parent().body))
                else:
                    comment.reply(bot(comment.body, comment.parent().selftext))
                
                if verbose:
                    print('Replying to conversation comment.')

            # replied_to.append(comment.id)

        # Catch exceptions to log them if they occur, but keep the bot running
        except Exception as e:
            print(f'Error: {e}')
            traceback.print_exc()

    # After replying to all comments, update replied_to file
    # with open(replied_to_fname, 'w') as fd:
    #     json.dump(replied_to, fd, ensure_ascii=False)

if __name__ == "__main__":
    controller()