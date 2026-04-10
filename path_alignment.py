import cv2
import numpy as np


class PathAlignmentEngine:
    def __init__(self):
        self.offset_ratio_threshold = 0.08
        self.min_lines = 2

    def detect(self, frame_rgb):
        gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 60, 150)

        h, w = edges.shape[:2]
        roi = np.zeros_like(edges)
        roi[int(h * 0.45) :, :] = 255
        edges = cv2.bitwise_and(edges, roi)

        lines = cv2.HoughLinesP(
            edges,
            1,
            np.pi / 180,
            threshold=60,
            minLineLength=int(w * 0.12),
            maxLineGap=int(w * 0.04),
        )

        if lines is None or len(lines) < self.min_lines:
            return None, None

        left = []
        right = []
        for x1, y1, x2, y2 in lines.reshape(-1, 4):
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0:
                continue
            slope = dy / dx
            if abs(slope) < 0.35:
                continue
            if slope < 0:
                left.append((x1, y1, x2, y2))
            else:
                right.append((x1, y1, x2, y2))

        left_line = self._fit_line(left, h)
        right_line = self._fit_line(right, h)

        if left_line is None and right_line is None:
            return None, None

        y_eval = int(h * 0.85)
        if left_line is not None and right_line is not None:
            corridor_center_x = (left_line["x_at"](y_eval) + right_line["x_at"](y_eval)) / 2.0
        elif left_line is not None:
            corridor_center_x = left_line["x_at"](y_eval) + w * 0.28
        else:
            corridor_center_x = right_line["x_at"](y_eval) - w * 0.28

        offset = corridor_center_x - (w / 2.0)
        if abs(offset) < w * self.offset_ratio_threshold:
            return None, self._debug_lines(left_line, right_line)

        if offset < 0:
            return "Veering Left", self._debug_lines(left_line, right_line)
        return "Veering Right", self._debug_lines(left_line, right_line)

    def _fit_line(self, segments, h):
        if not segments:
            return None
        xs = []
        ys = []
        for x1, y1, x2, y2 in segments:
            xs.extend([x1, x2])
            ys.extend([y1, y2])
        if len(xs) < 4:
            return None
        m, b = np.polyfit(ys, xs, 1)
        if abs(m) < 1e-3:
            return None

        def x_at(y):
            return m * y + b

        y1 = int(h * 0.55)
        y2 = int(h * 0.95)
        return {"p1": (int(x_at(y1)), y1), "p2": (int(x_at(y2)), y2), "x_at": x_at}

    def _debug_lines(self, left_line, right_line):
        out = []
        if left_line is not None:
            out.append((left_line["p1"], left_line["p2"]))
        if right_line is not None:
            out.append((right_line["p1"], right_line["p2"]))
        return out if out else None
