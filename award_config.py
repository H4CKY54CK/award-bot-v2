# Bot 1 and 2
PRIMARY = 'mhcp1'
SECONDARY = 'mhcp2'
# Records file
BOOK = 'records.json'
# Keyword
KEYWORD = '!award'
# Cooldown time before comment is entered into the queue
COOLDOWN = 0
# Time to keep before deleting.
TIME_TO_KEEP = 10386000
#Log file
LOGS = 'logs.txt'
# Flairs
FLAIR_LEVELS={
    1: 'Level 1',
    2: 'Level 2',
    3: 'Level 3',
    4: 'Level 4',
    5: 'Level 5',
    6: 'Max Level',
}
# Ignore this. It creates the dynamicity of the flair levels.
REVERSE_FLAIRS = {a:b for b, a in FLAIR_LEVELS.items()}
FLAIR_VALUES = FLAIR_LEVELS.values()
MAX_LEVEL = FLAIR_LEVELS[len(FLAIR_LEVELS)]
# I forget
TIMEFRAME = 604800.0
# Karma threshold
KARMA = 100
# All message responses. I'm sure you can figure out what they mean based on what they say, or what they are called
RECORDED = "Award recorded. Thank you."
QUEUEDOWN = "Your !award has been added to the queue because you are still on cooldown. (Time remaining: "
DUPLICATE = "You have already !awarded this comment."
POST = "Only other comments can be !awarded."
SELF_AWARD = "You can't !award yourself."
BOT_AWARD = "You can't !award the bot."
AWARD_AWARD = "You can't !award other !awards."
ALREADY_MAX = "User already max level. But they appreciate your generosity."
CUSTOM_FLAIR = "User has a custom flair already. But they appreciate your generosity."
LACK_LEVEL = "You lack the required level to assign yourself a custom flair."
MULTI_LINE = "Multi-line message detected. Please try again."
EXCEEDED = "Your flair text exceeded reddit's limit of 64 characters, but I assigned what I could."
FLAIR_CHANGED = "Your flair has been set. Let me know if you change your mind! Old:"
ILEGAL = "Illegal characters detected. Please try again."
SUBMISSION_KARMA = "You've acquired enough karma on this submission to earn yourself a level up!"
INVITE_SUBJECT = "You're invited!"
INVITE_BODY = "Explanation of invitation... Sorry, I got lazy."