import time

from app.controllers.summary import Summary
import datetime

while True:
    start = datetime.datetime.now()
    summary = Summary('TVS')
    summary.add_kpi()
    end = datetime.datetime.now()

    # 処理時間と待機時間で60秒になるように調整
    print('待機中...')
    remaining_time = datetime.timedelta(seconds=60) - (end - start)
    if remaining_time.total_seconds() > 3.0:
        time.sleep(remaining_time.total_seconds())
    else:
        time.sleep(3.0)