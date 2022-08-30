from dataclasses import dataclass
from datetime import datetime, timedelta
import time
from typing import Optional


@dataclass
class Player:
    start_dt: Optional[datetime] = None
    paused_seek: Optional[int] = None
    paused: bool = True

    def start(self):
        self.start_dt = datetime.now()
        self.paused = False

    def seek(self, seconds):
        if self.paused:
            self.paused_seek = seconds
        else:
            self.start_dt = datetime.now() - timedelta(seconds=seconds)

    def pause(self):
        if self.paused:
            assert self.paused_seek
            self.start_dt = datetime.now() - timedelta(seconds=self.paused_seek)
            self.paused_seek = None
            self.paused = False
        else:
            assert self.start
            self.paused_seek = int((datetime.now() - self.start_dt).seconds)
            self.start_dt = None
            self.paused = True

    def stop(self):
        self.start_dt = None
        self.paused_seek = None
        self.paused = False

    def get_time(self):
        if self.paused:
            return self.paused_seek
        else:
            return int((datetime.now() - self.start_dt).seconds)


if __name__ == '__main__':
    p = Player()
    p.start()
    time.sleep(1)
    p.pause()
    time.sleep(2)
    print(p.get_time())
