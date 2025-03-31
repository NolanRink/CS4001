import tkinter as tk
import json
import random

# QuizApp for miniproject 1. The app is supposed to herlp users gain knowledge on python programming for data analysis
class QuizApp:
    def __init__(self, master):
        self.master = master
        master.title("Quiz Application")
        master.configure(bg="#f0f8ff")  # Light background color

        # Set window size (optional)
        master.geometry("600x500")

        # Load questions from the JSON file
        with open("questions.json", "r") as f:
            self.questions_data = json.load(f)

        # Define difficulty levels and initialize counters
        self.difficulty_levels = ["easy", "medium", "hard"]
        self.current_difficulty_index = 0
        self.correct_count = 0

        # Shuffle questions for random order in each difficulty
        for level in self.difficulty_levels:
            random.shuffle(self.questions_data[level])
        self.current_question_index = 0

        # --- Create Frames for Layout ---
        self.header_frame = tk.Frame(master, bg="#f0f8ff")
        self.header_frame.pack(pady=15)

        self.question_frame = tk.Frame(master, bg="#f0f8ff")
        self.question_frame.pack(pady=10)

        self.options_frame = tk.Frame(master, bg="#f0f8ff")
        self.options_frame.pack(pady=10)

        self.explanation_frame = tk.Frame(master, bg="#f0f8ff")
        self.explanation_frame.pack(pady=10)

        self.footer_frame = tk.Frame(master, bg="#f0f8ff")
        self.footer_frame.pack(pady=15)

        # --- Header: Difficulty Label ---
        self.difficulty_label = tk.Label(
            self.header_frame, 
            text="Difficulty: Easy", 
            font=("Helvetica", 16, "bold"),
            bg="#f0f8ff", fg="#333"
        )
        self.difficulty_label.pack()

        # --- Question Section ---
        self.question_label = tk.Label(
            self.question_frame, 
            text="", 
            font=("Helvetica", 14),
            wraplength=550, justify="center",
            bg="#f0f8ff", fg="#222"
        )
        self.question_label.pack()

        # --- Options Section: Grid Layout for Option Buttons ---
        self.option_buttons = {}
        for index, option in enumerate(["A", "B", "C", "D"]):
            btn = tk.Button(
                self.options_frame, 
                text="", 
                font=("Helvetica", 12),
                width=40, 
                bg="#ffffff", relief="raised", bd=2,
                command=lambda opt=option: self.check_answer(opt)
            )
            btn.grid(row=index, column=0, pady=5, padx=10)
            self.option_buttons[option] = btn

        # --- Explanation Section ---
        self.explanation_label = tk.Label(
            self.explanation_frame, 
            text="", 
            font=("Helvetica", 12, "italic"),
            fg="#00529b", wraplength=550,
            bg="#f0f8ff"
        )
        self.explanation_label.pack()

        # --- Footer: Next/Finish Button ---
        self.next_button = tk.Button(
            self.footer_frame, 
            text="Next Question", 
            font=("Helvetica", 12),
            bg="#4CAF50", fg="white", activebackground="#45a049",
            command=self.next_question
        )
        # The Next button is not packed until an answer is selected

        # Start the quiz by displaying the first question
        self.show_question()

    def show_question(self):
        """Display the current question and options on the GUI."""
        difficulty = self.difficulty_levels[self.current_difficulty_index]
        if self.current_question_index >= len(self.questions_data[difficulty]):
            self.current_question_index = 0

        question_obj = self.questions_data[difficulty][self.current_question_index]
        self.difficulty_label.config(text=f"Difficulty: {difficulty.capitalize()}")
        self.question_label.config(text=question_obj["question"])

        for opt, btn in self.option_buttons.items():
            btn.config(text=f"{opt}. {question_obj['options'][opt]}", state=tk.NORMAL)
        
        # Clear previous explanation and hide Next button if it is shown
        self.explanation_label.config(text="")
        if self.next_button.winfo_ismapped():
            self.next_button.pack_forget()

    def check_answer(self, selected_option):
        """Handle answer selection: check answer, show message, explanation, and adjust GUI colors."""
        # Disable option buttons to prevent further selections
        for btn in self.option_buttons.values():
            btn.config(state=tk.DISABLED)

        difficulty = self.difficulty_levels[self.current_difficulty_index]
        question_obj = self.questions_data[difficulty][self.current_question_index]
        correct_option = question_obj["answer"]

        is_correct = (selected_option == correct_option)
        if is_correct:
            self.correct_count += 1
            message = "Correct!"
        else:
            message = "Incorrect!"

        # Display result message with explanation
        self.explanation_label.config(text=f"{message} Explanation: {question_obj['explanation']}")

        next_color = "#4CAF50" if is_correct else "#F44336"  # Green if correct, red if incorrect
        self.next_button.config(bg=next_color, activebackground=next_color)

        # Check if the user should level up 
        if is_correct and self.correct_count == 3:
            if self.current_difficulty_index < len(self.difficulty_levels) - 1:
                self.current_difficulty_index += 1
                self.correct_count = 0
                self.current_question_index = -1  # Next question will start at 0
                current_text = self.explanation_label.cget("text")
                new_level_name = self.difficulty_levels[self.current_difficulty_index].capitalize()
                self.explanation_label.config(text=current_text + f"\n\nLevel Up! Now moving to {new_level_name} questions.")
            else:
                current_text = self.explanation_label.cget("text")
                self.explanation_label.config(text=current_text + "\n\nCongratulations! You have completed the quiz.")
                self.next_button.config(text="Finish", command=self.master.destroy)

        self.next_button.pack(pady=5)

    def next_question(self):
        """Proceed to the next question (or new difficulty level)."""
        self.current_question_index += 1
        self.show_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
