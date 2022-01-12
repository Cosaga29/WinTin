import sys
from mappings.shade_mappings import *

def main():
    cur_node = int(sys.argv[1])
    direction = sys.argv[2]

    if cur_node in connections and direction in directions[cur_node]:
        # Get the possible exits for this node
        direction = directions[cur_node][direction]
        print(direction)
        print(connections[cur_node][direction])

    return 1


if __name__ == "__main__":
    main()