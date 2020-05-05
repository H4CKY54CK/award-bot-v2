import os
import re
import json
import praw
import time
import datetime
from multiprocessing import Process
# Hassle-free way to import the dev's config, and when the updated bot is pushed, prevent accidental overwriting of user's config
# Hassle-free for me, anyway
try:
    from config import *
except:
    from award_config import *

class Bot:
    'Reddit bot.'
    def __init__(self, site, book=None):
        'Initial setup.'
        if book is not None:
            self.book = book
            if not os.path.exists(self.book):
                self.data = {'queue': {}, 'recent': {}, 'submissions': []}
                json.dump(self.data, open(self.book, 'w'), indent=4)
            self.data = json.load(open(self.book))
        self.reddit = praw.Reddit(site)
        self.subreddit = self.reddit.subreddit(SUBREDDIT)
        self.THEBOT = str(self.reddit.user.me())

    def start_stream(self):
        'Begin streaming comments from subreddit.'
        counter = 0
        print(self.subreddit.display_name)
        for comment in self.subreddit.stream.comments(skip_existing=True, pause_after=0):
            counter += 1
            if counter == 100:
                counter = 0
                self.check_queue()
            if comment is None:
                continue
            if comment.body == KEYWORD:
                state = self.check(comment)
                if type(state) == str:
                    comment.reply(state)
                    continue
                    # comment.refresh()
                    # authors = [str(i.authors) for i in comment.replies]
                    # if self.reddit.user.me() in authors:
                    #     continue
                else:
                    self.process_comment(comment)

    def check_queue(self):
        'Check items in the queue.'

        # load records
        # set up easy access
        queue = self.data['queue']
        recent = self.data['recent']
        # createempty list to use later (iterating over a list, and trying to modify somthing in the list causes it to skip)
        users = []
        # iterate over the queue
        for user in queue:
            if recent[user].get('created', 0) + COOLDOWN < time.time():
                # we have the id
                try:
                    # use the id to create an instance of the comment. if it returns a comment, it succeeded. otherwise, it throws an error
                    comment = self.reddit.comment(queue[user][-1])
                # if it throws an error
                except:
                    # continue (by skipping everything from here down (within indentation), basically by moving back up to the top of
                    # this code block right under the `for` loop)
                    continue
                # by getting here, we successfully connected to reddit, because we built the comment
                state = self.check(comment, queued=True)
                # if my function returns a string, it's because it denied the award, as per our instruction
                if isinstance(state, str):
                    # tell them that
                    comment.reply(state)
                else:
                    # process it. this is my function, not praw's or reddit's. the only thing that connects to reddit in it, is 
                    # the reply. praw ALWAYS throws an error if something doesnt go through perfectly (usually. the only time it
                    # doesn't, is stuff like the finer features)
                    self.process_comment(comment)
                # we got this far, we must have been doing everything successfully. delete item from user's queue
                del queue[user][0]
            # append all users to our users list
            users.append(user)
        # iterate over our USERS list, not the queue
        for user in users:
            # if their queue is empty, remove the user
            if len(queue[user]) == 0:
                del queue[user]
            # if the user's last award ever is older than the time we designate, delete them from the rest of the records. 
            # this might be incorrect. i need to double check this, since we're also removing comments as they hit a certain age
            # elsewhere in the script
            if time.time() - recent[user].get('created', 0) > TIME_TO_KEEP:
                del recent[user]
        json.dump(self.data, open(self.book, 'w'), indent=4)

    def check(self, comment, queued=False):
        'Determine if issuer of `!award` is eligible to do so.'

        # A better name would have been `awards`
        recent = self.data['recent']
        user = str(comment.author)
        parent = comment.parent()
        # Check both sources for this value. First, the fast one. Then, the reliable one.
        parent_id = comment.parent_id or parent.name
        parent_user = str(parent.author)

        # See if they are in `awards` (`recent`)
        if user in recent.keys():
            # Each user has an entry in `recent`, called `created`.
            # THIS should have been named `recent`
            last = recent[user].get('created', 0)
            # And a dict of `comment id:comment.created_utc` of comments this user has awarded.
            awarded = recent[user].get('awarded', {})
        # If they aren't, set up some defaults.
        else:
            last = 0
            awarded = {}
        # Does the parent comment's ID already exist in the dict of what they've already awarded?
        if parent_id in awarded.keys():
            return DUPLICATE
        # A 'fullname' ID includes a prefix to the normal ID, letting us know what it is
        # 't3_...' is a submission
        if parent_id.startswith('t3'):
            return POST
        # Are they commenting on their own comment?
        if user == parent_user:
            return SELF_AWARD
        # Is the parent comment one made by this bot?
        if parent_user == self.THEBOT:
            return BOT_AWARD
        # Is this `!award` `!award`ing another `!award`?
        if parent.body == KEYWORD:
            return AWARD_AWARD
        # If the argument `queued` is True, then return. We don't want to accidentally requeue a queued comment
        # If it's False, then we can keep going
        if queued:
            return True
        # If the time of their last comment PLUS however long the cooldown is IS GREATER THAN the time this comment was created,
        if last + COOLDOWN > comment.created_utc:
            remaining = (last + COOLDOWN) - comment.created_utc
            if user not in self.data['queue']:
                self.data['queue'].update({user: []})
            queue = self.data['queue']
            queue[user].append(comment.id)
            json.dump(self.data, open(self.book, 'w'), indent=4)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {comment.id} entered into queue.\n")
            return QUEUEDOWN + f"{datetime.timedelta(seconds=round(remaining))}"
        return True
    def process_comment(self, comment):
        parent = comment.parent()
        author = str(parent.author)
        flair = parent.author_flair_text
        chauthor = str(comment.author)
        flair_class = ''
        if flair == MAX_LEVEL:
            comment.reply(ALREADY_MAX)
        elif flair in FLAIR_VALUES:
            user_level = REVERSE_FLAIRS[flair]
            new_flair = FLAIR_LEVELS[user_level+1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(RECORDED)
            self.add(comment)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} has been incremented one level, courtesy of {chauthor}.\n")
            if new_flair == MAX_LEVEL:
                self.reddit.redditor(author).message(INVITE_SUBJECT, INVITE_BODY)
        elif flair == None or flair == '':
            new_flair = FLAIR_LEVELS[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            comment.reply(RECORDED)
            self.add(comment)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} has been incremented one level, courtesy of {chauthor}.\n")
        elif len(flair) > 0:
            comment.reply(CUSTOM_FLAIR)
    def add(self, comment):
        recent = self.data['recent']
        author = str(comment.author)
        if author not in recent.keys():
            recent.update({author:{'created': comment.created_utc, 'awarded': {comment.parent_id: comment.created_utc}}})
        else:
            recent[author].update({'created': comment.created_utc})
            awarded = recent[author]['awarded']
            last_key = next(iter(awarded))
            if time.time() - awarded[last_key] > TIME_TO_KEEP:
                awarded.popitem()
            awarded.update({comment.parent_id: comment.created_utc})
        json.dump(self.data, open(self.book, 'w'), indent=4)
    def start_checking(self):
        print(self.subreddit.display_name)
        if not os.path.exists(SUBMISSIONS):
            data = {'submissions': []}
            json.dump(data, open(SUBMISSIONS, 'w'))
        data = json.load(open(SUBMISSIONS))
        while True:
            self.flairs = {}
            valid = r'[a-zA-Z0-9_-]+'
            for submission in self.subreddit.new(limit=None):
                if submission.created_utc > (time.time() - TIMEFRAME):
                    if submission.score >= KARMA and submission.is_self:
                        author = str(submission.author)
                        if submission.id not in data['submissions']:
                            data['submissions'].append(submission.id)
                            json.dump(data, open(SUBMISSIONS, 'w'), indent=4)
                            self.process_submission(submission)
                else:
                    continue
            for item in self.subreddit.flair(limit=None):
                self.flairs.update({str(item['user']):item['flair_text']})
            for msg in self.reddit.inbox.all():
                if msg is None or msg.distinguished:
                    continue
                if msg.new:
                    author = str(msg.author)
                    valid_user = re.match(valid, author)
                    if author in self.flairs and valid_user and not msg.was_comment:
                        user_flair = self.flairs[author]
                        if len(user_flair) > 0 and user_flair not in FLAIR_VALUES:
                            self.process_message(msg)
                        elif user_flair == MAX_LEVEL:
                            self.process_message(msg)
                        else:
                            msg.reply(LACK_LEVEL)
                            msg.mark_read()
    def process_message(self, msg):
        valid = r"[a-zA-Z0-9!#$%&'()*+,-\./:;<=>?@_{|}~]+"
        author = str(msg.author)
        flair_class = '' or None
        body = msg.body
        valid_body = re.match(valid, body)
        content = msg.body.split('\n')
        if len(content) > 1:
            msg.reply(MULTI_LINE)
            msg.mark_read()
        elif len(content) == 1:
            if valid_body:
                new_flair = content[0].rstrip()[:64]
                if len(msg.body) > 64:
                    old_flair = self.flairs[author]
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(EXCEEDED + f" Old: {old_flair} | New: {new_flair}")
                    msg.mark_read()
                    with open(LOGS, 'a') as f:
                        f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} user flair has been changed. Source: inbox. Old flair: {old_flair} | New flair: {new_flair}.\n")
                else:
                    old_flair = self.flairs[author]
                    self.subreddit.flair.set(author, new_flair, flair_class)
                    msg.reply(FLAIR_CHANGED + f" Old: {old_flair} | New: {new_flair}")
                    msg.mark_read()
                    with open(LOGS, 'a') as f:
                        f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} user flair has been changed. Source: inbox. Old flair: {old_flair} | New flair: {new_flair}.\n")
            else:
                msg.reply(ILLEGAL)
                msg.mark_read()
    def process_submission(self, submission):
        submission = self.reddit.submission(submission)
        author = str(submission.author)
        flair = submission.author_flair_text
        flair_class = ''
        if flair == MAX_LEVEL:
            pass
        elif flair in FLAIR_VALUES:
            user_level = REVERSE_FLAIRS[flair]
            new_flair = FLAIR_LEVELS[user_level+1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            submission.reply(SUBMISSION_KARMA)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} incremented one level. Source: Submission threshold met. {submission.id}.\n")
        elif flair == None or flair == '':
            new_flair = FLAIR_LEVELS[1]
            self.subreddit.flair.set(author, new_flair, flair_class)
            submission.reply(SUBMISSION_KARMA)
            with open(LOGS, 'a') as f:
                f.write(f"{datetime.datetime.fromtimestamp(time.time())}: {author} incremented one level. Source: Submission threshold met. {submission.id}.\n")
        elif len(flair) > 0:
            pass

if __name__ == '__main__':
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    b1 = Process(target=Bot(PRIMARY, BOOK).start_stream, daemon=True)
    b2 = Process(target=Bot(SECONDARY, None).start_checking, daemon=True)
    b1.start()
    b2.start()
    while True:
        if not b1.is_alive():
            b1 = Process(target=Bot(PRIMARY, BOOK).start_stream, daemon=True)
            b1.start()
        if not b2.is_alive():
            b2 = Process(target=Bot(SECONDARY, None).start_checking, daemon=True)
            b2.start()
        time.sleep(.5)
