import tkinter as tk
from tkinter import ttk, messagebox
import time
import math
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    HAS_ZONEINFO = True
except ImportError:
    HAS_ZONEINFO = False

FALLBACK_OFFSETS = {
    "Asia/Tehran": 3.5, "Europe/London": 0, "America/New_York": -5,
    "Asia/Tokyo": 9, "Asia/Dubai": 4, "Europe/Paris": 1,
    "Australia/Sydney": 10, "America/Los_Angeles": -8,
    "Europe/Istanbul": 3, "Europe/Moscow": 3, "Asia/Kolkata": 5.5,
    "America/Sao_Paulo": -3, "Asia/Shanghai": 8, "Asia/Singapore": 8,
    "Europe/Berlin": 1, "Africa/Cairo": 2, "America/Chicago": -6,
    "America/Toronto": -5,
}


def get_time_in_zone(tz_name):
    if HAS_ZONEINFO:
        try:
            return datetime.now(ZoneInfo(tz_name))
        except Exception:
            pass
    offset = FALLBACK_OFFSETS.get(tz_name, 0)
    tz = timezone(timedelta(hours=offset))
    return datetime.now(tz)


BG = "#0a0a0c"
CARD_BG = "#16161a"
HEADER_BG = "#1e1e24"
BORDER = "#2a2a34"
TEXT = "#ffffff"
TEXT_DIM = "#8e8e93"
BLUE = "#0a84ff"
GREEN = "#30d158"
ORANGE = "#ff9f0a"
RED = "#ff453a"
CYAN = "#64d2ff"


class AnimButton(tk.Frame):
    """Simple animated button using Frame + Label instead of Canvas.
    This avoids all the Tcl ID issues we were having."""

    def __init__(self, parent, text, color, command,
                 width=90, height=32, bg=None):
        if bg is None:
            try:
                bg = parent.cget("bg")
            except Exception:
                bg = CARD_BG

        super().__init__(parent, bg=bg, width=width, height=height,
                         bd=0, highlightthickness=0)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.text = text
        self.color = color
        self.command = command
        self.hover = False
        self._alive = True
        self._bg = bg

        self.label = tk.Label(
            self, text=text, bg=color, fg="white",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2"
        )
        self.label.pack(fill="both", expand=True, padx=2, pady=2)

        for widget in (self, self.label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<ButtonRelease-1>", self._on_release)

        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, e):
        if e.widget is self:
            self._alive = False

    def _lighten(self, color, amount=30):
        try:
            h = color.lstrip("#")
            r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
            return f"#{min(255, r+amount):02x}{min(255, g+amount):02x}{min(255, b+amount):02x}"
        except Exception:
            return color

    def _on_enter(self, e):
        if not self._alive:
            return
        self.hover = True
        try:
            self.label.config(bg=self._lighten(self.color, 30))
        except Exception:
            pass

    def _on_leave(self, e):
        if not self._alive:
            return
        self.hover = False
        try:
            self.label.config(bg=self.color)
        except Exception:
            pass

    def _on_click(self, e):
        if not self._alive:
            return
        try:
            self.label.config(relief="sunken")
        except Exception:
            pass

    def _on_release(self, e):
        if not self._alive:
            return
        try:
            self.label.config(relief="flat")
        except Exception:
            pass
        if self.command:
            try:
                self.command()
            except Exception:
                pass

    def set_text(self, text):
        self.text = text
        if not self._alive:
            return
        try:
            self.label.config(text=text)
        except Exception:
            pass

    def set_color(self, color):
        self.color = color
        if not self._alive:
            return
        try:
            self.label.config(bg=color)
        except Exception:
            pass


