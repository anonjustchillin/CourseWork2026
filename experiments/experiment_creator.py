import time
from datetime import datetime
from multiprocessing import Pool
import matplotlib.pyplot as plt
import os
import numpy as np
import statistics as stats
from defaults import EXPERIMENT_1_DEFAULTS, EXPERIMENT_2_DEFAULTS, EXPERIMENT_3_DEFAULTS, GA_DEFAULTS
from genetic_algorithm.genetic_algo import GeneticAlgorithm
from greedy_algorithm.greedy_algo import GreedyAlgorithm
from generator.task_generator import TaskGenerator


def _exp2_worker(args):
    """Один прогін експерименту 2: одна задача (class, k), всі pop_size на ній.

    Виконується в окремому процесі, тому має бути на рівні модуля (picklable).
    """
    (class_idx, r_class, b_class, s_class, pop_size_list,
     mutation_rate, elite_percent, max_stagnation) = args

    curr_task_data = TaskGenerator().generate(r_class, b_class, s_class_name=s_class)

    fitness_by_pop = {}
    for pop_size_i in pop_size_list:
        ga = GeneticAlgorithm(curr_task_data, pop_size_i,
                              mutation_rate, elite_percent, max_stagnation)
        best_res, _ = ga.run()
        fitness_by_pop[pop_size_i] = best_res.fitness
    return class_idx, fitness_by_pop


"""
Загалом планується проведення трьох експериментів:
1. визначення значення параметра умови завершення роботи алгоритму GA (t) в залежності від розмірності вхідної задачі;
2. дослідження впливу кількості особин в популяції (I) на точність роботи GA;
3. дослідження впливу розмірності задач на точність та час роботи жадібного та генетичного GA алгоритмів.
"""

DPI = 300

