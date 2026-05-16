import os
import sys
from tkinter import *

POI_TIMER = "POI_TIMER"

# Works for both .py and PyInstaller .exe
if getattr(sys, "frozen", False):
    _DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    _DIR = os.path.dirname(os.path.abspath(__file__))

# ── Default theme (dark) ──────────────────────────────────────────────────────
_DEFAULT_THEME = {
    "card_bg":           "#0f1a14",
    "card_bg_hover":     "#141f18",
    "card_border_idle":  "#1e3028",
    "dot_idle":          "#2a4030",
    "dot_run":           "#4ade80",
    "border_run":        "#4ade80",
    "border_over":       "#facc15",
    "time_color":        "#ffffff",
    "time_over":         "#E6BC00",
    "text_dim":          "#4a7a5a",
    "text_mid":          "#8aaa90",
    "text_hi":           "#dff5e3",
    "gold":              "#E6BC00",
}


class TimerButton(Frame):
    """
    A clickable / key-triggered timer card.

    Parameters
    ----------
    master    : parent widget
    title     : display title string
    key       : single keyboard character to toggle
    limit     : "MM:SS" string
    type      : POI_TIMER for POI behaviour, None for standard
    theme     : dict of colour keys (merged over _DEFAULT_THEME)
    on_start  : callable()           fired when timer starts
    on_tick   : callable(elapsed_s)  fired every second while running
    on_end    : callable()           fired when timer ends
    """

    def __init__(self, master, title, key, limit,
                 type=None, theme=None,
                 on_start=None, on_tick=None, on_end=None, **kwargs):

        t = dict(_DEFAULT_THEME)
        if theme:
            t.update(theme)
        self._t = t

        super().__init__(master, bg=t["card_bg"], **kwargs)

        self._type      = type
        self._key       = key
        self._limit_sec = self._parse_time(limit)
        self._elapsed   = 0
        self._running   = False
        self._job       = None
        self._over      = False

        self._on_start = on_start
        self._on_tick  = on_tick
        self._on_end   = on_end

        # ── Size ─────────────────────────────────────────────────────────────
        if type == POI_TIMER:
            W, H, big_fs, title_fs = 192, 160, 28, 13
        else:
            W, H, big_fs, title_fs = 258, 218, 36, 15

        self.config(width=W, height=H)
        self.pack_propagate(False)

        bg = t["card_bg"]

        # Canvas backdrop
        self._canvas = Canvas(self, bg=bg, highlightthickness=2,
                              highlightbackground=t["card_border_idle"],
                              cursor="hand2")
        self._canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Inner content frame
        inner = Frame(self, bg=bg, cursor="hand2")
        inner.place(x=12, y=10, width=W - 24, height=H - 20)

        self._title_lbl = Label(inner, text=title,
                                font=("Consolas", title_fs, "bold"),
                                fg=t["text_hi"], bg=bg, anchor="w")
        self._title_lbl.place(x=0, y=0)

        self._dot = Label(inner, text="●", font=("Arial", 9),
                          fg=t["dot_idle"], bg=bg)
        self._dot.place(relx=1, x=-2, y=2, anchor="ne")

        self._time_lbl = Label(inner, text="00:00",
                               font=("Consolas", big_fs, "bold"),
                               fg=t["time_color"], bg=bg)
        self._time_lbl.place(relx=0.5, rely=0.5, anchor="center")

        bot_y = H - 20 - 22

        self._limit_lbl = Label(inner, text=f"Limit  {limit}",
                                font=("Consolas", 8),
                                fg=t["text_dim"], bg=bg, anchor="w")
        self._limit_lbl.place(x=0, y=bot_y)

        self._reset_btn = Label(inner, text="↺",
                                font=("Arial", 11), fg=t["text_dim"], bg=bg,
                                cursor="hand2")
        self._reset_btn.place(relx=0.5, y=bot_y - 1, anchor="n")

        self._key_lbl = Label(inner, text=f"[{key}]",
                              font=("Consolas", 8, "bold"),
                              fg=t["text_mid"], bg=bg, anchor="e")
        self._key_lbl.place(relx=1, x=0, y=bot_y, anchor="ne")

        # Bindings
        clickable = (self, inner, self._canvas,
                     self._title_lbl, self._time_lbl,
                     self._limit_lbl, self._key_lbl, self._dot)
        for w in clickable:
            w.bind("<Button-1>", self._on_click)
            w.bind("<Enter>",    self._on_enter)
            w.bind("<Leave>",    self._on_leave)

        self._reset_btn.bind("<Button-1>", self._on_reset_click)

        self.after(100, self._bind_key)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _parse_time(self, s):
        try:
            m, sec = s.strip().split(":")
            return int(m) * 60 + int(sec)
        except Exception:
            return 0

    def _format_time(self, sec):
        m, s = divmod(sec, 60)
        return f"{m:02d}:{s:02d}"

    def _set_border(self, color):
        self._canvas.config(highlightbackground=color)

    def _bind_key(self):
        root = self.winfo_toplevel()
        root.bind(f"<{self._key}>",         lambda e: self._toggle(), add="+")
        root.bind(f"<{self._key.lower()}>", lambda e: self._toggle(), add="+")

    # ── Hover ─────────────────────────────────────────────────────────────────

    def _on_enter(self, _=None):
        if not self._running:
            self._canvas.config(bg=self._t["card_bg_hover"])

    def _on_leave(self, _=None):
        if not self._running:
            self._canvas.config(bg=self._t["card_bg"])

    # ── Toggle ────────────────────────────────────────────────────────────────

    def _on_click(self, event=None):
        self._toggle()

    def _toggle(self):
        if self._running:
            if self._type == POI_TIMER:
                self._hard_stop_reset()
            else:
                self._stop(auto=False)
        else:
            self._start()

    def _start(self):
        if self._running:
            return
        self._running = True
        self._over    = False
        self._dot.config(fg=self._t["dot_run"])
        self._set_border(self._t["border_run"])
        self._canvas.config(bg=self._t["card_bg"])
        if self._on_start:
            self._on_start()
        self._tick()

    def _stop(self, auto=False):
        self._running = False
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        self._dot.config(fg=self._t["dot_idle"])
        self._set_border(self._t["card_border_idle"])
        self._canvas.config(bg=self._t["card_bg"])
        self._time_lbl.config(fg=self._t["time_color"])
        if self._on_end:
            self._on_end()
        if auto and self._type == POI_TIMER:
            self.after(350, self._silent_reset)

    def _hard_stop_reset(self):
        self._running = False
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        self._dot.config(fg=self._t["dot_idle"])
        self._set_border(self._t["card_border_idle"])
        self._canvas.config(bg=self._t["card_bg"])
        self._time_lbl.config(fg=self._t["time_color"])
        self._silent_reset()

    def _tick(self):
        if not self._running:
            return
        self._elapsed += 1
        self._time_lbl.config(text=self._format_time(self._elapsed))
        if self._on_tick:
            self._on_tick(self._elapsed)

        if self._type == POI_TIMER and self._elapsed >= self._limit_sec:
            self._stop(auto=True)
            return

        if self._type != POI_TIMER and self._elapsed >= self._limit_sec and not self._over:
            self._over = True
            self._time_lbl.config(fg=self._t["time_over"])
            self._set_border(self._t["border_over"])

        self._job = self.after(1000, self._tick)

    # ── Reset ─────────────────────────────────────────────────────────────────

    def _on_reset_click(self, event=None):
        self.after(1, self.reset)
        return "break"

    def reset(self):
        self._running = False
        if self._job:
            self.after_cancel(self._job)
            self._job = None
        self._over    = False
        self._elapsed = 0
        self._time_lbl.config(text="00:00", fg=self._t["time_color"])
        self._dot.config(fg=self._t["dot_idle"])
        self._set_border(self._t["card_border_idle"])
        self._canvas.config(bg=self._t["card_bg"])

    def _silent_reset(self):
        self._elapsed = 0
        self._time_lbl.config(text="00:00", fg=self._t["time_color"])
