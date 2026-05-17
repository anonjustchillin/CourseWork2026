import typer
from rich.console import Console
from rich.table import Table
from all_text import *
from config import *
from defaults import GA_DEFAULTS, get_ga_params, EXPERIMENT_1_DEFAULTS, EXPERIMENT_2_DEFAULTS, EXPERIMENT_3_DEFAULTS
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

# Результати розв'язання
GREEDY_RESULT = None  # (x, y, cost, time)
GA_RESULT = None      # (x, y, cost, time)

INT_ONLY = ["m", "n", "q", "pop_size", "max_stagnation", "K", "fixed_generations"]

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
                if name in INT_ONLY:
                    value = int(input(f'Введіть {name}: '))
                else:
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
    from generator.task_generator import TaskGenerator

    def choose_class(class_type, options):
        """Вибір класу задачі з меню."""
        print_subtitle(f"Оберіть {class_type}-клас:")
        for i, opt in enumerate(options):
            print(f"  {i+1} -- {opt}")
        while True:
            try:
                choice = int(input(CHOICE_STR)) - 1
                if 0 <= choice < len(options):
                    return options[choice]
                print_error(ERROR_MESS)
            except ValueError:
                print_error(ERROR_MESS)

    def get_input(name):
        while True:
            try:
                if name in INT_ONLY:
                    value = int(input(f'Введіть {name}: '))
                else:
                    value = float(input(f'Введіть {name}: '))
                break
            except ValueError:
                print_error(INCORRECT_DATA)
        return value

    def generate_ga():
        global GA_DATA
        # Отримуємо параметри за замовчуванням
        recommended = get_ga_params()

        print_subtitle("Використати параметри GA за замовчуванням?")
        print(f"  1 -- Так: pop_size={recommended['pop_size']}, mutation={recommended['mutation_rate']}, elite={recommended['elite_percent']}, stagnation={recommended['max_stagnation']}")
        print("  2 -- Ні, ввести вручну")
        while True:
            try:
                ga_choice = int(input(CHOICE_STR))
                if ga_choice in [1, 2]:
                    break
                print_error(ERROR_MESS)
            except ValueError:
                print_error(ERROR_MESS)

        if ga_choice == 1:
            for key, value in recommended.items():
                GA_DATA[key] = value
        else:
            for key in GA_PARAMS.keys():
                if key == 'pop_size':
                    while True:
                        value = int(get_input(key + ' (парне число!)'))
                        if value % 2 == 0:
                            break
                        print_error("Має бути парне число!")
                elif key == 'mutation_rate' or key == 'elite_percent':
                    while True:
                        value = get_input(key + ' (від 0 до 1)')
                        if 0 <= value <= 1:
                            break
                        print_error("Має бути від 0 до 1!")
                else:
                    value = int(get_input(key))
                GA_DATA[key] = value
        return

    # Зберігаємо s_class якщо обрано
    s_class_selected = None

    def generate_basic_with_class():
        nonlocal s_class_selected
        global DATA

        r_class = choose_class("R", ["R1", "R2", "R3"])
        b_class = choose_class("B", ["B1", "B2", "B3"])

        print_subtitle("Розмірність задачі:")
        print("  1 -- Обрати S-клас (S1/S2/S3)")
        print("  2 -- Ввести m, n, q вручну")
        while True:
            try:
                size_choice = int(input(CHOICE_STR))
                if size_choice in [1, 2]:
                    break
                print_error(ERROR_MESS)
            except ValueError:
                print_error(ERROR_MESS)

        generator = TaskGenerator()

        if size_choice == 1:
            s_class_selected = choose_class("S", ["S1", "S2", "S3"])
            task_data = generator.generate(r_class, b_class, s_class_name=s_class_selected)
        else:
            m = int(get_input("m (кількість постачальників)"))
            n = int(get_input("n (кількість споживачів)"))
            q = int(get_input("q (кількість сценаріїв)"))
            task_data = generator.generate(r_class, b_class, m=m, n=n, q=q)

        for key, value in task_data.items():
            DATA[key] = value

        print_success(f"Задачу згенеровано: {r_class}-{b_class}, m={DATA['m']}, n={DATA['n']}, q={DATA['q']}")

    generate_basic_with_class()
    if getGA:
        generate_ga()
    print()
    return

