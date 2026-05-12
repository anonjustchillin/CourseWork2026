import typer
from rich.console import Console
from rich.table import Table
from all_text import *
from config import *
from experiments.experiment_creator import ExperimentCreator
from genetic_algorithm.genetic_algo import GeneticAlgorithm
from greedy_algorithm.greedy_algo import GreedyAlgorithm
import random
import os
import json

console = Console()
app = typer.Typer()

CURR_MENU = -1

DATA = {}
GA_DATA = {}
EXP_DATA_1 = {}
EXP_DATA_2 = {}
EXP_DATA_3 = {}
EXP_GA_DATA = {}

DEFAULT_FOLDER = 'output'
OUTPUT_DIR = ''


def switch_menu_page(choice, short=False):
    global CURR_MENU
    CURR_MENU = choice

    if not short:
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
            exit()
    else:
        if CURR_MENU == 0:
            start()
        else:
            exit()

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
                print_error(ERROR_MESS)
            else:
                break
        except ValueError:
            print_error(ERROR_MESS)
    return choice


@app.command(short_help='інформація про авторів')
def about():
    console.print(INFO)

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
            value = int(value)
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
            elif key == 'mutation_rate' or key == 'elite_percent':
                while True:
                    value = get_input(key+' (від 0 до 1) ')
                    if 0 <= value <= 1:
                        break
            else:
                value = get_input(key)
            GA_DATA[key] = value
        return

    input_basic()
    if getGA: input_ga()
    print()
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
            if key == 'pop_size' or 'max_stagnation':
                limit = get_input(f'максимальне значення для {key}')
                if key == 'pop_size':
                    while True:
                        value = random.randrange(1, limit)
                        if value%2 == 0:
                            break
                else:
                    value = random.randrange(1, limit)
            else:
                value = random.random()
                value = round(value, 2)
            GA_DATA[key] = value
        return

    generate_basic()
    if getGA: generate_ga()
    print()
    return

def read_data():
    def get_input():
        while True:
            try:
                data_path = input(f'Введіть шлях до json-файлу з даними: ')
                if not os.path.exists(data_path):
                    print_error(NO_FILE)
                    continue
                break
            except ValueError or FileNotFoundError:
                print_error(NO_FILE)

        return data_path

    global DATA, GA_PARAMS

    data_path = get_input()

    with open(data_path, 'r') as file:
        try:
            data = json.load(file)
            data_keys = ["m", "n", "q", "a", "b", "c", "delta_a", "k", "budget"]
            ga_data_keys = ["pop_size", "mutation_rate", "elite_percent", "max_stagnation"]

            for key in data_keys:
                if key == "m" or key == "n" or key == "q":
                    if data[key] <= 0:
                        print_error(INCORRECT_DATA)
                        start()
                elif key == "c":
                    if len(data[key]) != data["m"]:
                        print_error(INCORRECT_DATA)
                        start()
                    elif len(data[key][0]) != data["n"]:
                        print_error(INCORRECT_DATA)
                        start()
                elif key == "delta_a":
                    if len(data[key]) != data["m"]:
                        print_error(INCORRECT_DATA)
                        start()
                    elif len(data[key][0]) != data["q"]:
                        print_error(INCORRECT_DATA)
                        start()
                elif key == "k":
                    if len(data[key]) != data["m"]:
                        print_error(INCORRECT_DATA)
                        start()
                    elif len(data[key][0]) != data["q"]:
                        print_error(INCORRECT_DATA)
                        start()
                else:
                    DATA[key] = data[key]

            for key in ga_data_keys:
                if key == "pop_size":
                    if data[key] % 2 != 0:
                        print_error(INCORRECT_DATA)
                        start()
                elif key == 'mutation_rate' or key == 'elite_percent':
                    if 0 > data[key] > 1:
                        print_error(INCORRECT_DATA)
                        start()
                GA_DATA[key] = data[key]

        except json.decoder.JSONDecodeError:
            print_error(NO_DATA)

    print()
    return

