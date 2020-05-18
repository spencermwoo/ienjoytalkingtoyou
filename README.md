This is primarily a template for setting up a conversation bot in a subreddit.

Currently setup with a naive SQL chatbot from https://rodic.fr/blog/python-chatbot-1/

# Requirements

* Python 3.6+
* pip3
* praw
* reddit account and auth tokens

# How to run persistently

	cron, systemd, etc
	nohup /usr/bin/python3 /root/ienjoytalkingtoyou/reply.py &

# How to change bot

It's simple to replace the bot or write your own.

	mitsuku
	pandorabots
	cleverbotfree