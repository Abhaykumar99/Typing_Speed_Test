from tkinter import *
from tkinter import font as tkfont
import json
import os
import time
import random

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SCORE_FILE = os.path.join(BASE_DIR, "highscores.json")


# ── Colors ──────────────────────────────────────────────────────────────────
BG      = "#1e1e2e"
CARD    = "#2a2a3e"
ACCENT  = "#89b4fa"
GREEN   = "#a6e3a1"
RED     = "#f38ba8"
YELLOW  = "#f9e2af"
GRAY    = "#585b70"
TEXT    = "#cdd6f4"
FONT    = ("Consolas", 13)
FONT_B  = ("Segoe UI", 12, "bold")
FONT_H  = ("Segoe UI", 20, "bold")

# ── Test Paragraphs ──────────────────────────────────────────────────────────
PARAGRAPHS = [
    "The quick brown fox jumps over the lazy dog near the river bank every single morning.",
    "Python is a high level programming language known for its simplicity and readability.",
    "Practice makes a man perfect and consistency is the key to mastering any new skill.",
    "The sun rises in the east and sets in the west giving us a beautiful orange sky.",
    "Typing fast with accuracy is a very useful skill in the modern digital world today.",
    "Learning to code opens many doors and creates endless opportunities for your career.",
    "Every great journey begins with a single small step taken with courage and ambition.",
    "Hard work and dedication always pay off when you stay focused on your ultimate goal.",
]

# ── High Score Load/Save ─────────────────────────────────────────────────────
def load_best():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE) as f:
            return json.load(f).get("best_wpm", 0)
    return 0

def save_best(wpm):
    with open(SCORE_FILE, "w") as f:
        json.dump({"best_wpm": wpm}, f)


# ── App State ────────────────────────────────────────────────────────────────
class TypingTest:
    def __init__(self):
        self.start_time  = None   # timer tab shuru hoga jab pehla key press hoga
        self.running     = False
        self.best_wpm    = load_best()
        self.target_text = ""
        self.timer_id    = None

    def new_test(self):
        # naya random paragraph choose karo aur state reset karo
        self.target_text = random.choice(PARAGRAPHS)
        self.start_time  = None
        self.running     = False
        if self.timer_id:
            window.after_cancel(self.timer_id)
        self.timer_id = None


app = TypingTest()


def start_new():
    # test reset karo — naya paragraph, input clear, stats reset
    app.new_test()
    input_box.config(state=NORMAL)
    input_box.delete("1.0", END)
    input_box.focus()

    # target text dikhao
    target_box.config(state=NORMAL)
    target_box.delete("1.0", END)
    target_box.insert("1.0", app.target_text)
    target_box.config(state=DISABLED)

    wpm_label.config(   text="WPM: —",      fg=ACCENT)
    acc_label.config(   text="Accuracy: —", fg=ACCENT)
    time_label.config(  text="Time: 0s",    fg=TEXT)
    result_label.config(text="")
    reset_highlights()


def reset_highlights():
    # saare highlights hata do — fresh start
    target_box.config(state=NORMAL)
    target_box.tag_remove("correct", "1.0", END)
    target_box.tag_remove("wrong",   "1.0", END)
    target_box.tag_remove("current", "1.0", END)
    target_box.config(state=DISABLED)


def tick():
    # har second time update karo jab test chal raha ho
    if app.running:
        elapsed = int(time.time() - app.start_time)
        time_label.config(text=f"Time: {elapsed}s")
        app.timer_id = window.after(1000, tick)


def on_key(event=None):
    # user ne type kiya — agar pehla key hai toh timer start karo
    if not app.running and input_box.get("1.0", END).strip():
        app.running    = True
        app.start_time = time.time()
        tick()

    typed  = input_box.get("1.0", END).rstrip("\n")
    target = app.target_text

    # live highlight — sahi letter green, galat red
    target_box.config(state=NORMAL)
    target_box.tag_remove("correct", "1.0", END)
    target_box.tag_remove("wrong",   "1.0", END)
    target_box.tag_remove("current", "1.0", END)

    for i, ch in enumerate(typed):
        pos_start = f"1.{i}"
        pos_end   = f"1.{i+1}"
        if i < len(target):
            if ch == target[i]:
                target_box.tag_add("correct", pos_start, pos_end)
            else:
                target_box.tag_add("wrong",   pos_start, pos_end)

    # current position highlight
    cur = len(typed)
    if cur < len(target):
        target_box.tag_add("current", f"1.{cur}", f"1.{cur+1}")

    target_box.config(state=DISABLED)

    # test khatam hua? — jab poora paragraph type ho jaye
    if len(typed) >= len(target):
        finish_test(typed, target)


