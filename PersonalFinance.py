import os
import csv
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Label, Entry, Button, Listbox, END, Frame, StringVar, Radiobutton

class FinanceTracker:
    def __init__(self, data_file="finances.csv"):
        self.data_file = data_file
        self.finances = []  # Список для хранения данных о финансах
        self.incomes = []   # Список для хранения данных о доходах

    def add_transaction(self, amount, category, date, transaction_type):
        # Поиск существующей транзакции с указанной датой
        existing_transaction = None
        for transaction in self.finances + self.incomes:
            if transaction["date"] == date and transaction["category"] == category and transaction["type"] == transaction_type:
                existing_transaction = transaction
                break

        if existing_transaction:
            # Если транзакция с указанной датой уже существует, добавляем к ней сумму
            existing_transaction["amount"] = str(float(existing_transaction["amount"]) + float(amount))
        else:
            # Иначе создаем новую транзакцию
            transaction = {"amount": amount, "category": category, "date": date, "type": transaction_type}
            if transaction_type == "Расход":
                self.finances.append(transaction)
            elif transaction_type == "Доход":
                self.incomes.append(transaction)

    def save_data(self):
        # Сохранение данных в файл
        with open(self.data_file, mode="w", newline="") as file:
            fieldnames = ["amount", "category", "date", "type"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.finances + self.incomes)

    def generate_monthly_chart(self):
        # Создание графика для текущего месяца
        today = date.today()
        current_month = today.strftime("%Y-%m")
        transactions_in_month = [t for t in self.finances if t["date"].startswith(current_month)]
        incomes_in_month = [t for t in self.incomes if t["date"].startswith(current_month)]

        if not transactions_in_month and not incomes_in_month:
            # Нет данных для построения графика
            return

        category_amounts = {}
        for t_type, transactions in [("Расходы", transactions_in_month), ("Доходы", incomes_in_month)]:
            for transaction in transactions:
                category = transaction["category"]
                amount = float(transaction["amount"])
                if category in category_amounts:
                    category_amounts[category][t_type] += amount
                else:
                    category_amounts[category] = {t_type: amount}

        categories = list(category_amounts.keys())
        finance_amounts = [category_amounts[category].get("Расходы", 0) for category in categories]
        income_amounts = [category_amounts[category].get("Доходы", 0) for category in categories]

        plt.figure(figsize=(8, 6))
        plt.plot(categories, finance_amounts, label="Расходы")
        plt.plot(categories, income_amounts, label="Доходы")
        plt.xlabel("Категория")
        plt.ylabel("Сумма")
        plt.title(f"Расходы и доходы за {current_month}")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join("images", f"chart_{current_month}.png"))

class FinanceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер личных финансов")

        # Создаем и настраиваем элементы интерфейса
        self.amount_label = Label(root, text="Сумма:")
        self.amount_label.pack()
        self.amount_entry = Entry(root)
        self.amount_entry.pack()

        self.category_label = Label(root, text="Категория:")
        self.category_label.pack()
        self.category_entry = Entry(root)
        self.category_entry.pack()

        self.date_label = Label(root, text="Дата (гггг-мм-дд):")
        self.date_label.pack()
        self.date_entry = Entry(root)
        self.date_entry.pack()

        # Создаем переменную для типа транзакции
        self.transaction_type = StringVar()
        self.transaction_type.set("Расход")

        self.expense_radio = Radiobutton(root, text="Расход", variable=self.transaction_type, value="Расход")
        self.expense_radio.pack()

        self.income_radio = Radiobutton(root, text="Доход", variable=self.transaction_type, value="Доход")
        self.income_radio.pack()

        self.add_button = Button(root, text="Добавить транзакцию", command=self.add_transaction)
        self.add_button.pack()

        self.show_chart_button = Button(root, text="Показать график", command=self.generate_monthly_chart)
        self.show_chart_button.pack()

        self.transactions_listbox = Listbox(root)
        self.transactions_listbox.pack()

        # Инициализация трекера
        self.tracker = FinanceTracker()

        # Создаем фрейм для графика
        self.chart_frame = Frame(root)
        self.chart_frame.pack()

    def add_transaction(self):
        amount = self.amount_entry.get()
        category = self.category_entry.get()
        date = self.date_entry.get()
        transaction_type = self.transaction_type.get()
        self.tracker.add_transaction(amount, category, date, transaction_type)
        self.tracker.save_data()
        self.update_transactions_list()

    def generate_monthly_chart(self):
        self.tracker.generate_monthly_chart()
        self.update_transactions_list()
        self.show_chart()

    def update_transactions_list(self):
        self.transactions_listbox.delete(0, END)
        for transaction in self.tracker.finances + self.tracker.incomes:
            self.transactions_listbox.insert(END, f"{transaction['date']} - {transaction['category']} - {transaction['amount']} ({transaction['type']})")

    def show_chart(self):
        # Отображаем график во фрейме
        if hasattr(self, "chart_frame"):
            self.chart_frame.destroy()
        self.chart_frame = Frame(self.root)
        self.chart_frame.pack()

        figure, ax = plt.subplots(figsize=(8, 6))
        canvas = FigureCanvasTkAgg(figure, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()

        today = date.today()
        current_month = today.strftime("%Y-%m")
        transactions_in_month = [t for t in self.tracker.finances if t["date"].startswith(current_month)]
        incomes_in_month = [t for t in self.tracker.incomes if t["date"].startswith(current_month)]

        if not transactions_in_month and not incomes_in_month:
            # Нет данных для построения графика
            return

        category_amounts = {}
        for t_type, transactions in [("Расходы", transactions_in_month), ("Доходы", incomes_in_month)]:
            for transaction in transactions:
                category = transaction["category"]
                amount = float(transaction["amount"])
                if category in category_amounts:
                    category_amounts[category][t_type] += amount
                else:
                    category_amounts[category] = {t_type: amount}

        categories = list(category_amounts.keys())
        finance_amounts = [category_amounts[category].get("Расходы", 0) for category in categories]
        income_amounts = [category_amounts[category].get("Доходы", 0) for category in categories]

        plt.plot(categories, finance_amounts, label="Расходы")
        plt.plot(categories, income_amounts, label="Доходы")
        ax.set_xlabel("Категория")
        ax.set_ylabel("Сумма")
        ax.set_title(f"Расходы и доходы за {current_month}")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

if __name__ == "__main__":
    root = Tk()
    app = FinanceTrackerGUI(root)
    root.mainloop()
