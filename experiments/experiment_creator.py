import time
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import statistics as stats
from experiments.config import BASE_PARAMS_1, BASE_PARAMS_2, BASE_PARAMS_3
from genetic_algorithm.genetic_algo import GeneticAlgorithm
from greedy_algorithm.greedy_algo import GreedyAlgorithm
from generator.task_generator import TaskGenerator


"""
Загалом планується проведення трьох експериментів:
1. визначення значення параметра умови завершення роботи алгоритму GA (t) в залежності від розмірності вхідної задачі;
2. дослідження впливу кількості особин в популяції (I) на точність роботи GA;
3. дослідження впливу розмірності задач на точність та час роботи жадібного та генетичного GA алгоритмів.
"""

DPI = 300

class ExperimentCreator:
    def __init__(self, output_dir, params_1=BASE_PARAMS_1, params_2=BASE_PARAMS_2, params_3=BASE_PARAMS_3):
        self.fixed_generations = params_1["fixed_generations"]

        self.m_2 = params_2["m"]
        self.n_2 = params_2["n"]
        self.q_2 = params_2["q"]
        self.pop_size_list = params_2["pop_size_list"]
        self.K_2 = params_2["K"]

        self.m_3 = params_3["m"]
        self.n_3 = params_3["n"]
        self.q_3 = params_3["q"]
        self.v_scale = params_3["v_scale"]
        self.K_3 = params_3["K"]

        self.time_start = 0
        self.time_elapsed = 0

        self.output_dir = output_dir

    def start_time(self):
        self.time_start = time.time()

    def end_time(self):
        time_end = time.time()
        self.time_elapsed = time_end - self.time_start

    def run_experiment_1(self, class_name="R2-B2"):
        def trial(class_name, s_class_name, fixed_generations, pop_size, elite_percent, mutation_rate):
            """
            Параметри:
            class_name (str): Назва класу (наприклад, "R1-B1").
            s_class_name (str): Назва S класу (наприклад, "S1").
            fixed_generations (int): Максимальна кількість ітерацій (режим GA_fixed для експериментів).
            pop_size (int): Розмір популяції (парне число).
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
            """
            if s_class_name == "S1":
                m = 5
                n = 10
                q = 2
            elif s_class_name == "S2":
                m = 20
                n = 50
                q = 5
            else:
                m = 100
                n = 200
                q = 10

            curr_task = TaskGenerator()
            curr_task_data = curr_task.generate(m, n, q, class_name)

            record_log = []
            for k in range(1, fixed_generations+1):
                curr_solution = GeneticAlgorithm(curr_task_data, pop_size, mutation_rate, elite_percent, np.inf)
                _, curr_record = curr_solution.run(fixed_generations)
                record_log.append(curr_record)

            return record_log

        def plot_result(x, y, name=''):
            plt.plot(x, y)
            plt.title("Зміна значення ЦФ від кількості ітерації генетичного алгоритму")
            plt.xlabel("Номер ітерації")
            plt.ylabel("Значення ЦФ")
            plt.grid(alpha=0.3)
            plt.show()

            #plot_path = os.path.join(self.output_dir, name + ".png")
            #plt.savefig(self.output_dir, dpi=DPI)

            #plt.close()
            return

        results = {}
        for l in ["S1", "S2", "S3"]:
            record_log = trial(class_name, l, self.fixed_generations,)
            plot_result(self.fixed_generations, record_log)
            results[l] = record_log

        return results

    def run_experiment_2(self):
        def plot_result(data, class_names, name=''): # гістограми
            x = len(class_names)

            width = 0.25
            multiplier = 0

            fig, ax = plt.subplots(layout='constrained')
            for pop_size, values in data.items():
                offset = width * multiplier
                ax.bar(x+offset, values, width, label=pop_size)
                multiplier += 1

            ax.set_title("Вплив кількості особин в популяції (I) на ЦФ генетичного алгоритму")
            ax.set_ylabel("Значення ЦФ")
            ax.set_xticks(x + width, class_names)
            ax.legend()
            plt.show()

            #plt.savefig(self.output_dir, dpi=DPI)

            # plt.close()
            return
        """
            Параметри:
            pop_size_list (list of int): Масив розмірів популяції (парні числа).
            max_stagnation (int): Максимальна кількість ітерацій без покращення.
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
        """

        m = self.m_2
        n = self.n_2
        q = self.q_2
        K = self.K_2

        class_names = ["R1-B1", "R3-B1", "R1-B3", "R3-B3", "R2-B2"]

        results = {}

        for class_name in class_names:
            results, results_k = {i: [] for i in self.pop_size_list}
            for k in range(1, K+1):
                curr_task = TaskGenerator()
                curr_task_data = curr_task.generate(m, n, q, class_name)
                for pop_size in self.pop_size_list:
                    curr_solution = GeneticAlgorithm(curr_task_data, pop_size, mutation_rate, elite_percent, max_stagnation)
                    best_res, _ = curr_solution.run()
                    results_k[pop_size].append(best_res.fitness)

            for pop_size in self.pop_size_list:
                results[pop_size] = stats.fmean(results_k[pop_size])

        plot_result(results, class_names)

        return

    def run_experiment_3(self, class_name="R2-B2"):
        def plot_result(x, y1, y2, y_name='', name=''):
            plt.plot(x, y1, label='Жадібний алгоритм')
            plt.plot(x, y2, label='Генетичний алгоритм')
            plt.title("Вплив розмірності задачі на "+str.lower(y_name)+" алгоритмів")
            plt.xlabel("Коефіцієнт масштабу v")
            plt.ylabel(y_name)
            plt.legend()
            plt.grid(alpha=0.3)
            plt.show()

            #plt.savefig(self.output_dir, dpi=DPI)

            # plt.close()
            return
        """
            Параметри (для GA):
            pop_size (int): Розмір популяції (парне число).
            max_stagnation (int): Максимальна кількість ітерацій без покращення.
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
        """

        m = self.m_3
        n = self.n_3
        q = self.q_3
        K = self.K_3

        greedy_time = []
        genetic_time = []

        greedy_results = []
        genetic_results = []

        for v in self.v_scale:
            m = m*v
            n = n*v
            q = q*v

            greedy_time_k = []
            genetic_time_k = []

            greedy_results_k = []
            genetic_results_k = []

            for k in range(1, K+1):
                curr_task = TaskGenerator()
                curr_task_data = curr_task.generate(m, n, q, class_name)

                self.start_time()
                greedy_algo = GreedyAlgorithm(curr_task_data)
                greedy_res = greedy_algo.run()
                self.end_time()
                greedy_time_k.append(self.time_elapsed)

                greedy_results_k.append(greedy_res)

                self.start_time()
                genetic_algo = GeneticAlgorithm(curr_task_data)
                best_res, _ = genetic_algo.run()
                self.end_time()
                genetic_time_k.append(self.time_elapsed)

                genetic_results_k.append(best_res.fitness)

            greedy_time.append(sum(greedy_time_k)/K)
            genetic_time.append(sum(genetic_time_k)/K)

            greedy_results.append(sum(greedy_results_k)/K)
            genetic_results.append(sum(genetic_results_k)/K)

            plot_result(self.v_scale, greedy_time, genetic_time, y_name='час роботи')
            plot_result(self.v_scale, greedy_results, genetic_results, y_name='точність')


        return

    def run_all(self):
        self.run_experiment_1()
        self.run_experiment_2()
        self.run_experiment_3()
