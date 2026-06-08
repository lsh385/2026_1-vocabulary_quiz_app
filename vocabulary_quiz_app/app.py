from __future__ import annotations
import random
import tkinter as tk
from tkinter import font, ttk
from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word

class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]) -> None:
        self.words = words
        self.rng = random.Random()
        self.current: Word | None = None
        self.checked = False
        self.score = 0
        self.total = 0

        self.incorrect_words: list[Word] = []  
        self.review_mode = False  

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x320")  
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0 (정답률: 0.0%)")

        self.mode_var = tk.StringVar(value="일반 모드 진행 중")
        ttk.Label(root, textvariable=self.mode_var, font=("NanumGothic", 10), foreground="gray").pack(pady=(8, 0))

        ttk.Label(root, text="영단어").pack(pady=(8, 4))
        ttk.Label(root, textvariable=self.word_var, font=("NanumGothic", 24)).pack()

        self.answer_entry = ttk.Entry(root, font=("NanumGothic", 14))
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        buttons = ttk.Frame(root)
        buttons.pack(pady=6)
        self.check_button = ttk.Button(buttons, text="채점", command=self.check_current)
        self.check_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="다음", command=self.next_word).pack(
            side=tk.LEFT, padx=6
        )

        self.review_button = ttk.Button(buttons, text="오답 복습", command=self.toggle_review_mode)
        self.review_button.pack(side=tk.LEFT, padx=6)
        self.update_review_button_state()

        ttk.Label(root, textvariable=self.feedback_var).pack(pady=8)
        ttk.Label(root, textvariable=self.score_var).pack()

        self.next_word()

    def next_word(self) -> None:
        current_pool = self.incorrect_words if self.review_mode else self.words
        
        if self.review_mode and not self.incorrect_words:
            self.exit_review_mode()
            current_pool = self.words

        self.current = draw_word(current_pool, self.rng)
        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)
        self.feedback_var.set("")
        self.checked = False
        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    def check_current(self) -> None:
        if self.current is None or self.checked:
            return
        self.checked = True
        self.total += 1
        user_input = self.answer_entry.get()
        
        if check_answer(self.current, user_input):
            self.score += 1
            self.feedback_var.set("정답입니다!")
            if self.review_mode and self.current in self.incorrect_words:
                self.incorrect_words.remove(self.current)
        else:
            self.feedback_var.set(f"오답입니다. 정답: {self.current.meaning}")
            if not self.review_mode and self.current not in self.incorrect_words:
                self.incorrect_words.append(self.current)
        
        accuracy = (self.score / self.total) * 100 if self.total > 0 else 0.0
        self.score_var.set(f"Score: {self.score}/{self.total} (정답률: {accuracy:.1f}%)")
        
        self.check_button.state(["disabled"])
        self.update_review_button_state()

    def toggle_review_mode(self) -> None:
        if not self.review_mode:
            if not self.incorrect_words:
                return  
            self.review_mode = True
            self.mode_var.set(f"★ 오답 복습 모드 (남은 단어: {len(self.incorrect_words)}개) ★")
            self.review_button.configure(text="일반 모드")
        else:
            self.exit_review_mode()
            
        self.next_word()

    def exit_review_mode(self) -> None:
        self.review_mode = False
        self.mode_var.set("일반 모드 진행 중")
        self.review_button.configure(text="오답 복습")
        self.update_review_button_state()

    def update_review_button_state(self) -> None:
        if self.review_mode:
            self.mode_var.set(f"★ 오답 복습 모드 (남은 단어: {len(self.incorrect_words)}개) ★")
            self.review_button.state(["!disabled"])
        else:
            if not self.incorrect_words:
                self.review_button.configure(text="오답 없음")
                self.review_button.state(["disabled"])
            else:
                self.review_button.configure(text=f"오답 복습 ({len(self.incorrect_words)})")
                self.review_button.state(["!disabled"])