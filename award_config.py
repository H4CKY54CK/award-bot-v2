# Bot 1 and 2
PRIMARY = ''
SECONDARY = ''
# Tests require two valid accounts that are not the award bot.
TEST1 = 'hackysack'
TEST2 = 'hzazael'
BOT_NAME = 'misanthropydroid'
DEBUG_MODE = False
# Subreddit to run the bot in
SUBREDDIT = 'misanthropytest'
# Records files
BOOK = 'records.json'
SUBMISSIONS = 'submissions.json'
# Keyword
KEYWORD = '!award'
# Cooldown time before comment is entered into the queue
COOLDOWN = 86000
#COOLDOWN = 86400
# Time to keep before deleting.
TIME_TO_KEEP = 10368000
#Log file
LOGS = 'logs.txt'
# Flairs
FLAIR_LEVELS = {
    1: 'Antagonist',
    2: 'Sceptic',
    3: 'Idealist',
    4: 'Disbeliever',
    5: 'Cynic',
    6: 'Realist',
    7: 'Pragmatist',
    8: 'Hermit',
    9: 'Monk',
    10: 'Guide',
    11: 'Tutor',
    12: 'Master Misanthrope',
}
# Ignore this. It creates the dynamicity of the flair levels.
REVERSE_FLAIRS = {a:b for b, a in FLAIR_LEVELS.items()}
FLAIR_VALUES = FLAIR_LEVELS.values()
MAX_LEVEL = FLAIR_LEVELS[len(FLAIR_LEVELS)]
# How long to look back for submissions for karma checking
TIMEFRAME = 604800.0
# Karma threshold
KARMA = 150
# All message responses. I'm sure you can figure out what they mean based on what they say, or what they are called
RECORDED = "Your *!award* has been recorded. Thank you."
QUEUEDOWN = "Your *!award* has been queued, and will be processed in "
DUPLICATE = "You have already *!award*ed this comment."
POST = "Only other comments can be *!award*ed."
SELF_AWARD = "You can't *!award* yourself."
BOT_AWARD = "You can't *!award* the bot."
AWARD_AWARD = "You can't *!award* other *!award*s."
ALREADY_MAX = "This user is already max level. But they appreciate your generosity."
CUSTOM_FLAIR = "This user is already max level. But they appreciate your generosity."
#CUSTOM_FLAIR = "This User has a custom flair already. But they appreciate your generosity."
LACK_LEVEL = "You lack the required level to assign yourself a custom flair."
MULTI_LINE = "Multi-line message detected. Please try again."
EXCEEDED = "Your flair text exceeded reddit's limit of 64 characters, but I assigned what I could."
FLAIR_CHANGED = "Your flair has been set. Let me know if you change your mind!"
ILEGAL = "Illegal characters detected. Please try again."
SUBMISSION_KARMA = "You've acquired enough karma on this submission to earn yourself a level up!"
INVITE_SUBJECT = "Congratulations!"
INVITE_BODY = "You've reached the top level of Master Misanthrope and can set yourself a custom flair by replying to this message."