import typer
from rich.console import Console
from rich.table import Table
from experiments import *
from experiments.experiment_creator import ExperimentCreator
from genetic_algorithm.genetic_algo import GeneticAlgorithm
from greedy_algorithm.greedy_algo import GreedyAlgorithm

console = Console()
app = typer.Typer()

ERROR_MESS = 'Виникла помилка.'
NO_DATA = 'Даних немає.'
INCORRECT_DATA = 'Неправильно введено дані.'
NO_ACCESS = 'У Вас немає доступу до цієї команди.'

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

######################### ВИВЕДЕННЯ ТЕКСТУ НА КОНСОЛЬ
def print_comment(text: str):
    console.print(f"[italic]{text}[/italic]")
def print_error(text: str):
    console.print(f"[bold magenta]{text}[/bold magenta]")
def print_title(text: str):
    console.print(f"[bold blue]{str.upper(text)}[/bold blue]")
def print_subtitle(text: str):
    console.print(f"[bold]{str.upper(text)}[/bold]")
def print_success(text: str):
    console.print(f"[bold green]{text}[/bold green]")

######################### ЕКСПЕРИМЕНТИ
"""
1)	задання діапазонів зміни параметрів експериментів:
	розмірність задач (від; до; крок);
	кількість ІЗ, яку необхідно згенерувати для кожної розмірності;
	діапазони зміни параметрів задач (коефіцієнтів ЦФ, обмежень тощо);
2)	генерація множини ІЗ;
3)	розв’язання множини згенерованих ІЗ усіма розробленими методами;
"""
######## ОТРИМАННЯ ДАНИХ
def setup_experiments():
    def setup_1():
        return
    def setup_2():
        return
    def setup_3():
        return

######## ЗАПУСК ЕКСПЕРИМЕНТУ/ІВ
def run_experiments():
    def run_1(experiments):
        console.print("Експеримент 1....")
        experiments.run_experiment_1()
        console.print("Готово!")
    def run_2(experiments):
        console.print("Експеримент 2....")
        experiments.run_experiment_2()
        console.print("Готово!")
        print()
    def run_3(experiments):
        console.print("Експеримент 3....")
        experiments.run_experiment_3()
        console.print("Готово!")
        print()

    experiments = ExperimentCreator(output_dir='/')

######## ВИВІД РЕЗУЛЬТАТІВ
def show_experiment_results():
    return

@app.command(short_help='налаштування та запуск експериментів')
def experiment_mode():
    console.print(MAIN_MENU[2])
    experiments = ExperimentCreator(output_dir='/')

    console.print("Експеримент 1....")
    experiments.run_experiment_1()
    console.print("Готово!")


######################### ІНДИВІДУАЛЬНА ЗАДАЧА
######## ОТРИМАННЯ ДАНИХ
def input_data():
    return
def generate_data():
    return
def read_data():
    return
######## ПОКАЗ ТА ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТІВ
def show_task_results():
    return
######## РОЗВ'ЯЗОК
def solve_task(task_data, pop_size=2, mutation_rate=0.5, elite_percent=0.5, max_stagnation=5):
    print_title('Жадібний алгоритм')
    greedy_algo = GreedyAlgorithm(task_data)
    greedy_res = greedy_algo.run()
    print_success(f"Значення ЦФ: {greedy_res}")

    print()

    #print_title('Генетичний алгоритм')
    #genetic_algo = GeneticAlgorithm(task_data, pop_size, mutation_rate, elite_percent, max_stagnation)
    #best_res, _ = genetic_algo.run()
    #print_success(f"Значення ЦФ: {best_res.fitness}")

    return

@app.command(short_help="налаштування та розв'язання індивідуальної задачі")
def task_mode():
    console.print(MAIN_MENU[1])
    data = {
            "a": [80,90,60],
            "b": [80,110,70,90],
            "c": [[15, 22, 18, 25],
                  [20, 12, 10, 18],
                  [28, 20, 15, 12]],
            "delta_a": [[40, 90],
                        [30, 70],
                        [50, 100]],
            "k": [[250, 550],
                  [180, 450],
                  [320, 600]],
            "budget": 800,
            "m": 3,
            "n": 4,
            "q": 2
    }
    solve_task(data)


######################### ГОЛОВНЕ МЕНЮ
@app.command(short_help="налаштування та розв'язання індивідуальної задачі")
def start():
    console.print(MAIN_MENU[0])


if __name__ == "__main__":
    app()