def finish_test(typed, target):
    # timer stop karo aur final results calculate karo
    app.running = False
    if app.timer_id:
        window.after_cancel(app.timer_id)

    elapsed  = max(time.time() - app.start_time, 1)
    words    = len(target.split())
    wpm      = int((words / elapsed) * 60)

    # accuracy — kitne characters sahi lage
    correct  = sum(1 for a, b in zip(typed, target) if a == b)
    accuracy = round((correct / len(target)) * 100, 1)

    # new high score check
    if wpm > app.best_wpm:
        app.best_wpm = wpm
        save_best(wpm)
        best_label.config(text=f"🏆 Best: {app.best_wpm} WPM")
        result_label.config(text="🎉 New High Score!", fg=YELLOW)
    else:
        result_label.config(text="✅ Test Complete!", fg=GREEN)

    wpm_label.config( text=f"WPM: {wpm}",         fg=GREEN if wpm >= 40 else YELLOW)
    acc_label.config( text=f"Accuracy: {accuracy}%", fg=GREEN if accuracy >= 90 else RED)
    time_label.config(text=f"Time: {int(elapsed)}s")
    input_box.config( state=DISABLED)


# ── Main Window ──────────────────────────────────────────────────────────────
window = Tk()
window.title("Day 35 – Typing Speed Test")
window.config(bg=BG, padx=30, pady=25)
window.resizable(False, False)

Label(window, text="⌨️  Typing Speed Test", bg=BG, fg=ACCENT,
      font=FONT_H).grid(row=0, column=0, columnspan=3, pady=(0, 15))

# ── Target Text Box (readonly) ───────────────────────────────────────────────
Label(window, text="Type this paragraph:", bg=BG, fg=GRAY,
      font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=3, sticky="w")

target_box = Text(window, width=70, height=4, bg=CARD, fg=GRAY,
                  font=FONT, wrap=WORD, relief="flat",
                  spacing1=4, spacing3=4, state=DISABLED)
target_box.grid(row=2, column=0, columnspan=3, pady=(4, 12))

# colour tags for live feedback
target_box.tag_config("correct", foreground=GREEN)
target_box.tag_config("wrong",   foreground=RED, background="#3d1a1a")
target_box.tag_config("current", background=ACCENT, foreground=BG)

# ── Input Box ────────────────────────────────────────────────────────────────
Label(window, text="Your input:", bg=BG, fg=GRAY,
      font=("Segoe UI", 10)).grid(row=3, column=0, columnspan=3, sticky="w")

input_box = Text(window, width=70, height=4, bg=CARD, fg=TEXT,
                 insertbackground=TEXT, font=FONT, wrap=WORD,
                 relief="flat", spacing1=4, spacing3=4)
input_box.grid(row=4, column=0, columnspan=3, pady=(4, 15))
input_box.bind("<KeyRelease>", on_key)  # har key release par on_key call hoga

# ── Stats Row ────────────────────────────────────────────────────────────────
stats_frame = Frame(window, bg=BG)
stats_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10))

wpm_label    = Label(stats_frame, text="WPM: —",      bg=BG, fg=ACCENT, font=FONT_B)
acc_label    = Label(stats_frame, text="Accuracy: —", bg=BG, fg=ACCENT, font=FONT_B)
time_label   = Label(stats_frame, text="Time: 0s",    bg=BG, fg=TEXT,   font=FONT_B)
result_label = Label(stats_frame, text="",            bg=BG, fg=GREEN,  font=FONT_B)

wpm_label.pack(  side=LEFT, padx=20)
acc_label.pack(  side=LEFT, padx=20)
time_label.pack( side=LEFT, padx=20)
result_label.pack(side=LEFT, padx=20)

# ── Buttons + Best Score ─────────────────────────────────────────────────────
btn_frame = Frame(window, bg=BG)
btn_frame.grid(row=6, column=0, columnspan=3)

Button(btn_frame, text="▶  New Test", bg=ACCENT, fg=BG, font=FONT_B,
       relief="flat", padx=16, pady=7, command=start_new).pack(side=LEFT, padx=10)

best_label = Label(btn_frame, text=f"🏆 Best: {app.best_wpm} WPM",
                   bg=BG, fg=YELLOW, font=FONT_B)
best_label.pack(side=LEFT, padx=20)

# ── App shuru karo ────────────────────────────────────────────────────────────
start_new()
window.mainloop()
