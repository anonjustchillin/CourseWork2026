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
    "fixed_generations": {"S1": 20, "S2": 150, "S3": 400}
}

GA_EXPERIMENT_1_DEFAULTS = {
    "pop_size": 50,
    "mutation_rate": 0.3,
    "elite_percent": 0.2
}

# Для експерименту 2
EXPERIMENT_2_DEFAULTS = {
    "pop_size_list": [10, 50, 100],
    "K": 20 # (5)
}

GA_EXPERIMENT_2_DEFAULTS = {
    "mutation_rate": 0.3,
    "elite_percent": 0.2,
    "max_stagnation": 50 # висновок з експерименту 1
}

# Для експерименту 3
EXPERIMENT_3_DEFAULTS = {
    "v_scale": [2, 4, 6, 8],
    "K": 20 # (2)
}

GA_EXPERIMENT_3_DEFAULTS = {
    "pop_size": 50, # висновок з експерименту 2
    "mutation_rate": 0.3,
    "elite_percent": 0.2,
    "max_stagnation": 50
}

def get_ga_params():
    return GA_DEFAULTS.copy()
