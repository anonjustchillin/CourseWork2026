import typer
from rich.console import Console
from rich.table import Table
from all_text import *
from config import *
from experiments import *
from experiments.experiment_creator import ExperimentCreator
from genetic_algorithm.genetic_algo import GeneticAlgorithm
from greedy_algorithm.greedy_algo import GreedyAlgorithm
import random
import os

console = Console()
app = typer.Typer()

CURR_MENU = -1

DATA = {}
GA_DATA = {}

def switch_menu_page(choice):
    global CURR_MENU
    CURR_MENU = choice

    if CURR_MENU == 0:
        setup_task(CURR_MENU)
    elif CURR_MENU == 1:
        task_mode(CURR_MENU)
    elif CURR_MENU == 2:
        show_task(CURR_MENU)
    elif CURR_MENU == 3:
        show_task_results(CURR_MENU)
    elif CURR_MENU == 4:
        experiment_mode(CURR_MENU)
    else:
        return

def switch_data_menu_page(choice):
    if choice == 0:
        input_data()
    elif choice == 1:
        read_data()
    elif choice == 2:
        generate_data()
    elif choice == 3:
        start()
    else:
        return


def menu_input(menu_list=MAIN_MENU):
    while True:
        try:
            choice = int(input(CHOICE_STR))
            choice -= 1
            if choice not in range(len(menu_list)):
                raise ValueError
            else:
                break
        except ValueError:
            print_error(ERROR_MESS)
    return choice


@app.command(short_help='інформація про авторів')
def about():
    console.print(INFO)

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
def print_blue(text: str):
    console.print(f"[blue]{text}[/blue]")
def print_success(text: str):
    console.print(f"[bold green]{text}[/bold green]")
def print_options(menu_list=MAIN_MENU, title=True):
    for i in range(len(menu_list)):
        text = str(i+1) + " -- " + menu_list[i]
        if title:
            print_title(text)
        else:
            print_blue(text)

######################### ВВЕСТИ ДАНІ ЗАДАЧІ
######## ОТРИМАННЯ ДАНИХ
def input_data(getGA=True):
    def get_input(name):
        while True:
            try:
                value = float(input(f'Введіть {name}: '))
                break
            except ValueError:
                print_error(INCORRECT_DATA)
        return value

    def input_basic():
        global DATA

        first_keys = ["budget", "m", "n", "q"]
        other_keys_1d = ["a", "b"]
        other_keys_2d = ["c", "delta_a", "k"]


        for key in first_keys:
            value = get_input(key)
            DATA[key] = value

        DATA["a"] = [0 for x in range(DATA["m"])]
        DATA["b"] = [0 for x in range(DATA["n"])]
        DATA["c"] = [[0] * DATA["n"] for i in range(DATA["m"])]
        DATA["delta_a"] = [[0] * DATA["q"] for i in range(DATA["m"])]
        DATA["k"] = [[0] * DATA["q"] for i in range(DATA["m"])]

        for key in other_keys_1d:
            for i in range(len(DATA[key])):
                value = get_input(key+f"[{i+1}]")
                DATA[key][i] = value

        for key in other_keys_2d:
            for i in range(len(DATA[key])):
                for j in range(len(DATA[key][0])):
                    value = get_input(key+f"[{i+1}{j+1}]")
                    DATA[key][i][j] = value

        return

    def input_ga():
        global GA_DATA
        for key, value in GA_PARAMS.items():
            if key == 'pop_size':
                while True:
                    value = get_input(key+' (парне число!) ')
                    if value%2 == 0:
                        break
            else:
                value = get_input(key)
            GA_DATA[key] = value
        return

    input_basic()
    if getGA: input_ga()

    return

def generate_data(getGA=True):
    def get_input(name):
        while True:
            try:
                value = int(input(f'Введіть {name}: '))
                break
            except ValueError:
                print_error(INCORRECT_DATA)
        return value

    def generate_basic():
        global DATA

        first_keys = ["budget", "m", "n", "q"]
        other_keys_1d = ["a", "b"]
        other_keys_2d = ["c", "delta_a", "k"]

        for key in first_keys:
            limit = get_input(f'максимальне значення для {key}')
            value = random.randrange(1, limit)
            DATA[key] = value

        DATA["a"] = [0 for x in range(DATA["m"])]
        DATA["b"] = [0 for x in range(DATA["n"])]
        DATA["c"] = [[0] * DATA["n"] for i in range(DATA["m"])]
        DATA["delta_a"] = [[0] * DATA["q"] for i in range(DATA["m"])]
        DATA["k"] = [[0] * DATA["q"] for i in range(DATA["m"])]

        for key in other_keys_1d:
            limit = get_input(f'максимальне значення для {key}')
            for i in range(len(DATA[key])):
                value = random.randrange(1, limit)
                DATA[key][i] = value

        for key in other_keys_2d:
            limit = get_input(f'максимальне значення для {key}')
            for i in range(len(DATA[key])):
                for j in range(len(DATA[key][0])):
                    value = random.randrange(1, limit)
                    DATA[key][i][j] = value

        return

    def generate_ga():
        global GA_DATA
        for key, value in GA_PARAMS.items():
            if key == 'pop_size':
                while True:
                    value = get_input(key+' (парне число!) ')
                    if value%2 == 0:
                        break
            else:
                value = get_input(key)
            GA_DATA[key] = value
        return

    generate_basic()
    if getGA: generate_ga()

    return

