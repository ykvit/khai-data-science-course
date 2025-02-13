import numpy as np
import math

# Dictionary of available calculations with their formulas and implementations
CALCULATIONS = {
    1: {
        'formula': '(a^3 + b^3) / 2 - sqrt(|a - b|) / (1 + a * b)',
        'func': lambda a, b: (a**3 + b**3) / 2
                              - np.sqrt(abs(a - b)) / (1 + a * b)
    },
    2: {
        'formula': '(sin(a) + cos(b)) / (1 + a^2 + b^2)',
        'func': lambda a, b: (np.sin(a) + np.cos(b)) / (1 + a**2 + b**2)
    },
    3: {
        'formula': 'e^a + ln(|b + 1|)',
        'func': lambda a, b: np.exp(a) + np.log(abs(b + 1))
    },
    4: {
        'formula': '|a - b| / (1 + a * b) + sqrt(a^2 + b^2)',
        'func': lambda a, b: abs(a - b) / (1 + a * b) + np.sqrt(a**2 + b**2)
    },
    5: {
        'formula': 'tan(a) + b^2 / (1 + |a - b|)',
        'func': lambda a, b: np.tan(a) + b**2 / (1 + abs(a - b))
    },
    6: {
        'formula': '(a^2 - b^2) / (a + b) + cos(a * b)',
        'func': lambda a, b: (a**2 - b**2) / (a + b) + np.cos(a * b)
    },
    7: {
        'formula': 'a! / (b + 1) + sqrt(|b - a|)',
        'func': lambda a, b: math.gamma(a + 1) / (b + 1) + np.sqrt(abs(b - a))
                if a >= 0 and a == int(a) and a <= 20 else None
    },
    8: {
        'formula': 'log2(a + 2) / (b^2 + 1) + e^(-b)',
        'func': lambda a, b: np.log2(a + 2) / (b**2 + 1) + np.exp(-b)
    },
    9: {
        'formula': 'sqrt(a + b + 1) - 1 / (a^2 + b^2 + 1)',
        'func': lambda a, b: np.sqrt(a + b + 1) - 1 / (a**2 + b**2 + 1)
    },
    10: {
        'formula': 'sin(a * b) / (1 + |a - b|) + cos(a + b) / 2',
        'func': lambda a, b: np.sin(a * b) / (1 + abs(a - b)) + np.cos(a + b) / 2
    }
}
