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

        # --- 오답 복습을 위한 기능 추가 변수 ---
        self.incorrect_words: list[Word] = []  # 틀린 단어를 저장할 오답 노트
        self.review_mode = False  # 현재 복습 모드인지 여부
        # --------------------------------------

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x320")  # 버튼 추가 공간 확보를 위해 세로 크기를 280 -> 320으로 약간 늘렸습니다.
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")

        # --- 상단 상태 표시 레이블 추가 ---
        self.mode_var = tk.StringVar(value="일반 모드 진행 중")
        ttk.Label(root, textvariable=self.mode_var, font=("NanumGothic", 10), foreground="gray").pack(pady=(8, 0))
        # ----------------------------------

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

        # --- 오답 복습 버튼 추가 ---
        self.review_button = ttk.Button(buttons, text="오답 복습", command=self.toggle_review_mode)
        self.review_button.pack(side=tk.LEFT, padx=6)
        self.update_review_button_state()
        # ----------------------------

        ttk.Label(root, textvariable=self.feedback_var).pack(pady=8)
        ttk.Label(root, textvariable=self.score_var).pack()

        self.next_word()

    def next_word(self) -> None:
        # 어떤 단어 풀에서 뽑을지 결정 (일반 모드 vs 오답 복습 모드)
        current_pool = self.incorrect_words if self.review_mode else self.words
        
        # 복습 모드인데 오답 노드가 비어있다면 일반 모드로 강제 복귀
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
            # 복습 모드에서 정답을 맞춘 경우 오답 노트에서 제거 처리
            if self.review_mode and self.current in self.incorrect_words:
                self.incorrect_words.remove(self.current)
        else:
            self.feedback_var.set(f"오답입니다. 정답: {self.current.meaning}")
            # 일반 모드에서 틀렸을 때만 오답 노트에 추가 (중복 방지)
            if not self.review_mode and self.current not in self.incorrect_words:
                self.incorrect_words.append(self.current)
        
        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.check_button.state(["disabled"])
        self.update_review_button_state()

    # --- 오답 복습 기능을 위해 추가된 메서드들 ---
    
    def toggle_review_mode(self) -> None:
        """오답 복습 모드를 켜고 끄는 토글 함수"""
        if not self.review_mode:
            if not self.incorrect_words:
                return  # 틀린 단어가 없으면 복습 모드 진입 불가
            self.review_mode = True
            self.mode_var.set(f"★ 오답 복습 모드 (남은 단어: {len(self.incorrect_words)}개) ★")
            self.review_button.configure(text="일반 모드")
        else:
            self.exit_review_mode()
            
        self.next_word()

    def exit_review_mode(self) -> None:
        """일반 모드로 복귀"""
        self.review_mode = False
        self.mode_var.set("일반 모드 진행 중")
        self.review_button.configure(text="오답 복습")
        self.update_review_button_state()

    def update_review_button_state(self) -> None:
        """오답 노트 상태에 따라 버튼 활성화/비활성화 및 텍스트 갱신"""
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
