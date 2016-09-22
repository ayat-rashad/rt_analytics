from kairos import Timeseries
from kairos.exceptions import UnknownInterval
from pymongo import MongoClient
from datetime import datetime, timedelta
import time, redis, logging
from collections import defaultdict, Counter
import threading


def setup_log(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    fh = logging.FileHandler('log/%s.log' %name)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)

    return log


class AnalyticsManager:
    def __init__(self, client, loadFromDB=False, bulk_insert=False,
                    track_users=False, track_words=False):
        """
        TODO: config redis persistence and restoring lost data.
        TODO: populate memory from database
        TODO: setup config file
        """

        # Redis server to send data to
        self._client = client
        self._log = setup_log('manager')

        # database
        if loadFromDB:
            try:
                self.dbclient = MongoClient()
                self._DB = dbclient['campaign_analytics']
                self.load()
            except:
                self._log.error('ERROR: could not connect to MongoDB.')

        self._intervals = {
          'second':{
            'step':1,                  # one second
            'steps':60*60*24,          # keep for 1 day
          },
          'minute':{
            'step':60,                # 60 seconds
            'steps':60*24*3,          # keep for 3 days
          },
          'hour':{
            'step':'1h',            # one hour
            'steps':30*24,           # keep for 1 month
            'steps':3
          },
          'day':{
            'step':'1d',            # one day
            'steps':90           # keep for 3 month
          }
        }

        self._inserts = defaultdict(Counter)
        self._insert_lock = threading.Lock()
        self._n_inserts = 0
        self.bulk_insert = bulk_insert
        self._bulk_size = 16
        self._pipelined = 0
        self.track_users = track_users
        self.track_words = track_words

        # Series
        self.events = Timeseries(self._client, type='count', intervals=self._intervals)

        # Online users, consider offline after 2 minutes
        self.users = Timeseries(self._client, type='count',
                                intervals={'second2':{ 'step':1, 'steps':20 }})

        # Effective words, keep for 1 month
        self.words = Timeseries(self._client, type='histogram',
                                intervals={'month':{ 'step':'30d', 'steps':3 }})


    def store_event(self, event):
        """
        parameters:
            event: {
            campID: (int)
            etype: event type (str). pview, imp, or click.
            timestamp: time of event (int), (default) current time.
            words: list of words related to this event, (default) [].
            }

        returns:
            0 if success, otherwise -1 and { error: "message" }
        """
        try:
            campID, etype = event['campID'], event['etype']
            timestamp = event.get('timestamp', time.time())
            words = event.get('words', [])
            eventKey = '%d:%s' %(campID,etype)
            userKey = '%d:online' %(campID)
        except:
            msg = 'wrong event structure. type: %s, event: %s' %(type(event), event)
            self._log.error(msg)
            return (-1, {'error': msg})

        if etype not in ['pview', 'imp', 'click']:
            msg = 'wrong event type "%s",\
                    valid values: pview, imp, click.' %etype
            self._log.error(msg)
            return (-1, {'error': msg})

        # Bulk insert
        if self.bulk_insert:
            temp_inserts = None
            with self._insert_lock:
                self._inserts[timestamp][eventKey] += 1
                self._n_inserts += 1

                if self._n_inserts >= self._bulk_size:
                    try:
                        self.events.bulk_insert({t: {k:[v2] for k,v2 in v.items()} for t,v in self._inserts.items()})
                        self._inserts = defaultdict(Counter)
                        self._n_inserts = 0
                    except Exception as e:
                        msg = '%s: %s' %(type(e), e)
                        self._log.error(msg)
                        return (-1, {'error': msg})

        # Single insert
        else:
            try:
                self.events.insert(eventKey, timestamp=timestamp)
                '''self._pipelined += 1
                if self._pipelined >= self._bulk_size:
                    self.events.execute()
                    self._pipelined = 0'''

                # only count the user if the event is page view
                if self.track_users and etype=='pview':
                    self.users.insert(userKey, timestamp=timestamp)

                # only count the word if it led to impression or click
                if self.track_words and etype in ['imp', 'click']:
                    self.words.insert(campID, words, timestamp=timestamp)

            except Exception as e:
                msg = '%s: %s' %(type(e), e)
                self._log.error(msg)
                return (-1, {'error': msg})

        return (0, {'status': 'SUCCESS'})


    def get_camp_data(self, event):
        """
        parameters:
            event: {
            campID: (int)
            etype: event type (str). pview, imp, or click,
            interval: (str) second, minute, or hour. (default) minute,
            get_users: (bool) get online users. (default) True,
            get_camp_words: (bool) effective words for this campaign. (default) False,
            get_all_words: (bool) effective words for all campaigns. (default) False
            }

        returns:
            code (int) 0 for success, -1 for failure.
            if success, result:
                {
                  data: (list) (timestamp, event_count) tuples,
                  users: (int) count of online users,
                  camp_words: (list) most effective words for this campaign,
                  all_words: (list) most effective words of all campaigns
                }
            if failure: { error: "error message" }

        TODO: check if campID exists
        TODO: query by start and end
        """
        try:
            campID, etype = event['campID'], event['etype']
            interval = event.get('interval', 'minute')
            get_users = event.get('get_users', True)
            get_camp_words = event.get('get_camp_words', False)
            get_all_words = event.get('get_all_words', False)
            eventKey = '%d:%s' %(campID,etype)
            userKey = '%d:online' %(campID)
        except Exception as e:
            msg = 'ERROR: wrong event structure. %s' %e
            self._log.error(msg)
            return (-1, {'error': msg})

        data = []

        if etype not in ['pview', 'imp', 'click']:
            msg = 'wrong event type "%s",\
                    valid values: pview, imp, click.' %etype
            self._log.error(msg)
            return (-1, {'error': msg})

        result = {}

        try:
            data = self.events.series(eventKey, interval=interval)
            result['data'] = list(data.items())

            if self.track_users and get_users:
                users = self.users.series(userKey, interval='second2')
                users = sum(users.values())
                result['users'] = users

            if self.track_words and get_camp_words:
                camp_words = self.words.series(campID, 'month')
                sorted_words = sorted([(w,c) for w,c in camp_words.items()],
                                        key=lambda t: t[1])
                result['camp_words'] = sorted_words

            if self.track_words and get_all_words:
                all_camps = self.words.list()
                all_camps_words = self.words.series(all_camps, 'month')
                sorted_words = sorted([(w,c) for w,c in all_camps_words.items()],
                                        key=lambda t: t[1])
                result['all_words'] = sorted_words

        except UnknownInterval as e:
            msg = 'ERROR: wrong interval type "%s",\
                    valid values: second, minute, hour.' %str(interval)
            self._log.error(msg)
            return (-1, {'error': msg})

        except Exception as e:
            msg = '%s: %s.' %(type(e), e)
            self._log.error(msg)
            return (-1, {'error': msg})

        #result = {'data': list(data.items()), 'users': users}

        return (0, result)


    def flush(self):
        """
        Deletes all data stored in redis
        """
        self._log.info('Removing all data from database.')
        self.events.delete_all()
        self.users.delete_all()
        self.words.delete_all()


    def load(self):
        """
        load data from the database when the cache manager is up and running
        """
        pass
