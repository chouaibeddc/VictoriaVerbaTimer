import json
import os
import sys
from tkinter import *
from TimerButton import TimerButton, POI_TIMER

# ── Directory resolution — works for both .py and PyInstaller .exe ────────────
#
# When frozen by PyInstaller:
#   - __file__ points into a temp extraction folder (_MEIPASS)  ← WRONG
#   - sys.executable points to the actual .exe file             ← RIGHT
#
# When running as a plain .py script:
#   - sys.frozen is not set
#   - __file__ is the correct source path
#
if getattr(sys, "frozen", False):
    # Running as a compiled .exe — config files live next to the .exe
    _DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    # Running as a .py script — config files live next to app.py
    _DIR = os.path.dirname(os.path.abspath(__file__))


# ── Palette ───────────────────────────────────────────────────────────────────

DEFAULT_THEME = {
    "app_bg":            "#0a1209",
    "panel_bg":          "#0f1a14",
    "divider":           "#1a3020",
    "gold":              "#E6BC00",
    "gold_dim":          "#7a5e00",
    "text_dim":          "#3a6045",
    "text_mid":          "#7aaa85",
    "text_hi":           "#dff5e3",
    "gov_color":         "#4ade80",
    "opp_color":         "#f87171",
    "card_bg":           "#0f1a14",
    "card_bg_hover":     "#141f18",
    "card_border_idle":  "#1e3028",
    "dot_idle":          "#2a4030",
    "dot_run":           "#4ade80",
    "border_run":        "#4ade80",
    "border_over":       "#facc15",
    "time_color":        "#ffffff",
    "time_over":         "#E6BC00",
}

DEFAULT_CONFIG = {
    "app": {
        "title":      "Victoria Verba Timer V1.0",
        "subtitle":   "3rd Edition  ·  Official Debate Timer  ·  Ensam Express",
        "version":    "1.0",
        "fullscreen": True,
    },
    "theme": "theme_dark.json",
    "limits": {
        "speech":     "04:00",
        "rep_speech": "02:00",
        "poi":        "00:15",
        "tbpoi":      "00:20",
        "apoi":       "00:30",
    },
    "keys": {
        "Gov1": "A", "Gov2": "Z", "Gov3": "E", "GovRep": "R",
        "Opp1": "Q", "Opp2": "S", "Opp3": "D", "OppRep": "F",
        "POI":  "U", "TBPOI": "I", "APOI": "N",
    },
    "hotkeys": {
        "reset_all":         "Control-x",
        "quit":              "Control-F4",
        "toggle_fullscreen": "Escape",
    },
}


# ── JSON helpers ──────────────────────────────────────────────────────────────

def _strip_comments(d):
    """Drop keys starting with '_' (used as JSON comments)."""
    if isinstance(d, dict):
        return {k: _strip_comments(v) for k, v in d.items()
                if not k.startswith("_")}
    return d


def _deep_merge(base, override):
    """Merge override into base recursively; returns a new dict."""
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def _load_json_file(filename, default, label):
    """
    Load a JSON file from _DIR (same folder as app.py).
    Always prints which path is tried so problems are obvious.
    Falls back to `default` on any error.
    """
    path = os.path.join(_DIR, filename)
    print(f"[{label}] Looking for: {path}")

    if not os.path.exists(path):
        print(f"[{label}] NOT FOUND — using built-in defaults.")
        return dict(default)

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        data   = _strip_comments(raw)
        result = _deep_merge(default, data)
        print(f"[{label}] OK — loaded {len(data)} top-level keys.")
        return result
    except json.JSONDecodeError as e:
        print(f"[{label}] JSON ERROR: {e}")
        print(f"[{label}] Using built-in defaults.")
        return dict(default)


def load_config():
    return _load_json_file("config.json", DEFAULT_CONFIG, "Config")


def load_theme(filename):
    return _load_json_file(filename, DEFAULT_THEME, "Theme")


# ── App ───────────────────────────────────────────────────────────────────────

