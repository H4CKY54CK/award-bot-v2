import os
import sys
import praw
import json
import time
from configparser import ConfigParser
from award_config import *

class Bot:

    def __init__(self, site, subreddit):

        self.reddit = praw.Reddit(site)
        if subreddit is None:
            subreddit = self.reddit.custom.config['subreddit']
        self.subreddit = self.reddit.subreddit(subreddit)
        print(f"Testing in {self.subreddit.display_name}")

    def award(self, item):

        try:
            item = self.reddit.comment(item)
        except:
            item = self.reddit.submission(item)
        return item.reply('!award')

    def verify(self, msg, award_time):

        for comment in self.subreddit.stream.comments(skip_existing=True, pause_after=0):
            if comment is None:
                continue
            elif comment.body == msg or comment.body.startswith(msg):
                if DEBUG_MODE:
                    contents = comment.body
                    print(f"The Bot:\n    {contents}")
                    try:
                        pcontents = comment.parent().body
                        print(f"The !awarder:\n    {pcontents}")
                    except:
                        pcontents = comment.parent().description
                        print(f"The !awarder:\n    {pcontents}")
                    try:
                        gpcontents = comment.parent().parent().body
                        print(f"The !awardee:\n    {gpcontents}")
                    except:
                        try:
                            gpcontents = comment.parent().description
                            print(f"The !awardee:\n    {gpcontents}")
                        except:
                            pass
                    print(f"Expecting the Bot's reply to say:\n    {msg}")
                elapsed = comment.created_utc - award_time
                print(f'\n\033[38;2;124;252;0mPASSED\n  Bot response: {msg}\n  Response time: {elapsed:.02f}\033[0m\n-------------\n')
                return True

def main():

    # Log both testing accounts in (you need two separate ones that arent the award bot)
    bot1 = Bot(TEST1, SUBREDDIT)
    bot2 = Bot(TEST2, SUBREDDIT)

    # Clear flair.
    bot1.subreddit.flair.delete(str(bot2.reddit.user.me()))

    # Create an award in given subreddit in given submission
    for item in bot1.subreddit.new():
        awt = item.reply(KEYWORD)
        break
    # Verify it fails
    bot1.verify(POST, awt.created_utc)

    # Create reply in given subreddit in given submission
    for item in bot2.subreddit.new():
        com = item.reply('hellurr')
        break
    awt = bot1.award(com)
    # Verify it succeeds.
    bot1.verify(RECORDED, awt.created_utc)

    awt = bot1.award(com)
    # Verify duplicate
    bot1.verify(DUPLICATE, awt.created_utc)

    awt = bot1.award(awt)
    # Verify award on ourself
    bot1.verify(SELF_AWARD, awt.created_utc)

    # Find a comment by the award bot, award it
    for item in bot2.subreddit.new():
        comments = item.comments.list()
        for i in comments:
            if str(i.author).casefold() == BOT_NAME.casefold():
                # Save comment
                awt = i.reply(KEYWORD)
                break
        break
    # Verify it fails
    bot1.verify(BOT_AWARD, awt.created_utc)

    # Award comment
    awt = bot1.award(awt)
    # Verify we can't award ourselves
    bot1.verify(AWARD_AWARD, awt.created_utc)

    # Set flair to max
    maxf = FLAIR_LEVELS.popitem()
    FLAIR_LEVELS[maxf[0]] = maxf[1]
    bot1.subreddit.flair.set(str(bot2.reddit.user.me()), maxf[1], '')
    # Create a comment
    for item in bot2.subreddit.new():
        # Save comment
        awt = item.reply('hellurr')
        break
    # Award that comment
    awt = bot1.award(awt)
    # Verify we can't award, because they are max level
    bot1.verify(ALREADY_MAX, awt.created_utc)
    # Assign custom flair
    bot1.subreddit.flair.set(str(bot2.reddit.user.me()), 'Custom Flair', '')
    for item in bot2.subreddit.new():
        # Save comment
        awt = item.reply('hellurr')
        break
    # Award the saved comment
    awt = bot1.award(awt)
    # Verify comment
    bot1.verify(CUSTOM_FLAIR, awt.created_utc)

    print("Starting inbox tests...\n\n")

    bot1.subreddit.flair.set(str(bot1.reddit.user.me()), '', '')
    bot1.reddit.redditor(BOT_NAME).message('something', 'set my flair')
    time.sleep(10)
    for item in bot1.subreddit.flair():
        if item['user'] == bot1.reddit.user.me():
            assert item['flair_text'] == '', 'Flair assignment incorrect.'
            break
    print('Flair correctly denied.')
    print('\n\033[38;2;124;252;0mPASSED\033[0m\n-------------\n')
    bot1.subreddit.flair.set(str(bot1.reddit.user.me()), maxf[1], '')
    bot1.reddit.redditor(BOT_NAME).message('something', 'set my flair')
    time.sleep(10)
    for item in bot1.subreddit.flair():
        if item['user'] == bot1.reddit.user.me():
            assert item['flair_text'] == 'set my flair', 'Flair assignment incorrect.'
            break
    print('Flair assigned correctly.')
    print('\n\033[38;2;124;252;0mPASSED\033[0m\n-------------\n')
    bot1.reddit.redditor(BOT_NAME).message("something", "I hate all of you. Equally, of course, because I'm fair.")
    time.sleep(10)
    for item in bot1.subreddit.flair():
        if item['user'] == bot1.reddit.user.me():
            assert item['flair_text'] == "I hate all of you. Equally, of course, because I'm fair.", 'Flair assignment incorrect.'
            break
    print('Flair assigned correctly.')
    print('\n\033[38;2;124;252;0mPASSED\033[0m\n-------------\n')

    print("All tests have passed.")

if __name__ == '__main__':
    ts = time.time()
    main()
    te = time.time() - ts
    print(f"Elapsed time: {te:.02f}")
