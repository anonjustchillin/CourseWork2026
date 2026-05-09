import random
import copy
from genetic_algorithm.models.individual import Individual
from genetic_algorithm.algorithms.ga_operators import (
    reanimate_chromosome,
    crossover,
    mutate,
)
from transport_problem.canonical_form import to_canonical_form
from transport_problem.vam import calculate_vam
from transport_problem.evaluator import calculate_transport_cost

max_retries = 20


class GeneticAlgorithm:
    """Головний менеджер генетичного алгоритму."""

    def __init__(self, task_data, pop_size, mutation_rate, elite_percent,
                 max_stagnation, tournament_size=2):
        """
        Параметри:
        task_data (dict): Вхідні дані задачі (a, b, c, delta_a, k, budget).
        pop_size (int): Розмір популяції (парне число).
        mutation_rate (float): Ймовірність мутації (від 0 до 1).
        elite_percent (float): Частка елітних особин (від 0 до 1).
        max_stagnation (int): Максимальна кількість ітерацій без покращення.
        tournament_size (int): Розмір турніру при селекції.
        """
        self.a = task_data["a"]
        self.b = task_data["b"]
        self.c = task_data["c"]
        self.delta_a = task_data["delta_a"]
        self.k = task_data["k"]
        self.budget = task_data["budget"]

        self.m = len(self.a)
        self.q = len(self.delta_a[0])

        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.elite_count = round(elite_percent * pop_size / 2) * 2
        self.max_stagnation = max_stagnation
        self.tournament_size = tournament_size

    def _generate_chromosome(self):
        """Генерує випадкову хромосому розміром (m x q)."""
        y = [[0] * self.q for _ in range(self.m)]
        for i in range(self.m):
            scenario = random.randint(-1, self.q - 1)
            if scenario >= 0:
                y[i][scenario] = 1
        return y

    def _evaluate_individual(self, individual):
        """
        Розраховує fitness для особини через транспортне ядро.

        Параметри:
        individual (Individual): Особина з встановленою хромосомою.
        """
        y = individual.chromosome

        a_modified = [
            self.a[i] + sum(y[i][t] * self.delta_a[i][t] for t in range(self.q))
            for i in range(self.m)
        ]

        scenario_cost = sum(
            y[i][t] * self.k[i][t]
            for i in range(self.m)
            for t in range(self.q)
        )

        b_can, c_can = to_canonical_form(a_modified, self.b, self.c)
        x = calculate_vam(a_modified, b_can, c_can)
        transport_cost = calculate_transport_cost(x, c_can)

        individual.fitness = scenario_cost + transport_cost
        individual.transport_plan = x

    def _initialize_population(self):
        """Створює початкову популяцію допустимих унікальних особин."""
        population = []
        print("Ініціалізація початкової популяції")

        while len(population) < self.pop_size:
            y = self._generate_chromosome()
            y, is_viable = reanimate_chromosome(
                y, self.a, self.b, self.delta_a, self.k, self.budget
            )
            if not is_viable:
                continue

            candidate = Individual(y)
            if candidate in population:
                continue

            self._evaluate_individual(candidate)
            population.append(candidate)

        return population

    def _tournament_selection(self, population):
        """
        Формує батьківський пул через турнірний відбір.

        Параметри:
        population (list): Поточна популяція особин.

        Повертає:
        list: Батьківський пул розміром pop_size // 2.
        """
        parent_pool = []

        while len(parent_pool) < self.pop_size // 2:
            group = random.sample(population, self.tournament_size)
            winner = min(group, key=lambda ind: ind.fitness)
            parent_pool.append(winner)
        return parent_pool

    def _create_offspring(self, parent_pool, new_population):
        """
        Створює нащадка через схрещування та мутацію з перевіркою допустимості.

        Параметри:
        parent_pool (list): Пул батьків.
        new_population (list): Нова популяція, що формується (для перевірки унікальності).

        Повертає:
        Individual або None, якщо після MAX_RETRIES не вдалось отримати допустимого нащадка.
        """
        for _ in range(max_retries):
            p1, p2 = random.sample(parent_pool, 2)
            child1_y, _ = crossover(p1.chromosome, p2.chromosome)
            child_y = mutate(child1_y, self.mutation_rate, self.q)

            child_y, is_viable = reanimate_chromosome(
                child_y, self.a, self.b, self.delta_a, self.k, self.budget
            )
            if not is_viable:
                continue

            candidate = Individual(child_y)
            if candidate in new_population:
                continue

            self._evaluate_individual(candidate)
            return candidate

        return None

    def run(self, fixed_generations=None):
        """
                Запускає головний еволюційний цикл.

                Параметри:
                fixed_generations (int): Якщо задано, алгоритм виконає рівно цю кількість
                    ітерацій (режим GA_fixed для експериментів).
                    Якщо None, працює до досягнення max_stagnation.

                Повертає:
                tuple: (Individual, list) — найкраща особина та масив значень рекорду за ітераціями.
                """

        population = self._initialize_population()
        population.sort()

        best = population[0]
        history = [best.fitness]
        stagnation_counter = 0
        generation = 0

        if fixed_generations is None:
            print(f"Початковий рекорд: {best.fitness:.2f}")

        while True:
            if fixed_generations is not None:
                if generation >= fixed_generations: break
            elif stagnation_counter >= self.max_stagnation:
                break

            generation += 1
            parent_pool = self._tournament_selection(population)

            elites = population[:self.elite_count]
            new_population = [copy.deepcopy(e) for e in elites]

            failed_attempts = 0
            max_total_retries = max_retries * self.pop_size

            while len(new_population) < self.pop_size:
                offspring = self._create_offspring(parent_pool, new_population)

                if offspring is not None:
                    new_population.append(offspring)
                    failed_attempts = 0
                else:
                    failed_attempts += 1

                if failed_attempts > max_total_retries:
                    backup_parent = random.choice(parent_pool)
                    new_population.append(copy.deepcopy(backup_parent))
                    failed_attempts = 0

            new_population.sort()
            population = new_population

            if population[0].fitness < best.fitness:
                best = population[0]
                stagnation_counter = 0
                if fixed_generations is None:
                    print(f"Покоління {generation}: новий рекорд {best.fitness:.2f}")
            else:
                stagnation_counter += 1

            history.append(best.fitness)

        return best, history