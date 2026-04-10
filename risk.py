from dataclasses import dataclass
import time


PRIORITY_INFO = 10
PRIORITY_WARNING = 20
PRIORITY_CRITICAL = 30


@dataclass(frozen=True)
class RiskEvent:
    priority: int
    text: str
    interrupt: bool


class RiskArbiter:
    def __init__(self):
        self._last_spoken_priority = None
        self._last_spoken_time = 0.0

    def decide(self, *, motion, alignment, vision, lang):
        now = time.time()

        if motion is not None:
            if "APPROACHING" in motion.upper():
                return RiskEvent(PRIORITY_CRITICAL, self._localize_motion(motion, lang), True)
            interrupt = self._should_interrupt(now, PRIORITY_WARNING)
            return RiskEvent(PRIORITY_WARNING, self._localize_motion(motion, lang), interrupt)

        if alignment is not None:
            interrupt = self._should_interrupt(now, PRIORITY_WARNING)
            return RiskEvent(PRIORITY_WARNING, self._localize_alignment(alignment, lang), interrupt)

        if vision is not None:
            return RiskEvent(PRIORITY_INFO, vision, False)

        return None

    def mark_spoken(self, event):
        self._last_spoken_priority = event.priority
        self._last_spoken_time = time.time()

    def _should_interrupt(self, now, priority):
        if self._last_spoken_priority is None:
            return False
        if priority <= self._last_spoken_priority:
            return False
        return (now - self._last_spoken_time) < 2.0

    def _localize_motion(self, motion, lang):
        if lang == "zh":
            if "APPROACHING" in motion.upper():
                return "快速接近中！"
            if "LEFT" in motion.upper():
                return "左側快速移動"
            if "RIGHT" in motion.upper():
                return "右側快速移動"
            return "動態危險"
        return f"Warning: {motion}"

    def _localize_alignment(self, alignment, lang):
        if lang == "zh":
            if "LEFT" in alignment.upper():
                return "偏右，往左修正"
            if "RIGHT" in alignment.upper():
                return "偏左，往右修正"
            return "路徑結束"
        return alignment
