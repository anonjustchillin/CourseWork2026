class Individual:
    """Представляє одну особину в популяції генетичного алгоритму."""

    def __init__(self, chromosome):
        """
        Параметри:
        chromosome (list of lists): Бінарна матриця y розміром (m x q),
            де y[i][t] = 1 означає, що для підприємства i обрано сценарій t.
        """
        self.chromosome = [row[:] for row in chromosome]
        self.fitness = None

    def __lt__(self, other):
        """Порівняння за значенням цільової функції (для сортування популяції)."""
        return self.fitness < other.fitness

    def __eq__(self, other):
        """Порівняння хромосом для перевірки унікальності в популяції."""
        return self.chromosome == other.chromosome

    def __repr__(self):
        return f"Individual(fitness={self.fitness})"