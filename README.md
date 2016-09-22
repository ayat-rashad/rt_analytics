___/event:__<br>
    parameters: __json__ <br>
            `event`: {<br>
            `campID`: __(int)__,<br>
            `etype`: event type __(str)__. pview, imp, or click,<br>
            `timestamp`: time of event __(int)__, __(default)__ current time, <br>
            `words`: __(list)__  words related to this event, __(default)__ []<br>
}
<br><br>
returns: __json__ <br>
            { `status`: "SUCCESS" } if success,<br>
             otherwise { `error`: "message" }
<br><br>           
__/camp:__<br>
parameters: __json__<br>
event: {<br>
            `campID`: __(int)__,<br>
            `etype`: event type __(str)__. pview, imp, or click,<br>
            `interval`: __(str)__ second, minute, or hour. __(default)__ minute,<br>
            `get_users`: __(bool)__ get number of online users. __(default)__ True,<br>
            `get_camp_words`: __(bool)__ get effective words for this campaign. __(default)__ False,<br>
            `get_all_words`: __(bool)__ get effective words for all campaigns. __(default)__ False<br>
            }
<br><br>
returns: __json__<br>
if success, result __(gzipped)__: <br>
{ <br>
`data`: __(list)__ (timestamp, event_count) tuples,<br>
   `users`: __(int)__ count of online users,<br>
 `camp_words`: __(list)__ most effective words for this campaign,<br>
   `all_words`: __(list)__ most effective words of all campaigns
   <br>}<br>
            if failure: { `error`: "error message" }
