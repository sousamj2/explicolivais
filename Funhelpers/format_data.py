from datetime import datetime, timedelta
import locale
import pytz

def format_data(timestampUTC):
    # print(f"-----------------------[{timestampUTC}]----------",type(timestampUTC))
    
    if isinstance(timestampUTC, datetime):
        timestampUTC_str = timestampUTC.isoformat()
    elif isinstance(timestampUTC, str):
        timestampUTC_str = timestampUTC
    else:
        # If it's neither string nor datetime, return empty string or handle as an error
        return ""

    try:
        locale.setlocale(locale.LC_TIME, 'pt_PT.UTF-8')
        
        dt = datetime.fromisoformat(timestampUTC_str)
        dt = dt - timedelta(hours=1)
        lisbon_tz = pytz.timezone('Europe/Lisbon')
        
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        # print(f"Original datetime: {dt} with tz: {dt.tzinfo}")
        
        # dt_local = lisbon_tz
        dt_local = dt.astimezone(lisbon_tz)
        # print(f"Converted to Lisbon timezone: {dt_local} with tz: {dt_local.tzinfo}")
        
        now_local = datetime.now(lisbon_tz).date()
        dt_date = dt_local.date()
        yesterday = now_local - timedelta(days=1)
        
        if dt_date == now_local:
            date_str = "hoje"
        elif dt_date == yesterday:
            date_str = "ontem"
        else:
            date_str = dt_local.strftime('em %-d de %B de %Y')
        
        time_str = dt_local.strftime('às %H:%M')
        return f"{date_str} {time_str}"
        
    except Exception as e:
        print(f"Error formatting date: {e}")
        return timestampUTC

