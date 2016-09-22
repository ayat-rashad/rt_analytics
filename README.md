___/event:__  
    parameters: __json__   
            `event`: {  
            `campID`: __(int)__,  
            `etype`: event type __(str)__. pview, imp, or click,  
            `timestamp`: time of event __(int)__, __(default)__ current time,   
            `words`: __(list)__  words related to this event, __(default)__ []  
}
    
returns: __json__   
            { `status`: "SUCCESS" } if success,  
             otherwise { `error`: "message" }
               
__/camp:__  
parameters: __json__  
event: {  
            `campID`: __(int)__,  
            `etype`: event type __(str)__. pview, imp, or click,  
            `interval`: __(str)__ second, minute, or hour. __(default)__ minute,  
            `get_users`: __(bool)__ get number of online users. __(default)__ True,  
            `get_camp_words`: __(bool)__ get effective words for this campaign. __(default)__ False,  
            `get_all_words`: __(bool)__ get effective words for all campaigns. __(default)__ False  
            }
    
returns: __json__  
if success, result __(gzipped)__:   
{   
`data`: __(list)__ (timestamp, event_count) tuples,  
   `users`: __(int)__ count of online users,  
 `camp_words`: __(list)__ most effective words for this campaign,  
   `all_words`: __(list)__ most effective words of all campaigns
     }  
            if failure: { `error`: "error message" }
