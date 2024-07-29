import time

from app.controllers.summary import Summary
import datetime

while True:
    summary = Summary('TVS')
    summary.add_kpi()