def setup_task(choice):
    print_title(MAIN_MENU[choice])

    print_options(DATA_MENU)
    choice = menu_input(DATA_MENU)
    print()
    switch_data_menu_page(choice)

    print_success("Дані було збережено")
    print()

    print_options(RETURN_TO_MAIN)
    choice = menu_input(DATA_MENU)
    print()
    switch_menu_page(choice, True)

    return


######################### ВИВІД ЗАДАЧІ
def show_task(choice):
    ########## !!!!!!!!!!!!!!
    print_title(MAIN_MENU[choice])

    if len(DATA) == 0 and len(GA_DATA) == 0:
        print_error(NO_DATA)
        start()
    else:
        print_subtitle('ПАРАМЕТРИ ЗАДАЧІ')
        for key, value in DATA.items():
            print(f'{key} = {value}')
        for key, value in GA_DATA.items():
            print(f'{key} = {value}')
        print()
        print_options(RETURN_TO_MAIN)
        choice = menu_input(RETURN_TO_MAIN)
        switch_menu_page(choice, True)
    return

######################### ВИВІД РЕЗУЛЬТАТІВ ЗАДАЧІ
######## ПОКАЗ ТА ЗБЕРЕЖЕННЯ РЕЗУЛЬТАТІВ
def show_task_results(choice):
    print_title(MAIN_MENU[choice])

    print()
    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice, True)
    return

######################### ЕКСПЕРИМЕНТИ
######## ОТРИМАННЯ ДАНИХ
def setup_experiments(exp_list):
    def get_input(name):
        while True:
            try:
                value = float(input(f'Введіть {name}: '))
                break
            except ValueError:
                print_error(INCORRECT_DATA)
        return value

    def setup_1():
        print_subtitle("Експеримент 1. Налаштування")
        global EXP_DATA_1

        for key, value in EXPERIMENT_PARAMS_1.items():
            value = get_input(key)
            EXP_DATA_1[key] = value

        print()
        return

    def setup_2():
        print_subtitle("Експеримент 2. Налаштування")
        global EXP_DATA_2

        for key, value in EXPERIMENT_PARAMS_2.items():
            if key == 'pop_size_list':
                while True:
                    pop_size_count = get_input('кількість значень pop_size для аналізу')
                    pop_size_count = int(pop_size_count)
                    if pop_size_count < 0:
                        print_error(INCORRECT_DATA)
                        continue
                    break
                EXP_DATA_2[key] = [0 for x in range(pop_size_count)]
                for i in range(pop_size_count):
                    while True:
                        value = get_input(f'{key}[{i}] (парне число!) ')
                        if value%2 == 0:
                            break
                    EXP_DATA_2[key][i] = value
                EXP_DATA_2[key].sort()
            else:
                value = get_input(key)
            EXP_DATA_2[key] = value

        print()
        return

    def setup_3():
        print_subtitle("Експеримент 3. Налаштування")
        global EXP_DATA_3

        for key, value in EXPERIMENT_PARAMS_3.items():
            if key == 'v_scale':
                while True:
                    v_scale_count = get_input('кількість значень v_scale для аналізу')
                    v_scale_count = int(v_scale_count)
                    if v_scale_count < 0:
                        print_error(INCORRECT_DATA)
                        continue
                    break
                EXP_DATA_3[key] = [0 for x in range(v_scale_count)]
                for i in range(v_scale_count):
                    while True:
                        value = get_input(f'{key}[{i}] ')
                        if value <= 0:
                            print_error(INCORRECT_DATA)
                            continue
                        break
                    EXP_DATA_3[key][i] = value
                EXP_DATA_3[key].sort()
            else:
                value = get_input(key)
            EXP_DATA_3[key] = value

        print()
        return

    def setup_ga():
        print_subtitle("Базові параметри для генетичного алгоритму")
        global EXP_GA_DATA

        for key, value in GA_PARAMS.items():
            if key == 'pop_size':
                while True:
                    value = get_input(key+' (парне число!) ')
                    if value%2 == 0:
                        break
            elif key == 'mutation_rate' or key == 'elite_percent':
                while True:
                    value = get_input(key+' (від 0 до 1) ')
                    if 0 <= value <= 1:
                        break
            else:
                value = get_input(key)
            EXP_GA_DATA[key] = value

        print()
        return

    def get_output_dir():
        global OUTPUT_DIR
        while True:
            try:
                data_path = input(f'Введіть назву папки для збереження даних: ')
                data_path = os.path.join(DEFAULT_FOLDER, data_path)
                if not os.path.exists(data_path):
                        print_error(ERROR_MESS)
                else:
                    break
            except ValueError:
                print_error(ERROR_MESS)
        OUTPUT_DIR = data_path
        return

    if exp_list[0]: setup_1()
    if exp_list[1]: setup_2()
    if exp_list[2]: setup_3()
    setup_ga()
    get_output_dir()

