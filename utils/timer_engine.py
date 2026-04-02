import asyncio
from typing import Callable, Optional


class TimerInstance:
    def __init__(self, timer_id, seconds, on_tick, on_done):
        self.timer_id = timer_id
        self.seconds = seconds
        self.remaining = seconds
        self.on_tick = on_tick
        self.on_done = on_done
        self._task = None
        self.active = False

    def start(self, page):
        if self._task and not self._task.done():
            return
        self.active = True
        self._task = page.run_task(self._run)

    def cancel(self):
        self.active = False
        if self._task:
            try:
                self._task.cancel()
            except Exception:
                pass

    async def _run(self):
        while self.remaining > 0 and self.active:
            self.on_tick(self.timer_id, self.remaining)
            await asyncio.sleep(1)
            self.remaining -= 1
        if self.active:
            self.on_done(self.timer_id)
            self.active = False

    def format_remaining(self):
        m, s = divmod(self.remaining, 60)
        return f"{m:02d}:{s:02d}"


class TimerEngine:
    def __init__(self):
        self._timers = {}

    def start_timer(self, timer_id, seconds, on_tick, on_done, page):
        if timer_id in self._timers:
            self._timers[timer_id].cancel()
        t = TimerInstance(timer_id, seconds, on_tick, on_done)
        self._timers[timer_id] = t
        t.start(page)
        return t

    def cancel_timer(self, timer_id):
        if timer_id in self._timers:
            self._timers[timer_id].cancel()
            del self._timers[timer_id]

    def cancel_all(self):
        for t in self._timers.values():
            t.cancel()
        self._timers.clear()

    def get(self, timer_id):
        return self._timers.get(timer_id)
