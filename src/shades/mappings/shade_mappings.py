connections = {
    2: {
        4: 3,
        1: 8,
        3: 7,
        2: 6
    },
    3: {
        1: 9,
        3: 8,
        4: 7,
        2: 2
    },
    6: {
        5: 2,
        3: 7,
        2: 12,
        4: 11,
        1: 10
    },
    7: {
        6: 2,
        7: 3,
        3: 8,
        5: 13,
        4: 12,
        1: 11,
        2: 6
    },
    8: {
        6: 9,
        2: 14,
        3: 13,
        1: 12,
        4: 7,
        5: 2,
        7: 3
    },
    9: {
        1: 14,
        4: 13,
        2: 8,
        3: 3
    },
    10: {
        1: 6,
        3: 11,
        2: 16
    },
    11: {
        4: 6,
        2: 7,
        6: 12,
        3: 17,
        5: 16,
        1: 10
    },
    12: {
        3: 7,
        4: 8,
        7: 13,
        8: 18,
        5: 17,
        6: 16,
        2: 11,
        1: 6
    },
    13: {
        3: 8,
        8: 9,
        1: 14,
        7: 19,
        6: 18,
        5: 17,
        4: 12,
        2: 7
    },
    14: {
        6: 9,
        7: 3,
        4: 23,
        5: 19,
        1: 18,
        2: 13,
        3: 8
    },
    16: {
        4: 11,
        2: 12,
        3: 17,
        5: 22,
        1: 10
    },
    17: {
        2: 12,
        3: 13,
        5: 18,
        7: 23,
        6: 22,
        1: 16,
        4: 11
    },
    18: {
        1: 13,
        2: 14,
        6: 19,
        7: 23,
        5: 22,
        3: 17,
        4: 12
    },
    19: {
        3: 14,
        1: 23,
        2: 18,
        4: 13
    },
    22: {
        2: 17,
        1: 18,
        4: 23,
        3: 16
    },
    23: {
        3: 18,
        4: 19,
        1: 22,
        2: 17
    }
}

directions = {
    2: {
        'e': 4,
        'se': 1,
        's': 3,
        'sw': 2
    },
    3: {
        'se': 1,
        's': 3,
        'sw': 4,
        'w': 2
    },
    6: {
        'ne': 5,
        'e': 3,
        'se': 2,
        's': 4,
        'sw': 1
    },
    7: {
        'n': 6,
        'ne': 7,
        'e': 3,
        'se': 5,
        's': 4,
        'sw': 1,
        'w': 2
    },
    8: {
        'e': 6,
        'se': 2,
        's': 3,
        'sw': 1,
        'w': 4,
        'nw': 5,
        'n': 7
    },
    9: {
        's': 1,
        'sw': 4,
        'w': 2,
        'nw': 3
    },
    10: {
        'ne': 1,
        'e': 3,
        'se': 2
    },
    11: {
        'n': 4,
        'ne': 2,
        'e': 6,
        'se': 3,
        's': 5,
        'w': 1
    },
    12: {
        'n': 3,
        'ne': 4,
        'e': 7,
        'se': 8,
        's': 5,
        'sw': 6,
        'w': 2,
        'nw': 1
    },
    13: {
        'n': 3,
        'ne': 8,
        'e': 1,
        'se': 7,
        's': 6,
        'sw': 5,
        'w': 4,
        'nw': 2
    },
    14: {
        'n': 6,
        'ne': 7,
        'se': 4,
        's': 5,
        'sw': 1,
        'w': 2,
        'nw': 3
    },
    16: {
        'n': 4,
        'ne': 2,
        'e': 3,
        'se': 5,
        'nw': 1
    },
    17: {
        'n': 2,
        'ne': 3,
        'e': 5,
        'se': 7,
        's': 6,
        'w': 1,
        'nw': 4
    },
    18: {
        'n': 1,
        'ne': 2,
        'e': 6,
        's': 7,
        'sw': 5,
        'w': 3,
        'nw': 4
    },
    19: {
        'n': 3,
        'sw': 1,
        'w': 2,
        'nw': 4
    },
    22: {
        'n': 2,
        'ne': 1,
        'e': 4,
        'nw': 3
    },
    23: {
        'n': 3,
        'ne': 4,
        'w': 1,
        'nw': 2
    }
}