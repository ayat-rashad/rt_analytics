__/event:
    parameters: __json 
            event: {
            campID: (int)
            etype: event type (str). pview, imp, or click.
            timestamp: time of event (int), (default) current time.
            words: list of words related to this event, (default) [].
            }

        returns: __json
            {status: "SUCCESS"} if success, otherwise { error: "message" }
            
__/camp:
    parameters: __json
            event: {
            campID: (int),
            etype: event type (str). pview, imp, or click,
            interval: (str) second, minute, or hour. (default) minute,
            get_users: (bool) get number of online users. (default) True,
            get_camp_words: (bool) get effective words for this campaign. (default) False,
            get_all_words: (bool) get effective words for all campaigns. (default) False
            }

        returns: __json
            if success, result (gzipped): {
                data: (list) (timestamp, event_count) tuples,
                users: (int) count of online users,
                camp_words: (list) most effective words for this campaign,
                all_words: (list) most effective words of all campaigns
                }
            if failure: { error: "error message" }
