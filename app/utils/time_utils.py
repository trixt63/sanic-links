from datetime import datetime
from datetime import timezone

def get_timestamp():
    timestamp = datetime.now(timezone.utc).timestamp()
    timestamp = int(timestamp//60*60)
    return str(timestamp)