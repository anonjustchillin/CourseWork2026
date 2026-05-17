import time
from datetime import datetime
from multiprocessing import Pool
import matplotlib.pyplot as plt
import os
import numpy as np
import statistics as stats
from defaults import (EXPERIMENT_1_DEFAULTS, EXPERIMENT_2_DEFAULTS, EXPERIMENT_3_DEFAULTS,
                      GA_EXPERIMENT_1_DEFAULTS, GA_EXPERIMENT_2_DEFAULTS, GA_EXPERIMENT_3_DEFAULTS)
from genetic_algorithm.genetic_algo import GeneticAlgorithm
from greedy_algorithm.greedy_algo import GreedyAlgorithm
from generator.task_generator import TaskGenerator


def _exp1_worker(args):
    """Один прогін експерименту 1: одна задача (S-клас), GA на fixed_generations ітерацій.

    Виконується в окремому процесі, тому має бути на рівні модуля (picklable).
    """
    (s_class, r_class, b_class, fixed_generations,
     pop_size, mutation_rate, elite_percent) = args

    curr_task_data = TaskGenerator().generate(r_class, b_class, s_class_name=s_class)

    ga = GeneticAlgorithm(curr_task_data, pop_size, mutation_rate, elite_percent)
    ga.run(fixed_generations)

    return s_class, ga.history


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
        _, _, fitness = ga.run(verbose=False)
        fitness_by_pop[pop_size_i] = fitness
    return class_idx, fitness_by_pop


def _exp3_worker(args):
    """Один прогін експерименту 3: одна задача (v, k), обидва алгоритми на ній.

    Виконується в окремому процесі, тому має бути на рівні модуля (picklable).
    """
    (v_idx, r_class, b_class, m, n, q,
     pop_size, mutation_rate, elite_percent, max_stagnation) = args

    curr_task_data = TaskGenerator().generate(r_class, b_class, m=m, n=n, q=q)

    t0 = time.time()
    greedy_res = GreedyAlgorithm(curr_task_data).run()
    greedy_t = time.time() - t0

    t0 = time.time()
    _, _, ga_fitness = GeneticAlgorithm(curr_task_data, pop_size,
                                        mutation_rate, elite_percent, max_stagnation).run(verbose=False)
    genetic_t = time.time() - t0

    return v_idx, greedy_t, greedy_res[-1], genetic_t, ga_fitness


"""
Загалом планується проведення трьох експериментів:
1. визначення значення параметра умови завершення роботи алгоритму GA (t) в залежності від розмірності вхідної задачі;
2. дослідження впливу кількості особин в популяції (I) на точність роботи GA;
3. дослідження впливу розмірності задач на точність та час роботи жадібного та генетичного GA алгоритмів.
"""