class ClockWidget(tk.Frame):
    def __init__(self, parent, title, icon, on_delete, accent=BLUE):
        super().__init__(parent, bg=CARD_BG, bd=0, highlightthickness=0)
        self.on_delete = on_delete
        self.accent = accent
        self._alive = True

        self.outer = tk.Frame(self, bg=accent, bd=0)
        self.outer.pack(fill="both", expand=True, padx=1, pady=1)

        self.inner = tk.Frame(self.outer, bg=CARD_BG)
        self.inner.pack(fill="both", expand=True)

        header = tk.Frame(self.inner, bg=HEADER_BG)
        header.pack(fill="x")

        tk.Frame(header, bg=accent, width=4).pack(side="left", fill="y")

        self.title_label = tk.Label(
            header, text=f"{icon}  {title}", bg=HEADER_BG, fg=TEXT,
            font=("Segoe UI", 11, "bold"), anchor="w", padx=10, pady=8
        )
        self.title_label.pack(side="left")

        close_btn = tk.Label(
            header, text="✕", bg=HEADER_BG, fg=TEXT_DIM,
            font=("Segoe UI", 11, "bold"), padx=12, cursor="hand2"
        )
        close_btn.pack(side="right")
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=RED))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=TEXT_DIM))
        close_btn.bind("<Button-1>", lambda e: self._do_delete())

        self.body = tk.Frame(self.inner, bg=CARD_BG, padx=15, pady=15)
        self.body.pack(fill="both", expand=True)

    def _do_delete(self):
        self._alive = False
        try:
            self.on_delete(self)
        except Exception:
            pass

    def update(self):
        pass


