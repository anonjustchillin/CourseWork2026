import random

from generator.config import BASE_CONSTANTS, TASK_CLASSES


class TaskGenerator:
    """Генератор індивідуальних транспортних задач із розширенням виробництва."""

    def __init__(self, constants=BASE_CONSTANTS):
        self.c_mean = constants["c_mean"]
        self.c_var = constants["c_var"]
        self.a_mean = constants["a_mean"]
        self.d_var = constants["d_var"]
        self.delta_a_var = constants["delta_a_var"]
        self.mu = constants["mu"]
        self.k_var = constants["k_var"]

    def generate(self, m, n, q, class_name):
        """
        Генерує параметри задачі для заданого класу складності.

        Параметри:
        m (int): Кількість підприємств.
        n (int): Кількість споживачів.
        q (int): Кількість сценаріїв розширення.
        class_name (str): Назва класу (наприклад, "R1-B1").

        Повертає:
        dict: Словник з ключами a, b, c, delta_a, k, budget.
        """
        if class_name not in TASK_CLASSES:
            raise ValueError(f"Невідомий клас задачі: {class_name}")

        params = TASK_CLASSES[class_name]
        gamma = params["gamma"]
        beta = params["beta"]
        tau = params["tau"]

        # Транспортні витрати (c)
        c_min = self.c_mean * (1 - self.c_var)
        c_max = self.c_mean * (1 + self.c_var)
        c = [[round(random.uniform(c_min, c_max)) for _ in range(n)] for _ in range(m)]

        # Потужність (a) та попит (b)
        a_min = self.a_mean * (1 - self.d_var)
        a_max = self.a_mean * (1 + self.d_var)
        a = [round(random.uniform(a_min, a_max)) for _ in range(m)]

        b_mean = (self.a_mean * m) / ((1-gamma) * n)
        b_min = b_mean * (1 - self.d_var)
        b_max = b_mean * (1 + self.d_var)
        b = [round(random.uniform(b_min, b_max)) for _ in range(n)]

        # Приріст потужності (delta_a)
        delta_a_mean = beta*(n*b_mean - m*self.a_mean) / (gamma*m)
        delta_a_min = delta_a_mean * (1 - self.delta_a_var)
        delta_a_max = delta_a_mean * (1 + self.delta_a_var)

        delta_a = []
        for _ in range(m):
            row = [round(random.uniform(delta_a_min, delta_a_max)) for _ in range(q)]
            row.sort()  # Сценарії мають йти за зростанням потужності
            delta_a.append(row)

        # 4. Вартість сценаріїв (k)
        k = []
        for i in range(m):
            row_k = []
            for t in range(q):
                k_mean_it = self.mu * delta_a[i][t]
                k_min = k_mean_it * (1 - self.k_var)
                k_max = k_mean_it * (1 + self.k_var)
                row_k.append(round(random.uniform(k_min, k_max)))
            row_k.sort()
            k.append(row_k)

        # Бюджет (B)
        max_costs_sum = sum(max(row) for row in delta_a)
        budget = round(tau * self.mu * max_costs_sum)

        return {
            "a": a,
            "b": b,
            "c": c,
            "delta_a": delta_a,
            "k": k,
            "budget": budget
        }