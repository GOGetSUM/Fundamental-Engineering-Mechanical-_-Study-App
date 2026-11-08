"""FE Mechanical image-based flashcards (offline Tkinter app)."""
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from quiz_logic import QuizLogic

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

class StudyApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("FE Mechanical Study")
        try:
            self.window.iconbitmap(str(ROOT / "glasses.ico"))
        except tk.TclError:
            pass
        self.window.geometry("1050x850")
        self.window.configure(bg="#edf1f5")
        self.exam = tk.StringVar(value="Both exams")
        self.randomize = tk.BooleanVar(value=False)
        self.status = tk.StringVar()
        self.mode = "problem"
        self.image_ref = None
        bar = ttk.Frame(self.window, padding=12)
        bar.pack(fill="x")
        ttk.Label(bar, text="Question set:").pack(side="left")
        ttk.Combobox(bar, textvariable=self.exam, values=["Both exams", "Exam 1", "Exam 2"], state="readonly", width=15).pack(side="left", padx=8)
        ttk.Checkbutton(bar, text="Shuffle", variable=self.randomize).pack(side="left", padx=8)
        ttk.Button(bar, text="Start / Restart", command=self.restart).pack(side="left", padx=8)
        ttk.Label(bar, textvariable=self.status).pack(side="right")
        self.canvas = tk.Canvas(self.window, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=14, pady=8)
        self.canvas.bind("<Configure>", lambda _: self.render())
        controls = ttk.Frame(self.window, padding=12)
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
        self.restart()

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
            self.render()

    def show_problem(self):
        if self.quiz.current_question is not None:
            self.mode = "problem"
            self.render()

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
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        self.image_ref = ImageTk.PhotoImage(img)
        self.canvas.create_image(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, image=self.image_ref)

if __name__ == "__main__":
    StudyApp().window.mainloop()
