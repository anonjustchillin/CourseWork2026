import typer
from rich.console import Console
from rich.table import Table

console = Console()
app = typer.Typer()

# console.print
ERROR_MESS = f'[bold magenta]Виникла помилка.[/bold magenta]'
NO_DATA = f'[bold magenta]Даних немає.[/bold magenta]'
INCORRECT_DATA = f'[bold magenta]Неправильно введено дані.[/bold magenta]'
NO_ACCESS = f'[bold magenta]У Вас немає доступу до цієї команди.[/bold magenta]'

MAIN_MENU = ["Введення даних задачі",
        "Розв'язати задачу всіма розробленими алгоритмами",
        "Провести експерименти",
        "Вивести дані задачі",
        "Вивести розв'язки задачі",
        "Завершити роботу"]

DATA_MENU = ["Ввести дані самостійно",
             "Зчитати з файлу",
             "Згенерувати",
             "Повернутись в головне меню"]

RES_DATA_MENU = ["Вивести дані у консоль",
                 "Записати дані у файлі",
                 "Повернутись в головне меню"]

CHOICE_STR = 'Вибір: '

ALGO_1 = "Жадібний алгоритм"
ALGO_2 = "Генетичний алгоритм"

RESULT_STR = ["Результат роботи: ",
              "Значення ЦФ: "]

TOPIC = "Задача вибору сценаріїв розширення потужностей у транспортній моделі з бюджетним обмеженням"

@app.command(short_help='інформація про авторів')
def about():
    console.print(f"[bold magenta]Курсова робота з 'Дослідження операцій в інформаційно-управляючих системах' [bold blue]Кіселара Владислава, Ковалюк Валерії, Топки Тіни, Черепні Юрія[/bold blue] з групи ІС-32.[/bold magenta]")


def cut_str(text: str):
    return " ".join(text.split())


if __name__ == "__main__":
    app()