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
    m = len(y)
    q = len(y[0])

    total_demand = sum(b)
    base_capacity = sum(a)

    all_scenarios = []
    for i in range(m):
        for t in range(q):
            efficiency = delta_a[i][t] / k[i][t]
            all_scenarios.append((efficiency, i, t, delta_a[i][t], k[i][t]))

    all_scenarios.sort(reverse=True, key=lambda x: x[0])

    current_cost = _calculate_total_cost(y, k)
    current_expansion = _calculate_total_expansion(y, delta_a)

    while current_cost > budget:
        active = _get_active_scenarios(y)
        if not active:
            break

        least_efficient = None
        min_eff = float('inf')
        for i, t in active:
            eff = delta_a[i][t] / k[i][t]
            if eff < min_eff:
                min_eff = eff
                least_efficient = (i, t)

        if least_efficient:
            i, t = least_efficient
            y[i][t] = 0
            current_cost -= k[i][t]
            current_expansion -= delta_a[i][t]

    while base_capacity + current_expansion < total_demand:
        best_scenario = None
        best_eff = -1

        for i in range(m):
            if sum(y[i]) > 0:
                continue
            for t in range(q):
                if current_cost + k[i][t] <= budget:
                    eff = delta_a[i][t] / k[i][t]
                    if eff > best_eff:
                        best_eff = eff
                        best_scenario = (i, t)

        if best_scenario is None:
            break

        i, t = best_scenario
        y[i][t] = 1
        current_cost += k[i][t]
        current_expansion += delta_a[i][t]

    total_capacity = base_capacity + current_expansion
    demand_is_covered = total_demand <= total_capacity
    within_budget = current_cost <= budget

    return y, (demand_is_covered and within_budget)


def _calculate_total_expansion(y, delta_a):
    """Розраховує сумарний приріст потужності."""
    return sum(
        y[i][t] * delta_a[i][t]
        for i in range(len(y))
        for t in range(len(y[i]))
    )

def _calculate_total_cost(y, k):
    """Розраховує сумарні витрати на обрані сценарії розширення."""
    return sum(y[i][t] * k[i][t] for i in range(len(y)) for t in range(len(y[i])))


def _get_active_scenarios(y):
    """Повертає список пар (i, t) для всіх активних сценаріїв (y[i][t] == 1)."""
    return [(i, t) for i in range(len(y)) for t in range(len(y[i])) if y[i][t] == 1]

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
