import os
import sys
import praw
import json
import time
from configparser import ConfigParser
from award_config import *

class Bot:

    def __init__(self, site, subreddit=None):

        self.reddit = praw.Reddit(site)
        if subreddit is None:
            subreddit = self.reddit.custom.config['subreddit']
        self.subreddit = self.reddit.subreddit(subreddit)
        print(f"Testing in {self.subreddit.display_name}")

    def verify(self, msg, award_time):

        for comment in self.subreddit.stream.comments(skip_existing=True, pause_after=0):
            if comment is None:
                continue
            elif comment.body == msg or comment.body.startswith(msg):
                # contents = comment.body
                # print(f"The Bot:\n    {contents}")
                # try:
                #     pcontents = comment.parent().body
                #     print(f"The !awarder:\n    {pcontents}")
                # except:
                #     pcontents = comment.parent().description
                #     print(f"The !awarder:\n    {pcontents}")
                # try:
                #     gpcontents = comment.parent().parent().body
                #     print(f"The !awardee:\n    {gpcontents}")
                # except:
                #     try:
                #         gpcontents = comment.parent().description
                #         print(f"The !awardee:\n    {gpcontents}")
                #     except:
                #         pass
                # print(f"Expecting the Bot's reply to say:\n    {msg}")
                elapsed = comment.created_utc - award_time
                print(f'\n\033[38;2;124;252;0mPASSED (response time: {elapsed:.02f})\033[0m\n-------------\n')
                return True
        print('\n\033[38;2;255;0;0mFAILED DUE TO INTERRUPTION\033[0m\n-------------\n')
        return False

    def reply(self, item):

        com = self.reddit.comment(item)
        return com.reply('hellurr')

    def award(self, item):

        com = self.reddit.comment(item)
        return com.reply('!award')


def main():

    bot1 = Bot(TEST1, SUBREDDIT)
    bot2 = Bot(TEST2, SUBREDDIT)

    bot1.subreddit.flair.delete(str(bot2.reddit.user.me()))

    for item in bot1.subreddit.new():
        awt = item.reply('!award')
        break
    bot1.verify(POST, awt.created_utc)
    for item in bot2.subreddit.new():
        awt = com = item.reply('hellurr')
        break
    awt = bot1.award(com)
    bot1.verify(RECORDED, awt.created_utc)
    awt = com = bot1.award(com)
    bot1.verify(DUPLICATE, awt.created_utc)
    awt = bot1.award(com)
    bot1.verify(SELF_AWARD, awt.created_utc)
    for item in bot2.subreddit.new():
        comments = item.comments.list()
        for i in comments:
            if str(i.author).lower() == BOT_NAME:
                awt = com = i.reply('!award')
                break
        break
    bot1.verify(BOT_AWARD, awt.created_utc)
    awt = bot1.award(com)
    bot1.verify(AWARD_AWARD, awt.created_utc)
    bot1.subreddit.flair.set(str(bot2.reddit.user.me()), 'Max Level', '')
    for item in bot2.subreddit.new():
        awt = com = item.reply('hellurr')
        break
    awt = bot1.award(com)
    bot1.verify(ALREADY_MAX, awt.created_utc)
    bot1.subreddit.flair.set(str(bot2.reddit.user.me()), 'Custom Flair', '')
    for item in bot2.subreddit.new():
        awt = com = item.reply('hellurr')
        break
    awt = bot1.award(com)
    bot1.verify(CUSTOM_FLAIR, awt.created_utc)

    print("Starting inbox tests...\n\n")

    bot1.subreddit.flair.set('H4CKY54CK', 'Antagonist', '')
    bot1.reddit.redditor('misanthropydroid').message('something', 'set my flair')
    time.sleep(10)
    for item in bot1.subreddit.flair():
        if item['user'] == bot1.reddit.user.me():
            assert item['flair_text'] == 'Antagonist', 'Flair assignment incorrect.'
            break
    print('Flair correctly denied.')
    print('\n\033[38;2;124;252;0mPASSED\033[0m\n-------------\n')
    bot1.subreddit.flair.set('H4CKY54CK', 'Master Misanthrope', '')
    bot1.reddit.redditor('misanthropydroid').message('something', 'set my flair')
    time.sleep(10)
    for item in bot1.subreddit.flair():
        if item['user'] == bot1.reddit.user.me():
            assert item['flair_text'] == 'set my flair', 'Flair assignment incorrect.'
            break
    print('Flair assigned correctly.')
    print('\n\033[38;2;124;252;0mPASSED\033[0m\n-------------\n')
    bot1.reddit.redditor('misanthropydroid').message("something", "I hate all of you. Equally, of course, because I'm fair.")
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