def read_data():
    INPUT_DIR = 'input'

    def get_input():
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
        if not files:
            print_error(f"Папка '{INPUT_DIR}' порожня або не містить JSON-файлів")
            return None
        files.sort()
        print_subtitle(f"JSON-файли у папці '{INPUT_DIR}':")
        for i, f in enumerate(files):
            print(f"  {i + 1} -- {f}")
        while True:
            try:
                choice = int(input(CHOICE_STR)) - 1
                if 0 <= choice < len(files):
                    return os.path.join(INPUT_DIR, files[choice])
                print_error(ERROR_MESS)
            except ValueError:
                print_error(ERROR_MESS)

    def get_value(name):
        while True:
            try:
                if name in INT_ONLY:
                    return int(input(f'Введіть {name}: '))
                else:
                    return float(input(f'Введіть {name}: '))
            except ValueError:
                print_error(INCORRECT_DATA)

    def ask_ga():
        global GA_DATA
        recommended = get_ga_params()
        print_subtitle("Використати параметри GA за замовчуванням?")
        print(f"  1 -- Так: pop_size={recommended['pop_size']}, mutation={recommended['mutation_rate']}, elite={recommended['elite_percent']}, stagnation={recommended['max_stagnation']}")
        print("  2 -- Ні, ввести вручну")
        while True:
            try:
                ga_choice = int(input(CHOICE_STR))
                if ga_choice in [1, 2]:
                    break
                print_error(ERROR_MESS)
            except ValueError:
                print_error(ERROR_MESS)

        if ga_choice == 1:
            for key, value in recommended.items():
                GA_DATA[key] = value
        else:
            for key in GA_PARAMS.keys():
                if key == 'pop_size':
                    while True:
                        value = int(get_value(key + ' (парне число!)'))
                        if value % 2 == 0:
                            break
                        print_error("Має бути парне число!")
                elif key in ('mutation_rate', 'elite_percent'):
                    while True:
                        value = get_value(key + ' (від 0 до 1)')
                        if 0 <= value <= 1:
                            break
                        print_error("Має бути від 0 до 1!")
                else:
                    value = int(get_value(key))
                GA_DATA[key] = value

    global DATA, GA_DATA

    data_path = get_input()
    if data_path is None:
        return

    loaded = False
    with open(data_path, 'r') as file:
        try:
            data = json.load(file)
            data_keys = ["m", "n", "q", "a", "b", "c", "delta_a", "k", "budget"]

            for key in data_keys:
                if key not in data:
                    print_error(f"Відсутній ключ: {key}")
                    return

            if data["m"] <= 0 or data["n"] <= 0 or data["q"] <= 0:
                print_error("m, n, q мають бути > 0")
                return

            if len(data["c"]) != data["m"] or len(data["c"][0]) != data["n"]:
                print_error("Неправильний розмір матриці c")
                return

            if len(data["delta_a"]) != data["m"] or len(data["delta_a"][0]) != data["q"]:
                print_error("Неправильний розмір матриці delta_a")
                return

            if len(data["k"]) != data["m"] or len(data["k"][0]) != data["q"]:
                print_error("Неправильний розмір матриці k")
                return

            for key in data_keys:
                DATA[key] = data[key]

            print_success(f"Дані завантажено: m={DATA['m']}, n={DATA['n']}, q={DATA['q']}")
            loaded = True

        except json.decoder.JSONDecodeError:
            print_error("Помилка читання JSON файлу")
        except KeyError as e:
            print_error(f"Відсутній ключ у файлі: {e}")

    if loaded:
        print()
        ask_ga()

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
def save_results_to_file():
    """Зберігає результати обох алгоритмів у JSON-файл."""
    results = {}

    if GREEDY_RESULT:
        greedy_x, greedy_y, greedy_cost, greedy_time = GREEDY_RESULT
        results["greedy"] = {
            "transport_plan": greedy_x,
            "scenarios": greedy_y,
            "objective_value": greedy_cost,
            "time": greedy_time,
        }

    if GA_RESULT:
        ga_x, ga_y, ga_cost, ga_time = GA_RESULT
        results["genetic"] = {
            "transport_plan": ga_x,
            "scenarios": ga_y,
            "objective_value": ga_cost,
            "time": ga_time,
        }

    while True:
        filename = input("Введіть назву файлу для збереження результатів: ").strip()
        if filename:
            break
        print_error(INCORRECT_DATA)

    if not filename.endswith(".json"):
        filename += ".json"

    if not os.path.exists(DEFAULT_FOLDER):
        os.mkdir(DEFAULT_FOLDER)

    file_path = os.path.join(DEFAULT_FOLDER, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)

    print_success(f"Результати збережено: {file_path}")


