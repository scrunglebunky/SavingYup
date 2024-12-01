 # THE LOG
log_total = {"kills":0,"got_away":0,"shots":0,"hits":0,"damage":0}
log_zone = log_total.copy()
    
# UPDATING THE LOG
@staticmethod
def log_push():
    # this takes the log info from the current zone, and pushes it to update the total log
    for k,v in log_zone.items():
        log_total[k] += log_zone[k]
        log_zone[k] = 0

# RESETTING THE LOG SINCE THIS IS ALL GLOBAL BECAUSE I DON'T WANT TO PASS MORE ARGUMENTS
def log_reset():
    log_total["kills"] = 0
    log_total["got_away"] = 0
    log_total["shots"] = 0
    log_total["hits"] = 0
    log_total["damage"] = 0 

# FIX THIS IF YOU OPTIMIZE EVERYTHING