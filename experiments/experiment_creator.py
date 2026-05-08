import time
import matplotlib.pyplot as plt
import seaborn as sns
import os
from experiments.config import BASE_PARAMS_1, BASE_PARAMS_2, BASE_PARAMS_3
from genetic_algorithm.genetic_algo import GeneticAlgorithm
from greedy_algorithm.greedy_algo import GreedyAlgorithm


"""
Загалом планується проведення трьох експериментів:
1. визначення значення параметра умови завершення роботи алгоритму GA (t) в залежності від розмірності вхідної задачі;
2. дослідження впливу кількості особин в популяції (I) на точність роботи GA;
3. дослідження впливу розмірності задач на точність та час роботи жадібного та генетичного GA алгоритмів.
"""


class ExperimentCreator:
    def __init__(self, params_1=BASE_PARAMS_1, params_2=BASE_PARAMS_2, params_3=BASE_PARAMS_3):
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

    def start_time(self):
        self.time_start = time.time()

    def end_time(self):
        time_end = time.time()
        self.time_elapsed = time_end - self.time_start

    def run_experiment_1(self):
        """
            Параметри:
            fixed_generations (int): Максимальна кількість ітерацій (режим GA_fixed для експериментів).
            pop_size (int): Розмір популяції (парне число).
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
        """
        def trial():
            return
        return

    def run_experiment_2(self):
        """
            Параметри:
            pop_size_list (list of int): Масив розмірів популяції (парні числа).
            max_stagnation (int): Максимальна кількість ітерацій без покращення.
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
        """
        return

    def run_experiment_3(self):
        """
            Параметри (для GA):
            pop_size (int): Розмір популяції (парне число).
            max_stagnation (int): Максимальна кількість ітерацій без покращення.
            elite_percent (float): Частка елітних особин (від 0 до 1).
            mutation_rate (float): Ймовірність мутації (від 0 до 1).
        """
        return

    def run_all(self):
        self.run_experiment_1()
        self.run_experiment_2()
        self.run_experiment_3()
        return
