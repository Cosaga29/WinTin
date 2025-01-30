import re


# combat
prepare = re.compile(r"You prepare to attack .*?\.")
assist = re.compile(r"Noting the intentions of .*?, you move in to assist .*?\.")

COMBAT_START = [prepare, assist]


# rounds
round_start = re.compile(r"Hp: .*? Xp: \d+")

# combat round
base_round = re.compile(r"(.*?) (.*?) (.*?) (.*?) (.*?)")

POWER_ATTACK = re.compile(r"(.*?) launches a powerful attack")