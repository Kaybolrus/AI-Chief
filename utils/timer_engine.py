import asyncio
from typing import Callable, Optional


class TimerInstance:
    """Один активный таймер."""

    def __init__(
        self,
        timer_id: str,
        seconds: int,
        on_tick: Callable[[str, int], None],   # (timer_id, remaining_sec)
        on_done: Callable[[str], None],         # (timer_id)
    ):
        self.timer_id = timer_id
        self.seconds = seconds
        self.remaining = seconds
        self.on_tick = on_tick
        self.on_done = on_done
        self._task: Optional[asyncio.Task] = None
        self.active = False

    def start(self):
        if self._task and not self._task.done():
            return
        self.active = True
        self._task = asyncio.create_task(self._run())

    def cancel(self):
        self.active = False
        if self._task:
            self._task.cancel()

    async def _run(self):
        while self.remaining > 0 and self.active:
            self.on_tick(self.timer_id, self.remaining)
            await asyncio.sleep(1)
            self.remaining -= 1
        if self.active:
            self.on_done(self.timer_id)
            self.active = False

    def format_remaining(self) -> str:
        m, s = divmod(self.remaining, 60)
        return f"{m:02d}:{s:02d}"


class TimerEngine:
    """
    Менеджер всех активных таймеров.
    Один экземпляр на приложение.
    """

    def __init__(self):
        self._timers: dict[str, TimerInstance] = {}

    def start_timer(
        self,
        timer_id: str,
        seconds: int,
        on_tick: Callable,
        on_done: Callable,
    ) -> TimerInstance:
        # Если таймер с таким id уже есть — останавливаем старый
        if timer_id in self._timers:
            self._timers[timer_id].cancel()

        t = TimerInstance(timer_id, seconds, on_tick, on_done)
        self._timers[timer_id] = t
        t.start()
        return t

    def cancel_timer(self, timer_id: str):
        if timer_id in self._timers:
            self._timers[timer_id].cancel()
            del self._timers[timer_id]

    def cancel_all(self):
        for t in self._timers.values():
            t.cancel()
        self._timers.clear()

    def get(self, timer_id: str) -> Optional[TimerInstance]:
        return self._timers.get(timer_id)
