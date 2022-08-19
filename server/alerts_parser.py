from threading import Timer
from ukraine_map import UkraineMap
from urllib.request import urlopen
from pprint import pprint
import datetime as dt
import json

class _RepeatTimer(Timer):
    def run(self):
        self.function(*self.args, **self.kwargs)
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class AlertsParser:
    def __init__(self, map: UkraineMap, update_interval: int = 10):
        self._UPDATE_TIME = update_interval
        self._map = map
        self._timer = None
        self._last_update = None


    def start(self):
        update_timer = _RepeatTimer(self._UPDATE_TIME, self._update_status)
        update_timer.start()


    def _update_status(self):
        try:
            with urlopen('https://sirens.in.ua/api/v1/', timeout=self._UPDATE_TIME) as response:
                data = response.read()
                js = json.loads(data)
                self._map.set(regions=js)
                self._last_update = dt.datetime.now()
        except BaseException as err:
            pprint(f"Data parsing error {err=}, {type(err)=}")
        except:
            pprint("Unkwnon error")
        
    
    def last_update(self):
        if self._last_update != None:
            return self._last_update
        return None
