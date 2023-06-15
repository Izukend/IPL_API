import datetime
import pytz

def Time():
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    time = pytz.timezone('Europe/Paris')
    start = datetime.datetime.now(time)
    
    date_time = start.strftime(format)
    return date_time