def show_task_results(choice):
    print_title(MAIN_MENU[choice])

    if GREEDY_RESULT is None and GA_RESULT is None:
        print_error("Задачу ще не розв'язано. Спочатку оберіть пункт 2.")
        print()
    else:
        # Вивід результатів жадібного алгоритму
        if GREEDY_RESULT:
            greedy_x, greedy_y, greedy_cost, greedy_time = GREEDY_RESULT
            print_title('Жадібний алгоритм')
            print_scenarios_table(greedy_y, "Обрані сценарії")
            print()
            print_transport_plan(greedy_x, "Транспортний план")
            print()

        # Вивід результатів GA
        if GA_RESULT:
            ga_x, ga_y, ga_cost, ga_time = GA_RESULT
            print_title('Генетичний алгоритм')
            print_scenarios_table(ga_y, "Обрані сценарії")
            print()
            print_transport_plan(ga_x, "Транспортний план")
            print()

        # Порівняльна таблиця
        if GREEDY_RESULT and GA_RESULT:
            greedy_cost = GREEDY_RESULT[2]
            greedy_time = GREEDY_RESULT[3]
            ga_cost = GA_RESULT[2]
            ga_time = GA_RESULT[3]
            print_comparison_table(greedy_cost, greedy_time, ga_cost, ga_time)

        # Запит на збереження результатів у файл
        print_subtitle("Зберегти результати у файл?")
        print("  1 -- Так")
        print("  2 -- Ні")
        while True:
            try:
                save_choice = int(input(CHOICE_STR))
                if save_choice in [1, 2]:
                    break
                print_error(ERROR_MESS)
            except ValueError:
                print_error(ERROR_MESS)

        if save_choice == 1:
            save_results_to_file()
        print()

    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice, True)
    return

######################### ЕКСПЕРИМЕНТИ
######## ОТРИМАННЯ ДАНИХ
def setup_experiments(exp_list, dir_only=False):
    def get_input(name):
        while True:
            try:
                if name in INT_ONLY:
                    value = int(input(f'Введіть {name}: '))
                else:
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
                EXP_DATA_2[key] = [0 for i in range(pop_size_count)]
                for i in range(pop_size_count):
                    while True:
                        value = get_input(f'{key}[{i}] (парне число!) ')
                        if value%2 == 0:
                            break
                    EXP_DATA_2[key][i] = int(value)
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
                if exp_list[1] and not exp_list[0] and not exp_list[2]:
                    value = 0
                else:
                    while True:
                        value = get_input(key+' (парне число!) ')
                        if value%2 == 0:
                            break
            elif key == 'mutation_rate' or key == 'elite_percent':
                while True:
                    value = get_input(key+' (від 0 до 1) ')
                    if 0 <= value <= 1:
                        break
            elif key == 'max_stagnation' and (exp_list[0] and not exp_list[1] and not exp_list[2]):
                value = 0
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
                    os.mkdir(data_path)
                    break
                else:
                    break
            except ValueError or PermissionError:
                print_error(ERROR_MESS)
        OUTPUT_DIR = data_path
        return

    if dir_only:
        get_output_dir()
    else:
        if exp_list[0]: setup_1()
        if exp_list[1]: setup_2()
        if exp_list[2]: setup_3()
        setup_ga()
        get_output_dir()