######## ЗАПУСК ЕКСПЕРИМЕНТУ/ІВ
def run_experiments(exp_list, default_params):
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

    if not default_params:
        setup_experiments(exp_list)

    if len(EXP_DATA_1) != 0 and len(EXP_DATA_2) == 0 and len(EXP_DATA_3) == 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_1=EXP_DATA_1,
                                        pop_size=EXP_GA_DATA["pop_size"],
                                        elite_percent=EXP_GA_DATA["elite_percent"],
                                        mutation_rate=EXP_GA_DATA["mutation_rate"],
                                        max_stagnation=EXP_GA_DATA["max_stagnation"])
    elif len(EXP_DATA_1) == 0 and len(EXP_DATA_2) != 0 and len(EXP_DATA_3) == 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_2=EXP_DATA_2,
                                        pop_size=EXP_GA_DATA["pop_size"],
                                        elite_percent=EXP_GA_DATA["elite_percent"],
                                        mutation_rate=EXP_GA_DATA["mutation_rate"],
                                        max_stagnation=EXP_GA_DATA["max_stagnation"])
    elif len(EXP_DATA_1) == 0 and len(EXP_DATA_2) == 0 and len(EXP_DATA_3) != 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_3=EXP_DATA_3,
                                        pop_size=EXP_GA_DATA["pop_size"],
                                        elite_percent=EXP_GA_DATA["elite_percent"],
                                        mutation_rate=EXP_GA_DATA["mutation_rate"],
                                        max_stagnation=EXP_GA_DATA["max_stagnation"])
    elif len(EXP_DATA_1) != 0 and len(EXP_DATA_2) != 0 and len(EXP_DATA_3) != 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_1=EXP_DATA_1,
                                        params_2=EXP_DATA_2,
                                        params_3=EXP_DATA_3,
                                        pop_size=EXP_GA_DATA["pop_size"],
                                        elite_percent=EXP_GA_DATA["elite_percent"],
                                        mutation_rate=EXP_GA_DATA["mutation_rate"],
                                        max_stagnation=EXP_GA_DATA["max_stagnation"])
    else:
        print_comment('параметри за замовчуванням')
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR)

    if exp_list[0]: run_1(experiments)
    if exp_list[1]: run_2(experiments)
    if exp_list[2]: run_3(experiments)


######## ВИВІД РЕЗУЛЬТАТІВ
def show_experiment_results():
    ########## !!!!!!!!!!!!!!
    print_title('Результати експериментів')

    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice, True)

@app.command(short_help='налаштування та запуск експериментів')
def experiment_mode(choice):
    print_title(MAIN_MENU[choice])
    print_subtitle(EXPERIMENT_QUESTION)

    print_options(EXPERIMENT_DESC, False)
    exp_choice = menu_input(EXPERIMENT_DESC)

    exp_list = [False, False, False]
    default_params = False

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

    run_experiments(exp_list, default_params)
    show_experiment_results()

    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice, True)


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

    global DATA, GA_DATA

    if len(DATA) == 0 and len(GA_DATA) == 0:
        print_options(DATA_MENU)
        choice = menu_input(DATA_MENU)
        print()
        switch_data_menu_page(choice)

    solve_task(DATA, GA_DATA)

    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice, True)


######################### ГОЛОВНЕ МЕНЮ
@app.command(short_help="запуск програми")
def start():
    print()
    console.print(INFO)
    print_subtitle(TOPIC)
    print()
    print_options()
    choice = menu_input()
    print()
    switch_menu_page(choice)


if __name__ == "__main__":
    app()