class App(Tk):
    def __init__(self):
        super().__init__()

        # Load config first, then the theme it points to
        self.cfg = load_config()
        self.th  = load_theme(self.cfg.get("theme", "theme_dark.json"))

        # Debug dump so the user can verify in the console
        print("\n── Active configuration ─────────────────────────────")
        print(f"  limits  : {self.cfg['limits']}")
        print(f"  keys    : {self.cfg['keys']}")
        print(f"  hotkeys : {self.cfg['hotkeys']}")
        print(f"  theme   : {self.cfg.get('theme')}")
        print("─────────────────────────────────────────────────────\n")

        app_cfg = self.cfg["app"]
        lim     = self.cfg["limits"]

        # Window
        self.title(app_cfg["title"])
        if app_cfg.get("fullscreen", True):
            self.attributes("-fullscreen", True)
        self.configure(bg=self.th["app_bg"])

        # Limits
        self.SPEECH_LIMIT     = lim["speech"]
        self.REP_SPEECH_LIMIT = lim["rep_speech"]
        self.POI_LIMIT        = lim["poi"]
        self.TBPOI_LIMIT      = lim["tbpoi"]
        self.APOI_LIMIT       = lim["apoi"]
        self.KEY_MAPPING      = self.cfg["keys"]

        # Build UI
        self._build_ui(app_cfg)
        img = PhotoImage(file="ico.png")
        self.iconphoto(False, img)

        # Global hotkeys
        hk = self.cfg["hotkeys"]
        self.bind(f"<{hk['toggle_fullscreen']}>",
                  lambda e: self.attributes("-fullscreen",
                                            not self.attributes("-fullscreen")))
        self.bind(f"<{hk['reset_all']}>", lambda e: self.reset_all())
        self.bind(f"<{hk['quit']}>",      lambda e: self.quit_app())

    # ── Actions ───────────────────────────────────────────────────────────────

    def quit_app(self):
        self.destroy()

    def reset_all(self):
        for t in self.timers.values():
            t.reset()
        for t in self.poi_timers.values():
            t.reset()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self, app_cfg):
        th = self.th

        # Header
        header = Frame(self, bg=th["app_bg"])
        header.pack(fill="x", pady=(24, 0))
        Label(header, text="VICTORIA VERBA",
              font=("Consolas", 32, "bold"),
              fg=th["gold"], bg=th["app_bg"]).pack()
        Label(header, text=app_cfg.get("subtitle", ""),
              font=("Consolas", 11),
              fg=th["gold_dim"], bg=th["app_bg"]).pack(pady=(2, 14))

        Frame(self, bg=th["gold"],    height=2).pack(fill="x")
        Frame(self, bg=th["app_bg"],  height=6).pack(fill="x")

        # Body
        body = Frame(self, bg=th["app_bg"])
        body.pack(expand=True, fill="both", padx=30)

        left = Frame(body, bg=th["panel_bg"])
        left.pack(side="left", expand=True, fill="both", padx=(0, 10), pady=10)
        self._build_speeches(left)

        right = Frame(body, bg=th["panel_bg"])
        right.pack(side="right", fill="y", padx=(10, 0), pady=10)
        self._build_poi(right)

        # Footer
        hk = self.cfg["hotkeys"]
        Frame(self, bg=th["gold"], height=1).pack(fill="x")
        footer = Frame(self, bg=th["app_bg"], height=36)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        hint = (f"[{hk['toggle_fullscreen']}] fullscreen   "
                f"[{hk['reset_all']}] reset all   "
                f"[{hk['quit']}] quit")
        Label(footer, text=hint, font=("Consolas", 9),
              fg=th["text_dim"], bg=th["app_bg"]).pack(side="left", padx=20, pady=8)
        Label(footer,
              text=f"Victoria Verba Timer V{app_cfg.get('version', '1.0')}",
              font=("Consolas", 9),
              fg=th["text_dim"], bg=th["app_bg"]).pack(side="right", padx=20, pady=8)

    def _build_speeches(self, parent):
        th = self.th
        Label(parent, text="SPEECHES", font=("Consolas", 12, "bold"),
              fg=th["text_mid"], bg=th["panel_bg"]).pack(pady=(14, 0))

        grid = Frame(parent, bg=th["panel_bg"])
        grid.pack(expand=True)

        self.timers = {}

        for ci, lbl in enumerate(["Speaker 1", "Speaker 2", "Speaker 3", "Reply"]):
            Label(grid, text=lbl, font=("Consolas", 9),
                  fg=th["text_dim"], bg=th["panel_bg"]).grid(
                      row=0, column=ci, padx=12, pady=(10, 2))

        for ri, (eq, color) in enumerate([("Gov", th["gov_color"]),
                                           ("Opp", th["opp_color"])]):
            Label(grid, text=eq.upper(), font=("Consolas", 10, "bold"),
                  fg=color, bg=th["panel_bg"]).grid(
                      row=ri*2+1, column=0, columnspan=4,
                      sticky="w", padx=14, pady=(8, 0))

            for ci, suffix in enumerate(["1", "2", "3", "Rep"]):
                name = eq + suffix
                lim  = self.REP_SPEECH_LIMIT if suffix == "Rep" else self.SPEECH_LIMIT
                t = TimerButton(grid, title=name,
                                key=self.KEY_MAPPING[name],
                                limit=lim, theme=th)
                t.grid(row=ri*2+2, column=ci, padx=10, pady=6)
                self.timers[name] = t

    def _build_poi(self, parent):
        th = self.th
        Label(parent, text="POI TIMERS", font=("Consolas", 12, "bold"),
              fg=th["text_mid"], bg=th["panel_bg"]).pack(pady=(14, 6))

        poi_frame = Frame(parent, bg=th["panel_bg"])
        poi_frame.pack(expand=True)

        self.poi_timers = {}
        poi_defs = [
            ("POI",   self.KEY_MAPPING["POI"],   self.POI_LIMIT),
            ("TBPOI", self.KEY_MAPPING["TBPOI"], self.TBPOI_LIMIT),
            ("APOI",  self.KEY_MAPPING["APOI"],  self.APOI_LIMIT),
        ]

        for row, (name, key, lim) in enumerate(poi_defs):
            Label(poi_frame, text=name, font=("Consolas", 9, "bold"),
                  fg=th["text_dim"], bg=th["panel_bg"]).grid(
                      row=row*2, column=0, sticky="w", padx=16, pady=(8, 0))
            t = TimerButton(poi_frame, title=name, key=key,
                            limit=lim, type=POI_TIMER, theme=th)
            t.grid(row=row*2+1, column=0, padx=16, pady=4)
            self.poi_timers[name] = t

        Frame(poi_frame, bg=th["divider"], height=1).grid(
            row=7, column=0, sticky="ew", padx=16, pady=12)

        hk_label  = self.cfg["hotkeys"]["reset_all"]
        reset_btn = Label(poi_frame,
                          text=f"↺  Reset All  [{hk_label}]",
                          font=("Consolas", 10, "bold"),
                          fg=th["text_dim"], bg=th["panel_bg"],
                          cursor="hand2", padx=12, pady=6)
        reset_btn.grid(row=8, column=0, padx=16, pady=(0, 16))
        reset_btn.bind("<Button-1>", lambda e: self.reset_all())
        reset_btn.bind("<Enter>",    lambda e: reset_btn.config(fg=th["gold"]))
        reset_btn.bind("<Leave>",    lambda e: reset_btn.config(fg=th["text_dim"]))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    App().mainloop()
