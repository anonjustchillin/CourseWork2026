EXPERIMENT_PARAMS_1 = {
    "fixed_generations": 500
}

EXPERIMENT_PARAMS_2 = {
    "m": 20,
    "n": 50,
    "q": 5,
    "pop_size_list": [20, 50, 100, 200],
    "K": 30
}

EXPERIMENT_PARAMS_3 = {
    "m": 5,
    "n": 10,
    "q": 2,
    "v_scale": [1, 2, 4, 6, 8, 10],
    "K": 30
}

"""
data = {
            "a": [80,90,60],
            "b": [80,110,70,90],
            "c": [[15, 22, 18, 25],
                  [20, 12, 10, 18],
                  [28, 20, 15, 12]],
            "delta_a": [[40, 90],
                        [30, 70],
                        [50, 100]],
            "k": [[250, 550],
                  [180, 450],
                  [320, 600]],
            "budget": 800,
            "m": 3,
            "n": 4,
            "q": 2
    }
"""
BASIC_PARAMS = {
            "a": [],
            "b": [],
            "c": [],
            "delta_a": [],
            "k": [],
            "budget": 0,
            "m": 0,
            "n": 0,
            "q": 0
}

"""
pop_size=2, mutation_rate=0.5, elite_percent=0.5, max_stagnation=5
"""
GA_PARAMS = {
    "pop_size": 0,
    "mutation_rate": 0.0,
    "elite_percent": 0.0,
    "max_stagnation": 0
}