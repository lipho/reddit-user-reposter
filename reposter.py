import praw
import sqlite3
import time

#config

USERAGENT = "/u/plus20charisma's post & comment reposter by user & karma threshold."
USERNAME =  ""#bot's username
PASSWORD =  ""#bot's password
USERSCRAPE = "" #what user to scrape & repost from
SUBREDDIT = "" #what subreddit to post in. don't put /r/ or r/
MAXPOSTS = 100 #how far back to look.  max is 100
KARMATHRESHOLD = 1000 #anything with karma greater than this number will be reposted


WAIT = 30 #wait time in seconds between runs

#makes a database if one doesn't exist. 
#opens db if it already exists
print ("Opening database...")
sql = sqlite3.connect("sql.db")
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS oldsubmissions(ID TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS oldcomments(ID TEXT)')
sql.commit()

print("Logging in to reddit...")
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)

#comment scanner & reposter
def rep_bot_coms():
	user = r.get_redditor(USERSCRAPE)
	comments = user.get_comments(limit=MAXPOSTS)
	print ("Checking comments...")
	for comment in comments:
		#checks if comment already exists in db
		cur.execute('SELECT * FROM oldcomments WHERE ID=?', [comment.id])
		if not cur.fetchone():
			try:
				if comment.score > KARMATHRESHOLD:
					print ("Reposting comment above Karma Threshold...")
					repost_comment_body = comment.body
					#since comments don't have titles, the first 10 words become post title
					repost_title_list = repost_comment_body.split()
					repost_title = ' '.join(repost_title_list[:10]) + "..."
					r.submit(SUBREDDIT, repost_title, repost_comment_body+"\n > I'm a bot that is reposting from /u/%s. If there's any trouble, please message /u/plus20charisma!" % USERSCRAPE)
					print ("Comment posted to /r/"+SUBREDDIT+"!")
			except AttributeError:
				pass
			#writes comment to db by id
			cur.execute('INSERT INTO oldcomments VALUES(?)', [comment.id])
			sql.commit()
	print ("No more comments to submit!")

#same as rep_bot_coms() but for submissions
def rep_bot_submitted():
	user = r.get_redditor(USERSCRAPE)	
	posts = user.get_submitted(limit=MAXPOSTS)
	print ("Checking submissions...")
	for post in posts:
		cur.execute('SELECT * FROM oldsubmissions WHERE ID=?', [post.id])
		if not cur.fetchone():
			try:
				if post.score > KARMATHRESHOLD:
					print ("Reposting submission above Karma Threshold...")
					repost_title = post.title
					repost_url = post.url
					r.submit(SUBREDDIT, repost_title, repost_url+"\n > I'm a bot that is reposting from /u/%s. If there's any trouble, please message /u/plus20charisma!" % USERSCRAPE)
					print ("Submission posted to /r/"+SUBREDDIT+"!")
			except AttributeError:
				pass
			cur.execute('INSERT INTO oldsubmissions VALUES(?)', [post.id])
			sql.commit()
	print ("No more submissions to submit!")

while True:
	rep_bot_submitted()
	rep_bot_coms()
	print "Waiting " + str(WAIT) + " seconds"
	time.sleep(WAIT)

