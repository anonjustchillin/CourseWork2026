from transport_problem.canonical_form import to_canonical_form
from transport_problem.vam import calculate_vam
from transport_problem.evaluator import calculate_transport_cost


class GreedyAlgorithm:
    def __init__(self, task_data):
        """
        Параметри:
        task_data (dict): Вхідні дані задачі (a, b, c, delta_a, k, budget).
        """
        self.a = task_data["a"]
        self.b = task_data["b"]
        self.c = task_data["c"]
        self.delta_a = task_data["delta_a"]
        self.k = task_data["k"]
        self.budget = task_data["budget"]

        self.m = len(self.a)
        self.q = len(self.delta_a[0])

    def run(self):
        """
        Повертає:
        list of lists: Матриця розподілу ресурсів x (план перевезень).
        list of lists: Матриця бінарних змін y (обрані сценарії розширення виробництва).
        """
        E = {}
        for i in range(self.m):
            for t in range(self.q):
                E_value = self.delta_a[i][t]/self.k[i][t]
                E[E_value] = [i, t]

        E_desc = {k: v for k, v in sorted(E.items(), key=lambda item: item[0], reverse=True)}

        y = [[0] * self.q for _ in range(self.m)]

        for efficiency, (i, t) in E_desc.items():
            if 0 in y[i] and self.k[i][t] <= self.budget:
                y[i][t] = 1
                self.a[i] += self.delta_a[i][t]
                self.budget -= self.k[i][t]
                if sum(self.b) <= sum(self.a):
                    if sum(self.b) < sum(self.a):
                        self.b, self.c = to_canonical_form(self.a, self.b, self.c)
                    x = calculate_vam(self.a, self.b, self.c)

                    scenario_cost = sum(
                        y[i][t] * self.k[i][t]
                        for i in range(self.m)
                        for t in range(self.q)
                    )
                    transport_cost = calculate_transport_cost(x, self.c)
                    z = scenario_cost + transport_cost

                    return x, y, z

        return None
