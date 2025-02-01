import math
import time
import curses

from config import DpsConfig
from patterns import POWER_ATTACK
from damage import DAMAGE_TABLE, WEAPON_DAMAGE_TABLE


class DpsMeter:
    def __init__(self, screen: curses.window, config: DpsConfig):
        self._screen = screen
        self._round_count = 1
        self._entities = config.include
        self._fp = config.watch_path
        self._poll_rate = config.poll_rate

        # Initialize stats
        self._stats = {}
        for entity in self._entities:
            self._stats[entity] = 0

    def start(self):
        self._run()

    def _run(self):
        # last_update_time = os.stat(self._fp).st_mtime

        with open(self._fp, "r") as f:
            while True:
                # new_time = os.stat(self._fp).st_mtime
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                self._update([line])
                self._draw()

                time.sleep(self._poll_rate)

    def reset(self):
        for entity in self._stats.keys():
            self._stats[entity] = 0

        self._round_count = 1

    def _calc_power_attack(self, line: str, entity: str):
        return 1000

    def _calc_round_damage(self, line: str, entity: str) -> int:
        # Get what weapon type is being used
        damage_table = None
        for m in WEAPON_DAMAGE_TABLE:
            if m[0].search(line):
                damage_table = DAMAGE_TABLE[m[1].value]
                break

        if damage_table is None:
            return 0

        # For this weapon's damage type, figure out what the message was
        for entry in damage_table:
            if entry.matcher.match(line):
                return entry.damage

        return 0

    def _calc_damage(self, line: str) -> bool:
        # Search through each entity we're interested in to see if the line matches
        for entity in self._entities:
            if line.startswith(entity):
                # See if its a power attack
                if POWER_ATTACK.match(line):
                    self._stats[entity] += self._calc_power_attack(line, entity)
                    return True

                # Calc base round damage
                self._stats[entity] += self._calc_round_damage(line, entity)
                return True

        return False

    def _update(self, lines: list[str]):
        for line in lines:
            # Found round start in this line
            if line.startswith("Hp: "):
                self._round_count += 1
                continue

            # Found damage for this line
            if self._calc_damage(line):
                continue

    def _draw(self):
        self._screen.clear()

        # Calc the player width
        biggest_player_width = 0
        biggest_dpr = 0
        for player, damage in self._stats.items():
            dpr = int(damage / self._round_count)
            biggest_dpr = max(biggest_dpr, dpr)
            biggest_player_width = max(biggest_player_width, len(player))

        self._screen.addstr(0, 0, f"[DPR Meter]     Total Rounds: {self._round_count}")

        y = 1
        for player, damage in sorted(
            self._stats.items(), key=lambda x: x[1], reverse=True
        ):
            x = 0
            player_tag = f"[{player}]: "
            self._screen.addstr(y, 0, player_tag)
            x = biggest_player_width + 5

            damage_tag = f"{damage} "
            self._screen.addstr(y, x, damage_tag)
            num_width = 1 if biggest_dpr == 0 else int(math.log10(biggest_dpr))
            x = biggest_player_width + 4 + num_width + 5

            dpr_tag = f"DPR: {int(damage / self._round_count)}"
            self._screen.addstr(y, x, dpr_tag)

            y += 1

        self._screen.refresh()
        return
