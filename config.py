# Analytics DB
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Main DB
MONGO_URL = 'mongo://'
MONGO_DB = 'speakol_crawler'
MONGO_COLLECTION = 'roots_analytics'

# Analytics config
T_USER = True      # track online users
T_WORDS = True     # track words usage
BULK_INSERT = False # use bulk insert
LOAD_DB = False     # load the data from database

# Intervals
"""
SEC = 60*60*24         # keep for 1 day
MIN = 60*24*3        # keep for 3 days
HR = 30*24           # keep for 1 month
DAY = 90           # keep for 3 month
"""
