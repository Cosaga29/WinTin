import math
import time
import os
import curses

from config import DpsConfig
from patterns import POWER_ATTACK
from damage import DAMAGE_TABLE


class DpsMeter:
    def __init__(self, screen: curses.window, config: DpsConfig):
        self._screen = screen
        self._round_count = 0
        self._entities = config.include
        self._fp = config.watch_path
        self._poll_rate = config.poll_rate
        self._weapon_type_map = config.weapon_map

        # Initialize stats
        self._stats = {}
        for entity in self._entities:
            self._stats[entity] = 0


    def start(self):
        self._run()


    def _run(self):
        last_update_time = os.stat(self._fp).st_mtime

        with open(self._fp, "r") as f:
            while True:
                new_time = os.stat(self._fp).st_mtime

                # If the files modified time has changed, calculate damage
                if new_time != last_update_time:
                    last_update_time = new_time
                    self._update(f.readlines())
                    self._draw()
                    f.seek(0)

                time.sleep(self._poll_rate)
        return


    def reset(self):
        for entity in self._stats.keys():
            self._stats[entity] = 0

        self._round_count = 0


    def _get_damage_table(self, entity):
        damage_types = self._weapon_type_map[entity]
        # Just get the first one for now
        # Look up what damage table we should use for this weapon
        return damage_types[0].value
    

    def _calc_power_attack(self, entity):
        return 1000


    def _calc_round_damage(self, line, entity):
        # Calc base round damage
        if entity in self._weapon_type_map:
            damage_table = self._get_damage_table(entity)
            for entry in DAMAGE_TABLE[damage_table]:
                if entry.matcher.match(line):
                    self._stats[entity] += entry.damage
                    return True
                
        return False


    def _calc_damage(self, line: str) -> bool:
        for entity in self._entities:
            if line.startswith(entity):
                # See if its a power attack
                if POWER_ATTACK.match(line):
                    self._stats[entity] += self._calc_power_attack(entity)
                    return True
                
                # Calc base round damage
                return self._calc_round_damage(line, entity)

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

        y = 0
        for player, damage in self._stats.items():
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
