import random


def reanimate_chromosome(y, a, b, delta_a, k, budget):
    """
    Відновлює недопустиму хромосому до допустимого стану.

    Параметри:
    y (list of lists): Бінарна матриця сценаріїв (m x q).
    a (list): Номінальні потужності підприємств.
    b (list): Обсяги попиту споживачів.
    delta_a (list of lists): Матриця приросту потужності (m x q).
    k (list of lists): Матриця вартостей сценаріїв (m x q).
    budget (float): Загальний бюджет на розширення.

    Повертає:
    tuple: (y, bool) — оновлена хромосома та ознака життєздатності.
    """
    while _calculate_total_cost(y, k) > budget:
        active_scenarios = _get_active_scenarios(y)
        if not active_scenarios:
            return y, False

        efficiencies = [
            (delta_a[i][t] / k[i][t], i, t)
            for i, t in active_scenarios
        ]
        min_efficiency = min(efficiencies, key=lambda e: e[0])
        candidates = [e for e in efficiencies if e[0] == min_efficiency[0]]
        _, i, t = random.choice(candidates)

        y[i][t] = 0

    total_capacity = sum(a) + sum(y_it*delta_a_it for y_it,delta_a_it in zip(y, delta_a))
    demand_is_covered = sum(b) < total_capacity

    return y, demand_is_covered


def crossover(parent1_y, parent2_y):
    """
    Виконує одноточкове рядкове схрещування двох хромосом.

    Параметри:
    parent1_y (list of lists): Хромосома першого батька.
    parent2_y (list of lists): Хромосома другого батька.

    Повертає:
    tuple: Дві нові хромосоми-нащадки.
    """
    m = len(parent1_y)
    point = random.randint(1, m - 1)

    child1 = [row[:] for row in parent1_y[:point]] + [row[:] for row in parent2_y[point:]]
    child2 = [row[:] for row in parent2_y[:point]] + [row[:] for row in parent1_y[point:]]

    return child1, child2


def mutate(y, mutation_rate, q):
    """
    Виконує мутацію хромосоми — змінює сценарій для одного випадкового підприємства.

    Параметри:
    y (list of lists): Хромосома особини.
    mutation_rate (float): Ймовірність мутації.
    q (int): Кількість доступних сценаріїв розширення (без нульового).

    Повертає:
    list of lists: Змінена хромосома.
    """
    if random.random() > mutation_rate:
        return y

    y = [row[:] for row in y]
    m = len(y)
    i = random.randint(0, m - 1)

    y[i] = [0] * q
    new_scenario = random.randint(-1, q - 1)
    if new_scenario >= 0:
        y[i][new_scenario] = 1

    return y


def _calculate_total_cost(y, k):
    """Розраховує сумарні витрати на обрані сценарії розширення."""
    return sum(y[i][t] * k[i][t] for i in range(len(y)) for t in range(len(y[i])))


def _get_active_scenarios(y):
    """Повертає список пар (i, t) для всіх активних сценаріїв (y[i][t] == 1)."""
    return [(i, t) for i in range(len(y)) for t in range(len(y[i])) if y[i][t] == 1]