class ExperimentCreator:
    def __init__(self, output_dir,
                 params_1=EXPERIMENT_1_DEFAULTS,
                 params_2=EXPERIMENT_2_DEFAULTS,
                 params_3=EXPERIMENT_3_DEFAULTS,
                 ga_params=GA_DEFAULTS):
        # Параметри експерименту 1
        self.fixed_generations = params_1["fixed_generations"]

        # Параметри експерименту 2
        self.pop_size_list = params_2["pop_size_list"]
        self.K_2 = params_2["K"]

        # Параметри експерименту 3
        self.v_scale = params_3["v_scale"]
        self.K_3 = params_3["K"]

        # Параметри GA
        self.pop_size = ga_params["pop_size"]
        self.elite_percent = ga_params["elite_percent"]
        self.mutation_rate = ga_params["mutation_rate"]
        self.max_stagnation = ga_params["max_stagnation"]

        self.time_start = 0
        self.time_elapsed = 0

        self.output_dir = output_dir

        # Timestamp для унікальних імен файлів (створюється один раз при ініціалізації)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _get_plot_path(self, name):
        """Генерує шлях до файлу з timestamp."""
        filename = f"{name}_{self.timestamp}.png"
        return os.path.join(self.output_dir, filename)

    def start_time(self):
        self.time_start = time.time()

    def end_time(self):
        time_end = time.time()
        self.time_elapsed = time_end - self.time_start

    def run_experiment_1(self, r_class_name="R2", b_class_name="B2"):
        #print('Експеримент 1 !!!!')
        def trial(r_class_name, b_class_name, s_class_name):
            """
            Параметри:
            class_name (str): Назва класу (наприклад, "R1-B1").
            s_class_name (str): Назва S класу (наприклад, "S1").
            fixed_generations (int): Максимальна кількість ітерацій (режим GA_fixed для експериментів).
            pop_size (int): Розмір популяції (парне число).
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
            """

            curr_task = TaskGenerator()
            curr_task_data = curr_task.generate(r_class_name, b_class_name, s_class_name=s_class_name)
            #print('A task was generated')
            #print(curr_task_data)

            self.fixed_generations = int(self.fixed_generations)

            curr_solution = GeneticAlgorithm(curr_task_data, self.pop_size, self.mutation_rate, self.elite_percent, self.max_stagnation)
            _, record_log = curr_solution.run(self.fixed_generations)

            return record_log

        def plot_result(x_max, y, name=''):
            x = np.arange(0, x_max+1, 1)
            plt.figure(figsize=(12, 5))
            plt.plot(x, y)
            plt.title(f'Зміна значення ЦФ від кількості ітерації генетичного алгоритму ({l})')
            plt.xlabel("Номер ітерації")
            plt.ylabel("Значення ЦФ")
            plt.grid(alpha=0.3)

            plot_path = self._get_plot_path("experiment_1_" + name)
            plt.savefig(plot_path, dpi=DPI)

            plt.show()
            plt.close()
            return

        results = {}
        for l in ["S1", "S2", "S3"]:
            print(f'l={l}')
            record_log = trial(r_class_name, b_class_name, l)
            plot_result(self.fixed_generations, record_log, l)
            results[l] = record_log

        return results

    def run_experiment_2(self):
        #print('Експеримент 2 !!!!')
        def plot_result(data, class_names, name=''):
            x_classes = [class_name[0]+"-"+class_name[1] for class_name in class_names]
            x = np.arange(len(x_classes))

            width = 0.25
            multiplier = 0

            fig, ax = plt.subplots(figsize=(14, 6), layout='constrained')
            for pop_size, values in data.items():
                offset = width * multiplier
                rects = ax.bar(x+offset, values, width, label=pop_size)
                ax.bar_label(rects, padding=3, fontsize=8)
                multiplier += 1

            ax.set_title("Вплив кількості особин в популяції (I) на ЦФ генетичного алгоритму")
            ax.set_ylabel("Значення ЦФ")
            ax.set_xticks(x + width, x_classes)
            ax.legend(loc='lower right')

            plot_path = self._get_plot_path(name)
            plt.savefig(plot_path, dpi=DPI)

            plt.show()
            plt.close()
            return
        """
            Параметри:
            pop_size_list (list of int): Масив розмірів популяції (парні числа).
            max_stagnation (int): Максимальна кількість ітерацій без покращення.
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
        """

        s_class_name = "S2"
        K = self.K_2

        class_names = [["R1","B1"],
                       ["R3","B1"],
                       ["R1","B3"],
                       ["R3","B3"],
                       ["R2","B2"]]
        pop_size_labels = ["I="+str(i) for i in self.pop_size_list]
        results = {i: [] for i in pop_size_labels}

        jobs = []
        for class_idx, (r_class_name, b_class_name) in enumerate(class_names):
            for k in range(K):
                jobs.append((class_idx, r_class_name, b_class_name, s_class_name,
                             self.pop_size_list, self.mutation_rate,
                             self.elite_percent, self.max_stagnation))

        # results_k_by_class[class_idx][pop_size] -> список значень fitness
        results_k_by_class = {
            ci: {p: [] for p in self.pop_size_list} for ci in range(len(class_names))
        }

        with Pool(18) as pool:
            for class_idx, fitness_by_pop in pool.imap_unordered(_exp2_worker, jobs):
                for pop_size_i, fit in fitness_by_pop.items():
                    results_k_by_class[class_idx][pop_size_i].append(fit)

        # збираємо результати в порядку класів (процеси завершуються не по черзі)
        for class_idx in range(len(class_names)):
            for pop_size_i in self.pop_size_list:
                results["I="+str(pop_size_i)].append(
                    stats.fmean(results_k_by_class[class_idx][pop_size_i])
                )

        plot_result(results, class_names, f"experiment_2")

        return

    def run_experiment_3(self, r_class_name="R2", b_class_name="B2"):
        #print('Експеримент 3 !!!!')
        def plot_result(x, y1, y2, y_name='', name=''):
            plt.figure(figsize=(12, 5))
            plt.plot(x, y1, label='Жадібний алгоритм')
            plt.plot(x, y2, label='Генетичний алгоритм')
            plt.title("Вплив розмірності задачі на "+str.lower(y_name)+" алгоритмів")
            plt.xlabel("Коефіцієнт масштабу v")
            plt.ylabel(y_name)
            plt.legend()
            plt.grid(alpha=0.3)

            plot_path = self._get_plot_path(name)
            plt.savefig(plot_path, dpi=DPI)

            plt.show()
            plt.close()
            return
        """
            Параметри (для GA):
            pop_size (int): Розмір популяції (парне число).
            max_stagnation (int): Максимальна кількість ітерацій без покращення.
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
        """

        base_m = 5
        base_n = 10
        base_q = 2
        K = self.K_3

        greedy_time = []
        genetic_time = []

        greedy_results = []
        genetic_results = []

        for v in self.v_scale:
            #print(f'v={v}')
            m = int(base_m*v)
            n = int(base_n*v)
            q = int(base_q*v)

            greedy_time_k = []
            genetic_time_k = []

            greedy_results_k = []
            genetic_results_k = []

            for k in range(1, K+1):
                #print(f'k={k}')
                curr_task = TaskGenerator()
                curr_task_data = curr_task.generate(r_class_name, b_class_name, m=m, n=n, q=q)

                self.start_time()
                greedy_algo = GreedyAlgorithm(curr_task_data)
                greedy_res = greedy_algo.run()
                self.end_time()
                greedy_time_k.append(self.time_elapsed)

                greedy_results_k.append(greedy_res[-1])

                #if greedy_res is None:
                #    print('NONE!!!!')

                self.start_time()
                genetic_algo = GeneticAlgorithm(curr_task_data, self.pop_size, self.mutation_rate, self.elite_percent, self.max_stagnation)
                best_res, _ = genetic_algo.run()
                self.end_time()
                genetic_time_k.append(self.time_elapsed)
                genetic_results_k.append(best_res.fitness)

            greedy_time.append(sum(greedy_time_k)/K)
            genetic_time.append(sum(genetic_time_k)/K)

            greedy_results.append(sum(greedy_results_k)/K)
            genetic_results.append(sum(genetic_results_k)/K)

        plot_result(self.v_scale, greedy_time, genetic_time, y_name='час роботи', name=f"experiment_3_greedy")
        plot_result(self.v_scale, greedy_results, genetic_results, y_name='точність', name=f"experiment_3_genetic")


        return

    def run_all(self):
        self.run_experiment_1()
        self.run_experiment_2()
        self.run_experiment_3()
