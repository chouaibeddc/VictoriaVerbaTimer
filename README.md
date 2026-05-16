# VictoriaVerbaTimer ⏳

**VictoriaVerbaTimer** is a lightweight, high-precision desktop application engineered for **World Schools Debate Championship (WSDC)** timekeepers. Built completely from scratch with Python and Tkinter, it provides a zero-dependency, zero-lag interface that transforms your keyboard into a rapid-response timing console.

Developed with a clean layout and distraction-free visual design, it allows tournament organizers and timekeepers to manage complex speech bounds and Points of Information (POIs) entirely blind-touch—no mouse tracking required.

---

## ✨ Key Features

* **Complete WSDC Layout:** Tracks all standard speeches: **Speaker 1, 2, 3, and Reply** rounds for both the Government (`GOV`) and Opposition (`OPP`) teams.
* **Blind-Touch Keyboard Mapping:** Every single speech card and POI timer is bound to a dedicated keyboard key for instantaneous control.
* **Smart POI Management with Auto-Reset:** Contains three custom POI tracking modes (`POI`, `TBPOI`, and `APOI`). Upon expiration, POI timers automatically flash and undergo a silent reset to instantly clear the board for the next floor intervention.
* **Fully Extensible Theme Engine:** Comes with fully native **Dark Theme (Default)** and **Light Theme** editions via modular, comment-safe JSON configuration.
* **Adaptive Color Indicators:** Dynamic visual signaling that transitions border and font colors automatically when a speaker enters overtime.
* **Zero Dependencies:** Relies purely on Python's built-in standard library wrapper (`tkinter`), ensuring maximum cross-platform portability without bloated third-party framework setups.

---

## ⌨️ Control Console Mapping

The application uses standard hotkeys mapped out for speed. The default bindings match an **AZERTY/QWERTY-friendly** structural layout:

### 🎤 Speech Timers
| Position | Key Bind | Default Limit | Team Color Indicator |
| :--- | :---: | :---: | :--- |
| **Gov 1** | `A` | 05:00 | 🟢 Green |
| **Gov 2** | `Z` | 05:00 | 🟢 Green |
| **Gov 3** | `E` | 05:00 | 🟢 Green |
| **Gov Reply** | `R` | 02:00 | 🟢 Green |
| **Opp 1** | `Q` | 05:00 | 🔴 Red |
| **Opp 2** | `S` | 05:00 | 🔴 Red |
| **Opp 3** | `D` | 05:00 | 🔴 Red |
| **Opp Reply** | `F` | 02:00 | 🔴 Red |

### ⏱️ POI Timers (Auto-Resetting)
| Type | Key Bind | Default Limit | Purpose |
| :--- | :---: | :---: | :--- |
| **POI** | `U` | 00:15 | Standard Points of Information |
| **TBPOI** | `J` | 00:20 | Time Between Bound POI |
| **APOI** | `N` | 00:30 | Accepted Extended POI |

### 🛠 Global Utility Hotkeys
* `Escape` — Toggle Fullscreen Mode
* `Control + X` — Global Reset All (Clears all active clocks instantly back to `00:00`)
* `Control + F4` — Fast Quit Application

---

## 📂 Project Structure

Ensure your local directory maintains the following directory structure to guarantee proper configuration and assets mapping at run time:

```text
VictoriaVerbaTimer/
├── app.py             # Main entry point and core UI Layout loop
├── TimerButton.py     # Clickable/Key-triggered timing engine module
├── config.json        # Main settings, time limits, and input mapping
├── theme_dark.json    # High-contrast default dark theme profile
├── theme_light.json   # Clean ambient lighting theme profile
├── ico.png            # Asset window icon
└── ico.ico            # Main runtime desktop application icon
