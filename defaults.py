"""
Значення за замовчуванням для генетичного алгоритму та експериментів.
"""

# Для розв'язання окремої задачі
GA_DEFAULTS = {
    "pop_size": 50,
    "mutation_rate": 0.3,
    "elite_percent": 0.2,
    "max_stagnation": 100
}

# Для експерименту 1
EXPERIMENT_1_DEFAULTS = {
    # "fixed_generations": {"S1": 100, "S2": 400, "S3": 700} # для звіту
    "fixed_generations": {"S1": 20, "S2": 150, "S3": 400} # для презентації (~5 хвилин)
}

GA_EXPERIMENT_1_DEFAULTS = {
    "pop_size": 50,
    "mutation_rate": 0.3,
    "elite_percent": 0.2
}

# Для експерименту 2
EXPERIMENT_2_DEFAULTS = {
    "pop_size_list": [10, 50, 100],
    # "K": 30 # для звіту
    "K": 5 # для презентації (~6 хвилин)
}

GA_EXPERIMENT_2_DEFAULTS = {
    "mutation_rate": 0.3,
    "elite_percent": 0.2,
    "max_stagnation": 50 # висновок з експерименту 1
}

# Для експерименту 3
EXPERIMENT_3_DEFAULTS = {
    # "v_scale": [1, 2, 4, 6, 8, 10], # для звіту
    "v_scale": [2, 4, 6, 8], # для презентації
    # "K": 30 # для звіту
    "K": 2 # для презентації (~6 хвилин)
}

GA_EXPERIMENT_3_DEFAULTS = {
    "pop_size": 50, # висновок з експерименту 2
    "mutation_rate": 0.3,
    "elite_percent": 0.2,
    "max_stagnation": 50 # висновок з експерименту 1
}

def get_ga_params():
    return GA_DEFAULTS.copy()