class WorldClock(ClockWidget):
    def __init__(self, parent, city, timezone_name, on_delete):
        super().__init__(parent, city, "🌍", on_delete, accent=BLUE)
        self.timezone_name = timezone_name

        self.clock_canvas = tk.Canvas(
            self.body, width=90, height=90, bg=CARD_BG, highlightthickness=0
        )
        self.clock_canvas.pack(side="left", padx=(0, 15))

        right = tk.Frame(self.body, bg=CARD_BG)
        right.pack(side="left", fill="both", expand=True)

        self.time_label = tk.Label(
            right, text="", bg=CARD_BG, fg=TEXT,
            font=("Consolas", 26, "bold")
        )
        self.time_label.pack(anchor="w")

        self.date_label = tk.Label(
            right, text="", bg=CARD_BG, fg=TEXT_DIM,
            font=("Segoe UI", 9)
        )
        self.date_label.pack(anchor="w")

        self.offset_label = tk.Label(
            right, text="", bg=CARD_BG, fg=CYAN,
            font=("Segoe UI", 8, "bold")
        )
        self.offset_label.pack(anchor="w", pady=(2, 0))

    def _draw_analog(self, now):
        try:
            c = self.clock_canvas
            c.delete("all")
            cx, cy, r = 45, 45, 38

            c.create_oval(cx-r, cy-r, cx+r, cy+r,
                          outline=BORDER, width=2)

            for i in range(12):
                angle = math.radians(i * 30 - 90)
                x1 = cx + (r-5) * math.cos(angle)
                y1 = cy + (r-5) * math.sin(angle)
                x2 = cx + r * math.cos(angle)
                y2 = cy + r * math.sin(angle)
                c.create_line(x1, y1, x2, y2, fill=TEXT_DIM, width=1)

            h_ang = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)
            m_ang = math.radians(now.minute * 6 + now.second * 0.1 - 90)
            s_ang = math.radians(now.second * 6 - 90)

            c.create_line(cx, cy, cx + (r-18)*math.cos(h_ang),
                          cy + (r-18)*math.sin(h_ang), fill=TEXT, width=3,
                          capstyle="round")
            c.create_line(cx, cy, cx + (r-12)*math.cos(m_ang),
                          cy + (r-12)*math.sin(m_ang), fill=TEXT, width=2,
                          capstyle="round")
            c.create_line(cx, cy, cx + (r-8)*math.cos(s_ang),
                          cy + (r-8)*math.sin(s_ang), fill=self.accent, width=1)

            c.create_oval(cx-3, cy-3, cx+3, cy+3, fill=self.accent, outline="")
        except Exception:
            pass

    def update(self):
        if not self._alive:
            return
        try:
            now = get_time_in_zone(self.timezone_name)
            self.time_label.config(text=now.strftime("%H:%M:%S"))
            self.date_label.config(text=now.strftime("%A, %B %d, %Y"))
            offset = now.utcoffset()
            if offset is not None:
                total_min = int(offset.total_seconds() // 60)
                sign = "+" if total_min >= 0 else "-"
                total_min = abs(total_min)
                h, m = divmod(total_min, 60)
                self.offset_label.config(text=f"UTC{sign}{h:02d}:{m:02d}")
            self._draw_analog(now)
        except tk.TclError:
            self._alive = False
        except Exception:
            pass


class Stopwatch(ClockWidget):
    def __init__(self, parent, on_delete):
        super().__init__(parent, "Stopwatch", "⏱", on_delete, accent=GREEN)
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.laps = []
        self.pulse = 0

        self.time_label = tk.Label(
            self.body, text="00:00:00.00", bg=CARD_BG, fg=TEXT,
            font=("Consolas", 28, "bold")
        )
        self.time_label.pack(pady=(0, 10))

        self.ring_canvas = tk.Canvas(
            self.body, width=60, height=60, bg=CARD_BG, highlightthickness=0
        )
        self.ring_canvas.pack(pady=(0, 10))

        btn_frame = tk.Frame(self.body, bg=CARD_BG)
        btn_frame.pack()

        self.start_btn = AnimButton(btn_frame, "Start", GREEN, self.toggle,
                                     bg=CARD_BG)
        self.start_btn.pack(side="left", padx=3)

        self.lap_btn = AnimButton(btn_frame, "Lap", BLUE, self.add_lap,
                                   bg=CARD_BG)
        self.lap_btn.pack(side="left", padx=3)

        self.reset_btn = AnimButton(btn_frame, "Reset", "#8e8e93", self.reset,
                                     bg=CARD_BG)
        self.reset_btn.pack(side="left", padx=3)

        self.laps_frame = tk.Frame(self.body, bg=CARD_BG)
        self.laps_frame.pack(fill="x", pady=(10, 0))

    def _current_total(self):
        total = self.elapsed
        if self.running:
            total += time.time() - self.start_time
        return total

    def toggle(self):
        if self.running:
            self.elapsed += time.time() - self.start_time
            self.running = False
            self.start_btn.set_text("Resume")
            self.start_btn.set_color(GREEN)
        else:
            self.start_time = time.time()
            self.running = True
            self.start_btn.set_text("Pause")
            self.start_btn.set_color(ORANGE)

    def add_lap(self):
        if self.running or self.elapsed > 0:
            self.laps.append(self._current_total())
            self._refresh_laps()

    def _refresh_laps(self):
        try:
            for w in self.laps_frame.winfo_children():
                w.destroy()
            for i, lap in enumerate(reversed(self.laps[-3:]), 1):
                h = int(lap // 3600)
                m = int((lap % 3600) // 60)
                s = int(lap % 60)
                cs = int((lap * 100) % 100)
                tk.Label(
                    self.laps_frame,
                    text=f"▸ Lap {len(self.laps) - i + 1}:   "
                         f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}",
                    bg=CARD_BG, fg=TEXT_DIM, font=("Consolas", 9)
                ).pack(anchor="w")
        except Exception:
            pass

    def reset(self):
        self.running = False
        self.elapsed = 0
        self.laps = []
        try:
            self.time_label.config(text="00:00:00.00")
        except Exception:
            pass
        self.start_btn.set_text("Start")
        self.start_btn.set_color(GREEN)
        self._refresh_laps()

    def update(self):
        if not self._alive:
            return
        try:
            total = self._current_total()
            h = int(total // 3600)
            m = int((total % 3600) // 60)
            s = int(total % 60)
            cs = int((total * 100) % 100)
            self.time_label.config(text=f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}")

            self.pulse = (self.pulse + 0.15) % (2 * math.pi)
            c = self.ring_canvas
            c.delete("all")
            cx, cy, r = 30, 30, 22

            if self.running:
                start_ang = math.degrees(self.pulse) % 360
                c.create_arc(cx-r, cy-r, cx+r, cy+r,
                             start=start_ang, extent=270,
                             outline=GREEN, width=3, style="arc")
            else:
                c.create_oval(cx-r, cy-r, cx+r, cy+r,
                              outline=BORDER, width=2)
                c.create_oval(cx-4, cy-4, cx+4, cy+4,
                              fill=GREEN, outline="")
        except tk.TclError:
            self._alive = False
        except Exception:
            pass


class TimerWidget(ClockWidget):
    def __init__(self, parent, on_delete):
        super().__init__(parent, "Timer", "⏲", on_delete, accent=ORANGE)
        self.remaining = 0
        self.running = False
        self.last_tick = 0
        self.finished = False
        self.total_seconds = 0

        input_frame = tk.Frame(self.body, bg=CARD_BG)
        input_frame.pack(pady=(0, 10))

        self.h_spin = self._spin(input_frame, "HOURS", 0, 23)
        self.h_spin.pack(side="left", padx=4)
        self.m_spin = self._spin(input_frame, "MINUTES", 0, 59)
        self.m_spin.pack(side="left", padx=4)
        self.s_spin = self._spin(input_frame, "SECONDS", 0, 59)
        self.s_spin.pack(side="left", padx=4)

        self.time_label = tk.Label(
            self.body, text="00:00:00", bg=CARD_BG, fg=TEXT,
            font=("Consolas", 28, "bold")
        )
        self.time_label.pack(pady=8)

        self.progress_canvas = tk.Canvas(
            self.body, height=8, bg=BORDER, highlightthickness=0
        )
        self.progress_canvas.pack(fill="x", pady=(0, 12))
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 8, fill=ORANGE, outline=""
        )
        self.progress_canvas.bind("<Configure>", self._on_resize)

        btn_frame = tk.Frame(self.body, bg=CARD_BG)
        btn_frame.pack()

        self.start_btn = AnimButton(btn_frame, "Start", GREEN, self.toggle,
                                     bg=CARD_BG)
        self.start_btn.pack(side="left", padx=3)

        self.reset_btn = AnimButton(btn_frame, "Reset", "#8e8e93", self.reset,
                                     bg=CARD_BG)
        self.reset_btn.pack(side="left", padx=3)

    def _on_resize(self, event):
        self._update_progress()

    def _spin(self, parent, label, from_, to):
        f = tk.Frame(parent, bg=CARD_BG)
        tk.Label(f, text=label, bg=CARD_BG, fg=TEXT_DIM,
                 font=("Segoe UI", 7, "bold")).pack()
        var = tk.IntVar(value=0)
        sp = tk.Spinbox(
            f, from_=from_, to=to, textvariable=var, width=4,
            bg=HEADER_BG, fg=TEXT, buttonbackground=BORDER,
            font=("Segoe UI", 10, "bold"), bd=0, justify="center",
            insertbackground=TEXT, relief="flat", highlightthickness=0
        )
        sp.pack()
        f.var = var
        return f

    def toggle(self):
        if self.running:
            self.remaining -= (time.time() - self.last_tick)
            self.running = False
            self.start_btn.set_text("Resume")
            self.start_btn.set_color(GREEN)
        else:
            if self.remaining <= 0:
                secs = (self.h_spin.var.get() * 3600 +
                        self.m_spin.var.get() * 60 +
                        self.s_spin.var.get())
                if secs <= 0:
                    messagebox.showwarning("Warning", "Please set a time")
                    return
                self.remaining = secs
                self.total_seconds = secs
            self.last_tick = time.time()
            self.running = True
            self.start_btn.set_text("Pause")
            self.start_btn.set_color(ORANGE)
            self.finished = False

    def reset(self):
        self.running = False
        self.remaining = 0
        self.total_seconds = 0
        self.finished = False
        try:
            self.time_label.config(text="00:00:00", fg=TEXT)
        except Exception:
            pass
        self.start_btn.set_text("Start")
        self.start_btn.set_color(GREEN)
        self._update_progress()

    def update(self):
        if not self._alive:
            return
        try:
            if self.running:
                elapsed = time.time() - self.last_tick
                rem = max(0, self.remaining - elapsed)
                if rem <= 0 and not self.finished:
                    self.finished = True
                    self.running = False
                    self.remaining = 0
                    self.start_btn.set_text("Start")
                    self.start_btn.set_color(GREEN)
                    self._alarm()
            else:
                rem = self.remaining

            h = int(rem // 3600)
            m = int((rem % 3600) // 60)
            s = int(rem % 60)
            self.time_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            self._update_progress()
        except tk.TclError:
            self._alive = False
        except Exception:
            pass

    def _update_progress(self):
        try:
            if self.total_seconds > 0:
                ratio = max(0, min(1, self.remaining / self.total_seconds))
            else:
                ratio = 0
            w = self.progress_canvas.winfo_width()
            self.progress_canvas.coords(self.progress_bar, 0, 0, w * ratio, 8)
        except Exception:
            pass

    def _alarm(self):
        try:
            self.time_label.config(fg=RED)
        except Exception:
            pass
        for i in range(5):
            self.after(i * 400, lambda: self.bell())
        messagebox.showinfo("Timer", "⏰ Time's up!")


class AlarmWidget(ClockWidget):
    def __init__(self, parent, on_delete):
        super().__init__(parent, "Alarm", "⏰", on_delete, accent=RED)
        self.alarm_time = None
        self.triggered = False
        self.blink = 0
        self.snooze_count = 0

        input_frame = tk.Frame(self.body, bg=CARD_BG)
        input_frame.pack(pady=(0, 10))

        now = datetime.now()

        self.h_spin = self._spin(input_frame, "HOUR", 0, 23, now.hour)
        self.h_spin.pack(side="left", padx=4)
        self.m_spin = self._spin(input_frame, "MIN", 0, 59, now.minute)
        self.m_spin.pack(side="left", padx=4)
        self.s_spin = self._spin(input_frame, "SEC", 0, 59, now.second)
        self.s_spin.pack(side="left", padx=4)

        self.status_label = tk.Label(
            self.body, text="No alarm set", bg=CARD_BG, fg=TEXT_DIM,
            font=("Segoe UI", 10)
        )
        self.status_label.pack(pady=(8, 4))

        self.countdown_label = tk.Label(
            self.body, text="--:--:--", bg=CARD_BG, fg=TEXT_DIM,
            font=("Consolas", 24, "bold")
        )
        self.countdown_label.pack(pady=(0, 10))

        btn_frame = tk.Frame(self.body, bg=CARD_BG)
        btn_frame.pack()

        self.set_btn = AnimButton(btn_frame, "Set Alarm", RED, self.set_alarm,
                                   width=100, bg=CARD_BG)
        self.set_btn.pack(side="left", padx=3)

        self.snooze_btn = AnimButton(btn_frame, "Snooze", ORANGE, self.snooze,
                                      width=90, bg=CARD_BG)
        self.snooze_btn.pack(side="left", padx=3)

        self.clear_btn = AnimButton(btn_frame, "Clear", "#8e8e93", self.clear_alarm,
                                     width=80, bg=CARD_BG)
        self.clear_btn.pack(side="left", padx=3)

    def _spin(self, parent, label, from_, to, default):
        f = tk.Frame(parent, bg=CARD_BG)
        tk.Label(f, text=label, bg=CARD_BG, fg=TEXT_DIM,
                 font=("Segoe UI", 7, "bold")).pack()
        var = tk.IntVar(value=default)
        sp = tk.Spinbox(
            f, from_=from_, to=to, textvariable=var, width=4,
            bg=HEADER_BG, fg=TEXT, buttonbackground=BORDER,
            font=("Segoe UI", 10, "bold"), bd=0, justify="center",
            insertbackground=TEXT, relief="flat", highlightthickness=0
        )
        sp.pack()
        f.var = var
        return f

    def set_alarm(self):
        now = datetime.now()
        try:
            target = now.replace(
                hour=self.h_spin.var.get(),
                minute=self.m_spin.var.get(),
                second=self.s_spin.var.get(),
                microsecond=0
            )
        except Exception:
            return

        if target < now:
            target += timedelta(days=1)

        self.alarm_time = target
        self.triggered = False
        self.snooze_count = 0

        day_str = "today" if target.date() == now.date() else "tomorrow"
        self.status_label.config(
            text=f"✓ Alarm set for {target.strftime('%H:%M:%S')} ({day_str})",
            fg=GREEN
        )
        self.countdown_label.config(fg=TEXT)

    def snooze(self):
        if self.alarm_time is None:
            return
        self.alarm_time = datetime.now() + timedelta(minutes=5)
        self.triggered = False
        self.snooze_count += 1
        self.status_label.config(
            text=f"😴 Snoozed for 5 minutes (#{self.snooze_count})",
            fg=ORANGE
        )
        self.countdown_label.config(fg=TEXT)

    def clear_alarm(self):
        self.alarm_time = None
        self.triggered = False
        self.snooze_count = 0
        self.status_label.config(text="No alarm set", fg=TEXT_DIM)
        self.countdown_label.config(text="--:--:--", fg=TEXT_DIM)

    def update(self):
        if not self._alive or self.alarm_time is None:
            return
        try:
            now = datetime.now()
            diff = (self.alarm_time - now).total_seconds()

            if diff <= 0 and not self.triggered:
                self.triggered = True
                self.countdown_label.config(text="00:00:00", fg=RED)
                self.status_label.config(text="🔔  ALARM!  🔔", fg=RED)
                self._alarm()
                return

            if diff > 0:
                h = int(diff // 3600)
                m = int((diff % 3600) // 60)
                s = int(diff % 60)
                self.countdown_label.config(
                    text=f"{h:02d}:{m:02d}:{s:02d}", fg=TEXT
                )
            elif self.triggered:
                self.blink = (self.blink + 1) % 20
                color = RED if self.blink < 10 else ORANGE
                self.status_label.config(fg=color)
        except tk.TclError:
            self._alive = False
        except Exception:
            pass

    def _alarm(self):
        for i in range(8):
            self.after(i * 400, lambda: self.bell())
        messagebox.showinfo("Alarm", "⏰ ALARM! Wake up!")


class ClockApp:
    def __init__(self, root):
        self.root = root
        root.title("🕐 My Clocks")
        root.configure(bg=BG)
        root.geometry("800x650")
        root.minsize(560, 450)

        self.widgets = []
        self._running = True
        self._tick_id = None

        # Top bar
        top = tk.Frame(root, bg=BG, pady=14)
        top.pack(fill="x", padx=20)

        title_frame = tk.Frame(top, bg=BG)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="🕐", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20)).pack(side="left")
        tk.Label(title_frame, text=" My Clocks", bg=BG, fg=TEXT,
                 font=("Segoe UI", 18, "bold")).pack(side="left")

        add_btn = tk.Button(
            top, text="+  Add Widget", command=self.open_add_menu,
            bg=BLUE, fg="white", font=("Segoe UI", 10, "bold"),
            bd=0, padx=18, pady=8, cursor="hand2",
            activebackground="#0066cc", activeforeground="white",
            relief="flat"
        )
        add_btn.pack(side="right")

        container = tk.Frame(root, bg=BG)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=BG)

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scrollable, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>",
                             lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>",
                             lambda e: self.canvas.yview_scroll(1, "units"))

        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.add_world_clock("Asia/Tehran")
        self.add_world_clock("Europe/London")
        self.tick()

    def _on_close(self):
        self._running = False
        if self._tick_id is not None:
            try:
                self.root.after_cancel(self._tick_id)
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def _on_canvas_configure(self, event):
        try:
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        except Exception:
            pass

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def add_widget(self, widget):
        self.widgets.append(widget)
        widget.pack(fill="x", pady=6, padx=4)

    def remove_widget(self, widget):
        if widget in self.widgets:
            self.widgets.remove(widget)
        try:
            widget.pack_forget()
        except Exception:
            pass
        try:
            widget.destroy()
        except Exception:
            pass

    def add_world_clock(self, timezone_name):
        city = timezone_name.split("/")[-1].replace("_", " ")
        w = WorldClock(self.scrollable, city, timezone_name, self.remove_widget)
        self.add_widget(w)

    def add_stopwatch(self):
        w = Stopwatch(self.scrollable, self.remove_widget)
        self.add_widget(w)

    def add_timer(self):
        w = TimerWidget(self.scrollable, self.remove_widget)
        self.add_widget(w)

    def add_alarm(self):
        w = AlarmWidget(self.scrollable, self.remove_widget)
        self.add_widget(w)

    def tick(self):
        if not self._running:
            return

        for w in list(self.widgets):
            try:
                if not w.winfo_exists():
                    if w in self.widgets:
                        self.widgets.remove(w)
                    continue
                w.update()
            except tk.TclError:
                if w in self.widgets:
                    self.widgets.remove(w)
            except Exception:
                pass

        if self._running:
            try:
                self._tick_id = self.root.after(50, self.tick)
            except Exception:
                self._running = False

    def open_add_menu(self):
        menu = tk.Toplevel(self.root)
        menu.title("Add Widget")
        menu.configure(bg=CARD_BG)
        menu.geometry("360x560")
        menu.transient(self.root)

        menu.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 360) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 560) // 2
        menu.geometry(f"+{x}+{y}")

        tk.Label(
            menu, text="What would you like to add?",
            bg=CARD_BG, fg=TEXT,
            font=("Segoe UI", 13, "bold"), pady=16
        ).pack()

        for text, cmd, color in [
            ("⏱   Stopwatch", self._pick_stopwatch, GREEN),
            ("⏲   Timer", self._pick_timer, ORANGE),
            ("⏰   Alarm", self._pick_alarm, RED),
        ]:
            tk.Button(
                menu, text=text,
                command=lambda c=cmd: c(menu),
                bg=HEADER_BG, fg=color, font=("Segoe UI", 12, "bold"),
                bd=0, pady=14, cursor="hand2", anchor="w", padx=20,
                activebackground=BORDER, activeforeground=color,
                relief="flat"
            ).pack(fill="x", padx=20, pady=5)

        tk.Label(
            menu, text="🌍   WORLD CLOCK",
            bg=CARD_BG, fg=TEXT_DIM,
            font=("Segoe UI", 9, "bold"), pady=12
        ).pack()

        list_container = tk.Frame(menu, bg=CARD_BG)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        canvas = tk.Canvas(list_container, bg=CARD_BG, highlightthickness=0)
        sb = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=CARD_BG)

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        cities = [
            ("Tehran", "Asia/Tehran"), ("London", "Europe/London"),
            ("New York", "America/New_York"), ("Tokyo", "Asia/Tokyo"),
            ("Dubai", "Asia/Dubai"), ("Paris", "Europe/Paris"),
            ("Berlin", "Europe/Berlin"), ("Sydney", "Australia/Sydney"),
            ("Los Angeles", "America/Los_Angeles"), ("Chicago", "America/Chicago"),
            ("Toronto", "America/Toronto"), ("Istanbul", "Europe/Istanbul"),
            ("Moscow", "Europe/Moscow"), ("Delhi", "Asia/Kolkata"),
            ("Shanghai", "Asia/Shanghai"), ("Singapore", "Asia/Singapore"),
            ("Cairo", "Africa/Cairo"), ("São Paulo", "America/Sao_Paulo"),
        ]

        for name, tz in cities:
            tk.Button(
                inner, text=name,
                command=lambda t=tz, m=menu: self._pick_city(t, m),
                bg=HEADER_BG, fg=TEXT, font=("Segoe UI", 10),
                bd=0, pady=7, cursor="hand2", anchor="w", padx=14,
                activebackground=BORDER, activeforeground=BLUE,
                relief="flat"
            ).pack(fill="x", pady=2)

    def _pick_stopwatch(self, menu):
        try:
            menu.destroy()
        except Exception:
            pass
        self.add_stopwatch()

    def _pick_timer(self, menu):
        try:
            menu.destroy()
        except Exception:
            pass
        self.add_timer()

    def _pick_alarm(self, menu):
        try:
            menu.destroy()
        except Exception:
            pass
        self.add_alarm()

    def _pick_city(self, tz, menu):
        try:
            menu.destroy()
        except Exception:
            pass
        self.add_world_clock(tz)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClockApp(root)
    root.mainloop()