class ExperimentCreator:
    def __init__(self, output_dir,
                 params_1=EXPERIMENT_1_DEFAULTS,
                 params_2=EXPERIMENT_2_DEFAULTS,
                 params_3=EXPERIMENT_3_DEFAULTS,
                 ga_params_1=GA_EXPERIMENT_1_DEFAULTS,
                 ga_params_2=GA_EXPERIMENT_2_DEFAULTS,
                 ga_params_3=GA_EXPERIMENT_3_DEFAULTS):
        # Параметри експерименту 1
        self.fixed_generations = params_1["fixed_generations"]

        # Параметри експерименту 2
        self.pop_size_list = params_2["pop_size_list"]
        self.K_2 = params_2["K"]

        # Параметри експерименту 3
        self.v_scale = params_3["v_scale"]
        self.K_3 = params_3["K"]

        # Параметри GA (окремо для кожного експерименту)
        self.ga_params_1 = ga_params_1
        self.ga_params_2 = ga_params_2
        self.ga_params_3 = ga_params_3

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
        def plot_result(x_max, y, s_class):
            x = np.arange(0, x_max+1, 1)
            plt.figure(figsize=(12, 5))
            plt.plot(x, y)
            plt.title(f'Зміна значення ЦФ від кількості ітерації генетичного алгоритму ({s_class})')
            plt.xlabel("Номер ітерації")
            plt.ylabel("Значення ЦФ")
            plt.grid(alpha=0.3)

            plot_path = self._get_plot_path("experiment_1_" + s_class)
            plt.savefig(plot_path, dpi=300)

            plt.show()
            plt.close()

        self.fixed_generations = int(self.fixed_generations)

        s_classes = ["S1", "S2", "S3"]
        jobs = [
            (s, r_class_name, b_class_name, self.fixed_generations,
             self.ga_params_1["pop_size"],
             self.ga_params_1["mutation_rate"],
             self.ga_params_1["elite_percent"])
            for s in s_classes
        ]

        results = {}
        with Pool(min(3, os.cpu_count() or 1)) as pool:
            for s_class, history in pool.imap_unordered(_exp1_worker, jobs):
                print(f'l={s_class} готово')
                results[s_class] = history

        for s in s_classes:
            plot_result(self.fixed_generations, results[s], s)

        return results

    def run_experiment_2(self):
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
            plt.savefig(plot_path, dpi=300)

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
                             self.pop_size_list,
                             self.ga_params_2["mutation_rate"],
                             self.ga_params_2["elite_percent"],
                             self.ga_params_2["max_stagnation"]))

        # results_k_by_class[class_idx][pop_size] -> список значень fitness
        results_k_by_class = {
            ci: {p: [] for p in self.pop_size_list} for ci in range(len(class_names))
        }

        with Pool(min(18, os.cpu_count() or 1)) as pool:
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

    def run_experiment_3(self, r_class_name="R1", b_class_name="B1"):
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
            plt.savefig(plot_path, dpi=300)

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

        jobs = []
        for v_idx, v in enumerate(self.v_scale):
            m = int(base_m*v)
            n = int(base_n*v)
            q = int(base_q*v)
            for k in range(K):
                jobs.append((v_idx, r_class_name, b_class_name, m, n, q,
                             self.ga_params_3["pop_size"],
                             self.ga_params_3["mutation_rate"],
                             self.ga_params_3["elite_percent"],
                             self.ga_params_3["max_stagnation"]))

        # results_by_v[v_idx] -> {'greedy_t': [], 'greedy_r': [], 'genetic_t': [], 'genetic_r': []}
        results_by_v = {
            vi: {'greedy_t': [], 'greedy_r': [], 'genetic_t': [], 'genetic_r': []}
            for vi in range(len(self.v_scale))
        }

        with Pool(min(18, os.cpu_count() or 1)) as pool:
            for v_idx, gt, gr, et, er in pool.imap_unordered(_exp3_worker, jobs):
                results_by_v[v_idx]['greedy_t'].append(gt)
                results_by_v[v_idx]['greedy_r'].append(gr)
                results_by_v[v_idx]['genetic_t'].append(et)
                results_by_v[v_idx]['genetic_r'].append(er)

        greedy_time = []
        genetic_time = []
        greedy_results = []
        genetic_results = []
        for v_idx in range(len(self.v_scale)):
            greedy_time.append(stats.fmean(results_by_v[v_idx]['greedy_t']))
            genetic_time.append(stats.fmean(results_by_v[v_idx]['genetic_t']))
            greedy_results.append(stats.fmean(results_by_v[v_idx]['greedy_r']))
            genetic_results.append(stats.fmean(results_by_v[v_idx]['genetic_r']))

        plot_result(self.v_scale, greedy_time, genetic_time, y_name='час роботи', name="experiment_3_time")
        plot_result(self.v_scale, greedy_results, genetic_results, y_name='значення цільової функції', name="experiment_3_objective")

        return

    def run_all(self):
        self.run_experiment_1()
        self.run_experiment_2()
        self.run_experiment_3()