######## ЗАПУСК ЕКСПЕРИМЕНТУ/ІВ
def run_experiments(exp_list, default_params):
    def run_1(experiments):
        print_title("Експеримент 1")
        for key, item in EXP_DATA_1.items():
            print(f'{key}: {item}')
        for key, item in EXP_GA_DATA.items():
            print(f'{key}: {item}')
        print_subtitle(EXPERIMENT_RUN)
        experiments.run_experiment_1()
        print_success(EXPERIMENT_DONE)
        print()
    def run_2(experiments):
        print_title("Експеримент 2")
        for key, item in EXP_DATA_2.items():
            print(f'{key}: {item}')
        for key, item in EXP_GA_DATA.items():
            print(f'{key}: {item}')
        print_subtitle(EXPERIMENT_RUN)
        experiments.run_experiment_2()
        print_success(EXPERIMENT_DONE)
        print()
    def run_3(experiments):
        print_title("Експеримент 3")
        for key, item in EXP_DATA_3.items():
            print(f'{key}: {item}')
        for key, item in EXP_GA_DATA.items():
            print(f'{key}: {item}')
        print_subtitle(EXPERIMENT_RUN)
        experiments.run_experiment_3()
        print_success(EXPERIMENT_DONE)
        print()

    if not default_params:
        setup_experiments(exp_list)
    else:
        setup_experiments(exp_list, True)

    if len(EXP_DATA_1) != 0 and len(EXP_DATA_2) == 0 and len(EXP_DATA_3) == 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_1=EXP_DATA_1,
                                        ga_params_1=EXP_GA_DATA)
    elif len(EXP_DATA_1) == 0 and len(EXP_DATA_2) != 0 and len(EXP_DATA_3) == 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_2=EXP_DATA_2,
                                        ga_params_2=EXP_GA_DATA)
    elif len(EXP_DATA_1) == 0 and len(EXP_DATA_2) == 0 and len(EXP_DATA_3) != 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_3=EXP_DATA_3,
                                        ga_params_3=EXP_GA_DATA)
    elif len(EXP_DATA_1) != 0 and len(EXP_DATA_2) != 0 and len(EXP_DATA_3) != 0:
        experiments = ExperimentCreator(output_dir=OUTPUT_DIR,
                                        params_1=EXP_DATA_1,
                                        params_2=EXP_DATA_2,
                                        params_3=EXP_DATA_3,
                                        ga_params_1=EXP_GA_DATA,
                                        ga_params_2=EXP_GA_DATA,
                                        ga_params_3=EXP_GA_DATA)
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

    # Питаємо про параметри
    print()
    print_subtitle("Параметри експерименту")
    print_options(PARAMS_CHOICE, False)
    params_choice = menu_input(PARAMS_CHOICE)
    default_params = (params_choice == 0)

    run_experiments(exp_list, default_params)
    show_experiment_results()

    print_options(RETURN_TO_MAIN)
    choice = menu_input(RETURN_TO_MAIN)
    switch_menu_page(choice, True)


######################### ІНДИВІДУАЛЬНА ЗАДАЧА
######## РОЗВ'ЯЗОК
def format_scenarios(y_matrix):
    """Форматує матрицю сценаріїв у читабельний вигляд."""
    result = []
    for i, row in enumerate(y_matrix):
        selected = [t + 1 for t, val in enumerate(row) if val == 1]
        if selected:
            result.append(f"Постачальник {i + 1}: сценарій {selected[0]}")
        else:
            result.append(f"Постачальник {i + 1}: без розширення")
    return result


def print_transport_plan(x_matrix, title="Транспортний план"):
    """Виводить транспортний план у компактному вигляді."""
    print_subtitle(title)

    # Збираємо ненульові перевезення
    shipments = []
    for i, row in enumerate(x_matrix):
        for j, val in enumerate(row):
            if val > 0:
                shipments.append(f"A{i+1}→B{j+1}: {int(val)}")

    # Виводимо по 4 в рядок
    if shipments:
        for i in range(0, len(shipments), 4):
            chunk = shipments[i:i+4]
            print("  " + "   ".join(chunk))
    else:
        print("  (немає перевезень)")


