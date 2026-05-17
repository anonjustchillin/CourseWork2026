def calculate_vam(a, b, c):
    """
    Знаходить опорний план транспортної задачі методом апроксимації Фогеля (VAM).

    Алгоритм приймає збалансовані матриці, розраховує штрафи для невиключених
    рядків та стовпців (різниця між двома найменшими тарифами) і розподіляє
    ресурси так, щоб мінімізувати ризик переплати.

    Параметри:
    a (list): Номінальні потужності постачальників (після канонізації).
    b (list): Обсяги попиту споживачів (після канонізації).
    c (list of lists): Матриця вартостей перевезення (після канонізації).

    Повертає:
    list of lists: Матриця розподілу ресурсів x (план перевезень).
    """
    m = len(a)
    n = len(b)

    a_copy = list(a)
    b_copy = list(b)

    x = [[0] * n for _ in range(m)]

    active_rows = list(range(m))
    active_cols = list(range(n))

    while active_rows and active_cols:
        row_penalties = []
        for i in active_rows:
            costs = [c[i][j] for j in active_cols]
            if len(costs) > 1:
                sorted_costs = sorted(costs)
                row_penalties.append((sorted_costs[1] - sorted_costs[0], i))
            else:
                row_penalties.append((0, i))

        col_penalties = []
        for j in active_cols:
            costs = [c[i][j] for i in active_rows]
            if len(costs) > 1:
                sorted_costs = sorted(costs)
                col_penalties.append((sorted_costs[1] - sorted_costs[0], j))
            else:
                col_penalties.append((0, j))

        best_row = min(row_penalties, key=lambda x: (-x[0], x[1]))
        best_col = min(col_penalties, key=lambda x: (-x[0], x[1]))

        best_row_penalty, row_idx = best_row
        best_col_penalty, col_idx = best_col

        if best_row_penalty >= best_col_penalty:
            col_idx = min(active_cols, key=lambda j: (c[row_idx][j], j))
        else:
            row_idx = min(active_rows, key=lambda i: (c[i][col_idx], i))

        allocation = min(a_copy[row_idx], b_copy[col_idx])
        x[row_idx][col_idx] = allocation

        a_copy[row_idx] -= allocation
        b_copy[col_idx] -= allocation

        if a_copy[row_idx] == 0 and row_idx in active_rows:
            active_rows.remove(row_idx)
        if b_copy[col_idx] == 0 and col_idx in active_cols:
            active_cols.remove(col_idx)

        if len(active_rows) == 1 and len(active_cols) == 1:
            i_1 = active_rows[0]
            j_1 = active_cols[0]

            x[i_1][j_1] = a_copy[i_1]
            a_copy[i_1] = 0
            b_copy[j_1] = 0
            active_rows.clear()
            active_cols.clear()
        else:
            if len(active_rows) == 1 and len(active_cols) > 1:
                i_1 = active_rows[0]
                for j in active_cols:
                    x[i_1][j] = b_copy[j]
                    b_copy[j] = 0
                a_copy[i_1] = 0
                active_rows.clear()
                active_cols.clear()
            elif len(active_rows) > 1 and len(active_cols) == 1:
                j_1 = active_cols[0]
                for i in active_rows:
                    x[i][j_1] = a_copy[i]
                    a_copy[i] = 0
                b_copy[j_1] = 0
                active_rows.clear()
                active_cols.clear()

    return x