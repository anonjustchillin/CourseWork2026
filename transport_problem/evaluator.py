def calculate_transport_cost(x, c_can):
    """
    Розраховує загальні транспортні витрати за знайденим планом перевезень.

    Параметри:
    x (list of lists): Матриця розподілу ресурсів (результат VAM).
    c_can (list of lists): Збалансована матриця вартостей перевезення.

    Повертає:
    int/float: Загальна сума транспортних витрат.
    """
    m = len(x)
    n = len(x[0])
    total_cost = 0

    for i in range(m):
        for j in range(n):
            if x[i][j] > 0:
                total_cost += x[i][j] * c_can[i][j]

    return total_cost