def print_scenarios_table(y_matrix, title="Обрані сценарії"):
    """Виводить обрані сценарії у вигляді таблиці."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Постачальник", style="bold")
    table.add_column("Сценарій", justify="center")

    for i, row in enumerate(y_matrix):
        selected = [t + 1 for t, val in enumerate(row) if val == 1]
        scenario_str = str(selected[0]) if selected else "-"
        table.add_row(f"A{i + 1}", scenario_str)

    console.print(table)


def solve_task(task_data, ga_data):
    import time
    global GREEDY_RESULT, GA_RESULT

    # Жадібний алгоритм
    print_title('Жадібний алгоритм')
    start_time = time.time()
    greedy_algo = GreedyAlgorithm(task_data)
    greedy_res = greedy_algo.run()
    greedy_time = time.time() - start_time

    if greedy_res:
        greedy_x, greedy_y, greedy_cost = greedy_res
        GREEDY_RESULT = (greedy_x, greedy_y, greedy_cost, greedy_time)
        print_scenarios_table(greedy_y, "Жадібний: обрані сценарії")
        print()
        print_transport_plan(greedy_x, "Жадібний: транспортний план")
        print()
        print_success(f"Жадібний: ЦФ = {greedy_cost:.0f}, час = {greedy_time:.3f} с")
    else:
        greedy_cost = None
        GREEDY_RESULT = None
        print_error("Розв'язок не знайдено")
    print()

    # Генетичний алгоритм
    print_title('Генетичний алгоритм')
    print_comment(f"Параметри: pop_size={ga_data['pop_size']}, mutation={ga_data['mutation_rate']}, elite={ga_data['elite_percent']}, stagnation={ga_data['max_stagnation']}")
    start_time = time.time()
    genetic_algo = GeneticAlgorithm(task_data,
                                    ga_data["pop_size"],
                                    ga_data["mutation_rate"],
                                    ga_data["elite_percent"],
                                    ga_data["max_stagnation"])
    ga_x, ga_y, ga_cost = genetic_algo.run()
    ga_time = time.time() - start_time

    GA_RESULT = (ga_x, ga_y, ga_cost, ga_time)

    print_scenarios_table(ga_y, "GA: обрані сценарії")
    print()
    print_transport_plan(ga_x, "GA: транспортний план")
    print()
    print_success(f"GA: ЦФ = {ga_cost:.0f}, час = {ga_time:.3f} с")
    print()

    # Порівняльна таблиця
    print_comparison_table(greedy_cost, greedy_time, ga_cost, ga_time)

    return


def print_comparison_table(greedy_cost, greedy_time, ga_cost, ga_time):
    """Виводить порівняльну таблицю результатів."""
    print_title('Порівняння результатів')
    comparison = Table(show_header=True, header_style="bold magenta")
    comparison.add_column("Алгоритм", style="bold")
    comparison.add_column("Значення ЦФ", justify="right")
    comparison.add_column("Час (с)", justify="right")
    comparison.add_column("", justify="center")

    greedy_cost_str = f"{greedy_cost:.0f}" if greedy_cost else "N/A"

    # Визначаємо переможця
    if greedy_cost and ga_cost:
        if greedy_cost < ga_cost:
            greedy_mark, ga_mark = "[green]winner[/green]", ""
        elif ga_cost < greedy_cost:
            greedy_mark, ga_mark = "", "[green]winner[/green]"
        else:
            greedy_mark, ga_mark = "[yellow]tie[/yellow]", "[yellow]tie[/yellow]"
    else:
        greedy_mark, ga_mark = "", ""

    comparison.add_row("Жадібний", greedy_cost_str, f"{greedy_time:.3f}", greedy_mark)
    comparison.add_row("Генетичний", f"{ga_cost:.0f}", f"{ga_time:.3f}", ga_mark)

    console.print(comparison)
    print()

@app.command(short_help="налаштування та розв'язання індивідуальної задачі")
def task_mode(choice):
    print_title(MAIN_MENU[choice])

    global DATA, GA_DATA

    if len(DATA) == 0 and len(GA_DATA) == 0:
        print_options(DATA_MENU)
        choice = menu_input(DATA_MENU)
        print()
        switch_data_menu_page(choice)

    for key, item in DATA.items():
        print(f'{key}: {item}')
    for key, item in GA_DATA.items():
        print(f'{key}: {item}')
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