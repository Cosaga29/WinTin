import curses
import os
from meter import DpsMeter
from config import DpsConfig


base_config = DpsConfig(
    include={"You", "Masume", "Learned Lyden"},
    watch_path=os.path.join(os.path.dirname(__file__), "../../logs/combat.log"),
    poll_rate=0.2
)


def main(stdscr: curses.window):
    curses.curs_set(0)

    dps_meter: DpsMeter = DpsMeter(stdscr, base_config)
    dps_meter.start()


if __name__ == "__main__":
    curses.wrapper(main)