def read_data():


    return

def setup_task(choice):
    ########## !!!!!!!!!!!!!!
    print_title(MAIN_MENU[choice])
    return


######################### ВИВІД ЗАДАЧІ
def show_task(choice):
    ########## !!!!!!!!!!!!!!
    print_title(MAIN_MENU[choice])
    return

######################### ВИВІД РЕЗУЛЬТАТІВ ЗАДАЧІ
######## ПОКАЗ ТА ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТІВ
def show_task_results(choice):
    print_comment(MAIN_MENU[choice])
    return

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
def setup_experiments(exp_list):
    def setup_1():
        switch_data_menu_page(choice)
        return
    def setup_2():
        switch_data_menu_page(choice)
        return
    def setup_3():
        switch_data_menu_page(choice)
        return

    print_options(DATA_MENU)
    choice = menu_input(DATA_MENU)
    print()

    if exp_list[0]: setup_1()
    if exp_list[1]: setup_2()
    if exp_list[2]: setup_3()

######## ЗАПУСК ЕКСПЕРИМЕНТУ/ІВ
def run_experiments(exp_list):
    def run_1(experiments):
        print_title("Експеримент 1")
        print_subtitle(EXPERIMENT_QUESTION)
        experiments.run_experiment_1()
        print_success("Готово!")
        print()
    def run_2(experiments):
        print_title("Експеримент 2")
        experiments.run_experiment_2()
        print_success("Готово!")
        print()
    def run_3(experiments):
        print_title("Експеримент 3")
        experiments.run_experiment_3()
        print_success("Готово!")
        print()

    setup_experiments(exp_list)

    experiments = ExperimentCreator(output_dir='/')
    if exp_list[0]: run_1(experiments)
    if exp_list[1]: run_2(experiments)
    if exp_list[2]: run_3(experiments)


######## ВИВІД РЕЗУЛЬТАТІВ
def show_experiment_results():
    ########## !!!!!!!!!!!!!!
    print_title('Experiment Results')
    return

@app.command(short_help='налаштування та запуск експериментів')
def experiment_mode(choice):
    print_title(MAIN_MENU[choice])
    print_subtitle(EXPERIMENT_QUESTION)

    print_options(EXPERIMENT_DESC, False)
    exp_choice = menu_input(EXPERIMENT_DESC)

    exp_list = [False, False, False]

    if exp_choice == 0:
        exp_list[0] = True
    elif exp_choice == 1:
        exp_list[1] = True
    elif exp_choice == 2:
        exp_list[2] = True
    else:
        exp_list[0] = True
        exp_list[1] = True
        exp_list[2] = True

    run_experiments(exp_list)
    show_experiment_results()

    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice)


######################### ІНДИВІДУАЛЬНА ЗАДАЧА
######## РОЗВ'ЯЗОК
def solve_task(task_data, ga_data):
    print_title('Жадібний алгоритм')
    greedy_algo = GreedyAlgorithm(task_data)
    greedy_res = greedy_algo.run()
    print_success(f"Обрані сценарії розширення: {greedy_res[0]}")
    print_success(f"Обсяг продукції: {greedy_res[1]}")
    print_success(f"Значення ЦФ: {greedy_res[-1]}")
    print()

    print_title('Генетичний алгоритм')
    genetic_algo = GeneticAlgorithm(task_data,
                                    ga_data["pop_size"],
                                    ga_data["mutation_rate"],
                                    ga_data["elite_percent"],
                                    ga_data["max_stagnation"])
    best_res, _ = genetic_algo.run()
    print_success(f"Обрані сценарії розширення: {best_res.chromosome}")
    print_success(f"Обсяг продукції: {best_res.transport_plan}")
    print_success(f"Значення ЦФ: {best_res.fitness}")
    print()

    return

@app.command(short_help="налаштування та розв'язання індивідуальної задачі")
def task_mode(choice):
    print_title(MAIN_MENU[choice])

    print_options(DATA_MENU)
    choice = menu_input(DATA_MENU)
    print()
    switch_data_menu_page(choice)

    global DATA, GA_DATA
    solve_task(DATA, GA_DATA)

    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice)


######################### ГОЛОВНЕ МЕНЮ
@app.command(short_help="запуск програми")
def start():
    console.print(INFO)
    print_subtitle(TOPIC)
    print()
    print_options()
    choice = menu_input()
    print()
    switch_menu_page(choice)


if __name__ == "__main__":
    app()