def to_canonical_form(a, b, c):
    """
        Зводить транспортну задачу до канонічного (збалансованого) вигляду.

        Якщо загальна потужність постачальників перевищує загальний попит споживачів,
        функція додає фіктивного споживача з нульовими вартостями перевезення,
        щоб збалансувати систему.

        Параметри:
        a (list): Номінальні потужності постачальників.
        b (list): Обсяги попиту споживачів.
        c (list of lists): Матриця вартостей перевезення.

        Повертає:
        tuple: Збалансовані списки (a_can, b_can, c_can).
        """
    sum_a = sum(a)
    sum_b = sum(b)

    a_can = list(a)
    b_can = list(b)
    c_can = [row[:] for row in c]

    if sum_a > sum_b:
        b_can.append(sum_a - sum_b)
        for i in range(len(a_can)):
            c_can[i].append(0)

    return a_can, b_can, c_can