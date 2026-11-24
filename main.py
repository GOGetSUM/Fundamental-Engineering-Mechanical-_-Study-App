"""FE Mechanical image-based flashcards (offline Tkinter app)."""
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import time
import math
import csv
from branding import APP_NAME, CREATOR, COFFEE_URL, SOURCE_CITATION, SOURCE_NOTE
from PIL import Image, ImageTk
from quiz_logic import QuizLogic

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

class StudyApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(APP_NAME)
        try:
            self.window.iconbitmap(str(ROOT / "brand_logo.ico"))
        except tk.TclError:
            pass
        self.window.geometry("1180x900")
        self.window.minsize(900, 680)
        self.window.configure(bg="#09090c")
        self.setup_theme()
        self.exam = tk.StringVar(value="Both exams")
        self.randomize = tk.BooleanVar(value=False)
        self.status = tk.StringVar()
        self.mode = "problem"
        self.image_ref = None
        self.zoom = 1.0
        self.zoom_label = tk.StringVar(value="100%")
        self.timer_mode = tk.StringVar(value="Countdown")
        self.timer_hours = tk.StringVar(value="00")
        self.timer_minutes = tk.StringVar(value="25")
        self.timer_seconds = tk.StringVar(value="00")
        self.timer_display = tk.StringVar(value="00:25:00")
        self.timer_status = tk.StringVar(value="Ready")
        self.timer_running = False
        self.timer_elapsed = 0.0
        self.timer_duration = 25 * 60
        self.timer_started_at = None
        self.timer_frame = ttk.Frame(self.window, padding=28)
        self.answer_frame = ttk.Frame(self.window, padding=14)
        self.answer_entries = {}
        self.answer_key_path = ROOT / "answer_key.csv"
        self.answer_key = self.load_answer_key()
        self.build_timer_banner()
        self.nav = ttk.Frame(self.window, padding=(12, 12), style="Nav.TFrame")
        self.nav.pack(side="bottom", fill="x")
        self.nav_buttons = {}
        for label, page in (("Home", "home"), ("Study", "study"), ("Timer Settings", "timer"), ("Answer Sheet", "answers"), ("Features", "features"), ("About & Support", "about")):
            btn = ttk.Button(self.nav, text=label, style="Nav.TButton", command=lambda pg=page: self.show_page(pg))
            btn.pack(side="left", expand=True, fill="x", padx=4)
            self.nav_buttons[page] = btn
        self.study_frame = ttk.Frame(self.window)
        self.info_frame = ttk.Frame(self.window, padding=28)
        bar = ttk.Frame(self.study_frame, padding=12)
        bar.pack(fill="x")
        ttk.Label(bar, text="Question set:").pack(side="left")
        ttk.Combobox(bar, textvariable=self.exam, values=["Both exams", "Exam 1", "Exam 2"], state="readonly", width=15).pack(side="left", padx=8)
        ttk.Checkbutton(bar, text="Shuffle", variable=self.randomize).pack(side="left", padx=8)
        ttk.Button(bar, text="Start / Restart", command=self.restart).pack(side="left", padx=8)
        ttk.Label(bar, textvariable=self.status).pack(side="right")
        self.canvas = tk.Canvas(self.study_frame, bg="white", highlightthickness=0)
        self.zoom_bar = ttk.Frame(self.study_frame, padding=(14, 4))
        ttk.Label(self.zoom_bar, text="Solution zoom:").pack(side="left")
        ttk.Button(self.zoom_bar, text="−", width=4, command=lambda: self.change_zoom(1/1.25)).pack(side="left", padx=4)
        ttk.Label(self.zoom_bar, textvariable=self.zoom_label, width=6).pack(side="left")
        ttk.Button(self.zoom_bar, text="+", width=4, command=lambda: self.change_zoom(1.25)).pack(side="left", padx=4)
        ttk.Button(self.zoom_bar, text="Fit to Screen", command=self.reset_zoom).pack(side="left", padx=8)
        ttk.Label(self.zoom_bar, text="Mouse wheel to zoom · Drag to pan").pack(side="left", padx=8)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=8)
        self.canvas.bind("<MouseWheel>", lambda e: self.change_zoom(1.25 if e.delta > 0 else 1/1.25))
        self.canvas.bind("<Button-4>", lambda e: self.change_zoom(1.25))
        self.canvas.bind("<Button-5>", lambda e: self.change_zoom(1/1.25))
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)
        self.canvas.bind("<Configure>", lambda _: self.render())
        controls = ttk.Frame(self.study_frame, padding=12)
        controls.pack(fill="x")
        self.answer_button = ttk.Button(controls, text="Show solution", command=self.show_solution)
        self.answer_button.pack(side="left", padx=8)
        self.problem_button = ttk.Button(controls, text="Show problem", command=self.show_problem)
        self.problem_button.pack(side="left", padx=8)
        self.previous_button = ttk.Button(controls, text="← Previous problem", command=self.previous_question)
        self.previous_button.pack(side="right", padx=8)
        self.next_button = ttk.Button(controls, text="Next question →", command=self.next_question)
        self.next_button.pack(side="right", padx=8)
        self.window.bind("<Right>", lambda _: self.next_question())
        self.window.bind("<Left>", lambda _: self.previous_question())
        self.window.bind("<space>", lambda _: self.show_solution() if self.mode == "problem" else self.show_problem())
        self.build_timer_page()
        self.build_answer_page()
        self.restart()
        self.show_page("home")
        self.window.after(150, self.timer_tick)

    def setup_theme(self):
        self.colors = {"bg":"#09090c", "panel":"#17171c", "red":"#d60022", "red_hover":"#f01432", "fg":"#f7f7f8", "muted":"#b5b5c0"}
        style = ttk.Style(self.window)
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Nav.TFrame", background=self.colors["panel"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"], font=("Segoe UI", 11))
        style.configure("TButton", background=self.colors["panel"], foreground=self.colors["fg"], borderwidth=0, padding=(14, 10), font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#36363e"), ("pressed", "#474750")], foreground=[("disabled", "#777780")])
        style.configure("Nav.TButton", background=self.colors["panel"], foreground=self.colors["fg"], padding=(8, 16))
        style.configure("NavActive.TButton", background=self.colors["red"], foreground="white", padding=(8, 16))
        style.map("NavActive.TButton", background=[("active", self.colors["red_hover"])])
        style.configure("Accent.TButton", background=self.colors["red"], foreground="white", padding=(20, 15), font=("Segoe UI", 15, "bold"))
        style.map("Accent.TButton", background=[("active", self.colors["red_hover"])])
        style.configure("TCombobox", fieldbackground="#24242c", background="#24242c", foreground="#ffffff", arrowcolor="#ffffff")
        style.map("TCombobox", fieldbackground=[("readonly", "#24242c")], foreground=[("readonly", "#ffffff")])
        style.configure("TEntry", fieldbackground="#24242c", foreground="white")
        style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure("TRadiobutton", background=self.colors["bg"], foreground=self.colors["fg"])
        style.map("TRadiobutton", background=[("active", self.colors["bg"])], foreground=[("active", "white")])

    def show_page(self, page):
        for name, button in self.nav_buttons.items():
            button.configure(style="NavActive.TButton" if name == page else "Nav.TButton")
        self.study_frame.pack_forget()
        self.info_frame.pack_forget()
        self.timer_frame.pack_forget()
        self.answer_frame.pack_forget()
        if page == "answers":
            self.refresh_answer_page()
            self.answer_frame.pack(fill="both", expand=True)
            return
        if page == "timer":
            self.timer_frame.pack(fill="both", expand=True)
            return
        if page == "study":
            self.study_frame.pack(fill="both", expand=True)
            self.window.after_idle(self.render)
            return
        self.info_frame.pack(fill="both", expand=True)
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        if page == "home":
            # Branded landing screen: no unnecessary footer statement.
            home = tk.Frame(self.info_frame, bg=self.colors["bg"])
            home.pack(expand=True, fill="both")
            content = tk.Frame(home, bg=self.colors["bg"])
            content.place(relx=0.5, rely=0.48, anchor="center")
            icon_path = ROOT / "brand_logo.png"
            if icon_path.exists():
                with Image.open(icon_path) as source:
                    icon = source.convert("RGBA")
                    icon.thumbnail((310, 310))
                self.home_icon = ImageTk.PhotoImage(icon)
                tk.Label(content, image=self.home_icon, bg=self.colors["bg"]).pack(pady=(0, 16))
            tk.Label(content, text="FE Mechanical Study", font=("Segoe UI", 34, "bold"),
                     fg="white", bg=self.colors["bg"]).pack()
            tk.Label(content, text="Fundamentals of Engineering (FE) Exam Review",
                     font=("Segoe UI", 15), fg=self.colors["muted"], bg=self.colors["bg"]).pack(pady=(5, 30))
            ttk.Button(content, text="📖  Start Studying  ›", style="Accent.TButton",
                       command=lambda: self.show_page("study")).pack(fill="x", padx=55, pady=(0, 15))
            if COFFEE_URL:
                ttk.Button(content, text="☕  Buy Me a Coffee  ↗",
                           command=lambda: webbrowser.open(COFFEE_URL)).pack(fill="x", padx=85)
        elif page == "features":
            self.page_title("Features & How to Use")
            features = (
                "Choose Exam 1, Exam 2, or both sets.",
                "Turn on Shuffle to randomize question order.",
                "Use Show solution to reveal the worked answer; Show problem returns to the question.",
                "On solutions, zoom from 100% to 400% with + / − or the mouse wheel.",
                "Drag an enlarged solution to pan; Fit to Screen resets zoom.",
                "Use Previous / Next or the left and right arrow keys to navigate.",
                "Use Space to switch between the problem and its solution.",
                "Study offline after setup; no account or subscription required.",
                "Use the timer in the top banner on every page, including while solving questions.",
                "Open Timer Settings to configure countdown duration or switch to stopwatch.",
                "Open Answer Sheet for an editable 220-question grid and direct access to each solution.",
            )
            for item in features:
                ttk.Label(self.info_frame, text="• " + item, font=("Segoe UI", 11),
                          wraplength=760, justify="left").pack(anchor="w", pady=8)
        else:
            self.page_title("About & Support")
            self.info_text("This application is an independent study aid for students preparing for "
                           "the Fundamentals of Engineering (FE) exam, with a focus on mechanical engineering. "
                           "It is intended for practice and review, not as an official exam or a guarantee of passing.")
            self.info_text("This Python edition is distributed as a digital download. Tips are completely optional "
                           "and do not unlock any features.")
            ttk.Label(self.info_frame, text="Support the creator", font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(18, 6))
            if COFFEE_URL:
                ttk.Button(self.info_frame, text="Buy Me a Coffee (opens browser)",
                           command=lambda: webbrowser.open(COFFEE_URL)).pack(anchor="w", pady=5)
            else:
                self.info_text("Buy Me a Coffee link coming soon — set COFFEE_URL in branding.py.")
            ttk.Label(self.info_frame, text="Sources & Attribution", font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(20, 6))
            self.info_text(SOURCE_CITATION or "Textbook citation pending: enter the verified title, author, edition, publisher, and year in branding.py.")
            self.info_text(SOURCE_NOTE)
            self.info_text("Not affiliated with or endorsed by NCEES. FE and Fundamentals of Engineering are references to the exam.")

    def build_timer_banner(self):
        banner = tk.Frame(self.window, bg="#111115", padx=18, pady=11,
                          highlightbackground=self.colors["red"], highlightthickness=0)
        banner.pack(side="top", fill="x")
        tk.Label(banner, text="◷  Study Timer", bg="#111115", fg="white",
                 font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 18))
        ttk.Button(banner, text="Countdown / Stopwatch", command=lambda: self.show_page("timer")).pack(side="left", padx=5)
        tk.Label(banner, textvariable=self.timer_display, bg="#111115", fg="white",
                 font=("Consolas", 22, "bold")).pack(side="left", padx=18)
        ttk.Button(banner, text="▶", command=self.timer_start).pack(side="left", padx=3)
        ttk.Button(banner, text="Ⅱ", command=self.timer_pause).pack(side="left", padx=3)
        ttk.Button(banner, text="↺", command=self.timer_reset).pack(side="left", padx=3)
        ttk.Button(banner, text="⚙", command=lambda: self.show_page("timer")).pack(side="left", padx=3)
        tk.Label(banner, textvariable=self.timer_status, bg="#111115", fg="#bdbdc5").pack(side="right", padx=8)
        tk.Frame(self.window, bg=self.colors["red"], height=3).pack(side="top", fill="x")

    def load_answer_key(self):
        answers = {}
        if self.answer_key_path.exists():
            with self.answer_key_path.open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    try:
                        number = int(row.get("question", ""))
                        answer = row.get("answer", "").strip().upper()
                        if 1 <= number <= 220 and answer in ("A", "B", "C", "D"):
                            answers[number] = answer
                    except (ValueError, TypeError):
                        continue
        return answers

    def build_answer_page(self):
        ttk.Label(self.answer_frame, text="Complete Exam Answer Sheet", font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(0, 6))
        ttk.Label(self.answer_frame, text="Answer letters are shown only when entered and verified against the original solutions. "
                  "Blank entries are not confirmed. Click a question to inspect its full worked solution.",
                  wraplength=920, justify="left").pack(anchor="w", pady=(0, 10))
        selector = ttk.Frame(self.answer_frame)
        selector.pack(fill="x", pady=5)
        self.answer_exam = tk.StringVar(value="Exam 1")
        for name in ("Exam 1", "Exam 2"):
            ttk.Radiobutton(selector, text=name, value=name, variable=self.answer_exam,
                            command=self.refresh_answer_page).pack(side="left", padx=8)
        ttk.Button(selector, text="Save answer key", command=self.save_answer_key).pack(side="right")
        self.answer_scroll = tk.Canvas(self.answer_frame, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.answer_frame, orient="vertical", command=self.answer_scroll.yview)
        self.answer_scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.answer_scroll.pack(side="left", fill="both", expand=True)
        self.answer_inner = ttk.Frame(self.answer_scroll)
        self.answer_scroll.create_window((0, 0), window=self.answer_inner, anchor="nw", tags="inner")
        self.answer_inner.bind("<Configure>", lambda e: self.answer_scroll.configure(scrollregion=self.answer_scroll.bbox("all")))
        self.answer_scroll.bind("<Configure>", lambda e: self.answer_scroll.itemconfigure("inner", width=e.width))

    def refresh_answer_page(self):
        for n, var in self.answer_entries.items():
            value = var.get().strip().upper()
            if value in ("A", "B", "C", "D"):
                self.answer_key[n] = value
            elif not value:
                self.answer_key.pop(n, None)
        self.answer_entries.clear()
        for widget in self.answer_inner.winfo_children():
            widget.destroy()
        start = 1 if self.answer_exam.get() == "Exam 1" else 111
        for index, n in enumerate(range(start, start + 110)):
            r, c = divmod(index, 5)
            cell = ttk.Frame(self.answer_inner, padding=(6, 5))
            cell.grid(row=r, column=c, sticky="w", padx=5, pady=3)
            ttk.Button(cell, text=f"{n:03}", width=5, command=lambda number=n: self.open_answer_solution(number)).pack(side="left")
            var = tk.StringVar(value=self.answer_key.get(n, ""))
            ttk.Combobox(cell, textvariable=var, values=("", "A", "B", "C", "D"),
                         width=3, state="readonly").pack(side="left", padx=4)
            self.answer_entries[n] = var
        self.answer_scroll.yview_moveto(0)

    def save_answer_key(self):
        for n, var in self.answer_entries.items():
            value = var.get().strip().upper()
            if value in ("A", "B", "C", "D"):
                self.answer_key[n] = value
            else:
                self.answer_key.pop(n, None)
        try:
            with self.answer_key_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(("question", "answer"))
                for n in range(1, 221):
                    writer.writerow((n, self.answer_key.get(n, "")))
        except OSError as exc:
            messagebox.showerror("Unable to save", f"Could not write answer_key.csv: {exc}")
            return
        messagebox.showinfo("Answer sheet saved", "Answer entries saved to answer_key.csv. "
                            "Please verify each entry against the source solutions before distributing it as a correct answer key.")

    def open_answer_solution(self, number):
        # A dedicated viewer does not disturb the current study question or shuffled order.
        path = ROOT / "assets" / "solutions" / f"{number:03}.png"
        if not path.exists():
            messagebox.showwarning("Missing solution", f"No solution image for question {number}.")
            return
        top = tk.Toplevel(self.window)
        top.title(f"Solution — Question {number:03}")
        top.geometry("850x750")
        canvas = tk.Canvas(top, bg="white")
        sx = ttk.Scrollbar(top, orient="horizontal", command=canvas.xview)
        sy = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        canvas.pack(fill="both", expand=True)
        with Image.open(path) as src:
            photo = ImageTk.PhotoImage(src.convert("RGB"))
        canvas.create_image(0, 0, anchor="nw", image=photo)
        canvas.image_ref = photo
        canvas.configure(scrollregion=(0, 0, photo.width(), photo.height()))
        canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))

    @staticmethod
    def format_time(seconds):
        total = max(0, int(seconds))
        return f"{total // 3600:02d}:{(total // 60) % 60:02d}:{total % 60:02d}"

    def build_timer_page(self):
        ttk.Label(self.timer_frame, text="Study Timer", font=("Segoe UI", 24, "bold")).pack(pady=(12, 18))
        modes = ttk.Frame(self.timer_frame)
        modes.pack(pady=8)
        for mode in ("Countdown", "Stopwatch"):
            ttk.Radiobutton(modes, text=mode, value=mode, variable=self.timer_mode,
                            command=self.timer_switch_mode).pack(side="left", padx=18)
        entry_row = ttk.Frame(self.timer_frame)
        entry_row.pack(pady=16)
        self.timer_entries = []
        for label, variable in (("Hours", self.timer_hours), ("Minutes", self.timer_minutes), ("Seconds", self.timer_seconds)):
            section = ttk.Frame(entry_row)
            section.pack(side="left", padx=12)
            ttk.Label(section, text=label).pack()
            entry = ttk.Entry(section, textvariable=variable, width=7, justify="center", font=("Segoe UI", 14))
            entry.pack(pady=4)
            self.timer_entries.append(entry)
        ttk.Label(self.timer_frame, textvariable=self.timer_display, font=("Consolas", 52, "bold")).pack(pady=(20, 4))
        ttk.Label(self.timer_frame, textvariable=self.timer_status, font=("Segoe UI", 12)).pack(pady=8)
        actions = ttk.Frame(self.timer_frame)
        actions.pack(pady=16)
        self.timer_start_button = ttk.Button(actions, text="Start", command=self.timer_start)
        self.timer_start_button.pack(side="left", padx=10)
        ttk.Button(actions, text="Pause", command=self.timer_pause).pack(side="left", padx=10)
        ttk.Button(actions, text="Reset", command=self.timer_reset).pack(side="left", padx=10)
        ttk.Label(self.timer_frame, text="The timer continues while you browse other pages.\n"
                  "Countdown completion displays an alert.", justify="center").pack(pady=14)

    def timer_parse_duration(self):
        try:
            values = [int(v.get().strip()) for v in (self.timer_hours, self.timer_minutes, self.timer_seconds)]
        except ValueError:
            raise ValueError("Enter whole numbers for hours, minutes, and seconds.")
        if not (0 <= values[0] <= 99 and 0 <= values[1] < 60 and 0 <= values[2] < 60):
            raise ValueError("Use 0–99 hours, 0–59 minutes, and 0–59 seconds.")
        duration = values[0] * 3600 + values[1] * 60 + values[2]
        if duration == 0:
            raise ValueError("Set a countdown greater than zero.")
        return duration

    def timer_switch_mode(self):
        self.timer_running = False
        self.timer_started_at = None
        self.timer_elapsed = 0.0
        self.timer_start_button.configure(text="Start")
        countdown = self.timer_mode.get() == "Countdown"
        for entry in self.timer_entries:
            entry.configure(state="normal" if countdown else "disabled")
        if countdown:
            try:
                self.timer_duration = self.timer_parse_duration()
            except ValueError:
                self.timer_duration = 25 * 60
            self.timer_display.set(self.format_time(self.timer_duration))
        else:
            self.timer_display.set("00:00:00")
        self.timer_status.set("Ready")

    def timer_start(self):
        if self.timer_running:
            return
        if self.timer_elapsed == 0 and self.timer_mode.get() == "Countdown":
            try:
                self.timer_duration = self.timer_parse_duration()
            except ValueError as exc:
                messagebox.showerror("Invalid countdown", str(exc))
                return
        if self.timer_mode.get() == "Countdown" and self.timer_elapsed >= self.timer_duration:
            self.timer_elapsed = 0.0
        self.timer_started_at = time.monotonic()
        self.timer_running = True
        self.timer_status.set("Running")
        self.timer_start_button.configure(text="Resume")
        self.timer_update_display()

    def timer_pause(self):
        if self.timer_running:
            self.timer_elapsed += time.monotonic() - self.timer_started_at
            self.timer_running = False
            self.timer_started_at = None
            self.timer_status.set("Paused")
            self.timer_update_display()

    def timer_reset(self):
        self.timer_running = False
        self.timer_started_at = None
        self.timer_elapsed = 0.0
        self.timer_start_button.configure(text="Start")
        self.timer_status.set("Ready")
        if self.timer_mode.get() == "Countdown":
            try:
                self.timer_duration = self.timer_parse_duration()
            except ValueError as exc:
                messagebox.showerror("Invalid countdown", str(exc))
                return
        self.timer_update_display()

    def timer_update_display(self):
        elapsed = self.timer_elapsed + (time.monotonic() - self.timer_started_at if self.timer_running else 0)
        if self.timer_mode.get() == "Countdown":
            remaining = max(0, self.timer_duration - elapsed)
            # Round up so the clock does not immediately lose one second.
            self.timer_display.set(self.format_time(math.ceil(remaining)))
            if self.timer_running and remaining <= 0:
                self.timer_running = False
                self.timer_started_at = None
                self.timer_elapsed = self.timer_duration
                self.timer_status.set("Time's up!")
                self.timer_start_button.configure(text="Start")
                self.window.bell()
                messagebox.showinfo("Countdown complete", "Your study countdown has finished!")
        else:
            self.timer_display.set(self.format_time(elapsed))

    def timer_tick(self):
        if self.timer_running:
            self.timer_update_display()
        self.window.after(150, self.timer_tick)

    def page_title(self, title):
        ttk.Label(self.info_frame, text=title, font=("Segoe UI", 24, "bold"),
                  wraplength=780).pack(pady=(15, 22))

    def info_text(self, value):
        ttk.Label(self.info_frame, text=value, font=("Segoe UI", 11),
                  wraplength=760, justify="left").pack(anchor="w", pady=8)

    def restart(self):
        choice = self.exam.get()
        ids = range(1, 111) if choice == "Exam 1" else range(111, 221) if choice == "Exam 2" else range(1, 221)
        self.quiz = QuizLogic(ids, shuffle=self.randomize.get())
        self.next_question()

    def update_question(self):
        n = self.quiz.current_question
        if n is None:
            self.status.set("No questions in this set")
            return
        self.mode = "problem"
        self.zoom = 1.0
        self.zoom_bar.pack_forget()
        done, total = self.quiz.progress
        self.status.set(f"Exam {1 if n <= 110 else 2} · Problem {n:03} · {done}/{total}")
        self.answer_button.configure(state="normal")
        self.previous_button.configure(state="normal" if self.quiz.has_previous() else "disabled")
        self.next_button.configure(state="normal" if self.quiz.still_has_questions() else "disabled")
        self.render()

    def next_question(self):
        if self.quiz.next_question() is not None:
            self.update_question()

    def previous_question(self):
        if self.quiz.previous_question() is not None:
            self.update_question()

    def show_solution(self):
        if self.quiz.current_question is not None:
            self.mode = "solution"
            self.zoom_bar.pack(fill="x", before=self.canvas)
            self.render()

    def show_problem(self):
        if self.quiz.current_question is not None:
            self.mode = "problem"
            self.zoom = 1.0
            self.zoom_bar.pack_forget()
            self.render()

    def change_zoom(self, factor):
        if self.mode != "solution":
            return
        self.zoom = max(1.0, min(4.0, self.zoom * factor))
        self.render()

    def reset_zoom(self):
        self.zoom = 1.0
        self.render()

    def start_pan(self, event):
        if self.mode == "solution" and self.zoom > 1:
            self.canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        if self.mode == "solution" and self.zoom > 1:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

    def render(self):
        self.canvas.delete("all")
        if self.mode == "complete":
            self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, text="All questions completed!", font=("Arial", 24))
            return
        n = self.quiz.current_question
        if n is None:
            return
        path = ROOT / "assets" / ("solutions" if self.mode == "solution" else "problems") / f"{n:03}.png"
        if not path.exists():
            self.canvas.create_text(20, 20, anchor="nw", text=f"Missing image: {path}", fill="red")
            return
        with Image.open(path) as src:
            img = src.convert("RGB")
        width = max(1, self.canvas.winfo_width()-30)
        height = max(1, self.canvas.winfo_height()-30)
        zoom = self.zoom if self.mode == "solution" else 1.0
        self.zoom_label.set(f"{zoom:.0%}")
        if self.mode == "solution":
            scale = min(width / img.width, height / img.height, 1.0) * zoom
            img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.Resampling.LANCZOS)
        else:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        self.image_ref = ImageTk.PhotoImage(img)
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        rw, rh = max(cw, img.width + 30), max(ch, img.height + 30)
        self.canvas.configure(scrollregion=(0, 0, rw, rh), cursor="fleur" if zoom > 1 else "")
        self.canvas.create_image(rw/2, rh/2, image=self.image_ref)
        self.canvas.xview_moveto(0.5 * (rw-cw)/rw)
        self.canvas.yview_moveto(0.5 * (rh-ch)/rh)

if __name__ == "__main__":
    StudyApp().window.mainloop()
