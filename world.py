import enemies
import npc
import random


class MapTile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def intro_text(self):
        raise NotImplementedError("Create a subclass instead!")

    def modify_player(self, player):
        pass


class StartTile(MapTile):
    def intro_text(self):
        return """
        You find yourself in a cave with a flickering torch on the wall.
        You can make out four paths, each equally as dark and foreboding.
        """


class EnemyTile(MapTile):
    def __init__(self, x, y):
        r = random.random()
        if r < 0.50:
            self.enemy = enemies.GiantSpider()
            self.alive_text = "\nA giant spider jumps down from " \
                              "its web in front of you!\n"
            self.dead_text = "\nThe corpse of a dead spider " \
                             "rots on the ground."
        elif r < 0.80:
            self.enemy = enemies.Ogre()
            self.alive_text = "\nAn ogre is blocking your path!\n"
            self.dead_text = "\nA dead ogre reminds you of your triumph.\n"
        elif r < 0.95:
            self.enemy = enemies.BatColony()
            self.alive_text = "\nYou hear a squeaking noise growing louder" \
                              "...suddenly you are lost in s swarm of bats!\n"
            self.dead_text = "\nDozens of dead bats are scattered on the ground.\n"
        else:
            self.enemy = enemies.RockMonster()
            self.alive_text = "\nYou've disturbed a rock monster " \
                              "from his slumber!\n"
            self.dead_text = "\nDefeated, the monster has reverted " \
                             "into an ordinary rock.\n"

        super().__init__(x, y)

    def intro_text(self):
        text = self.alive_text if self.enemy.is_alive() else self.dead_text
        return text

    def modify_player(self, player):
        if self.enemy.is_alive():
            player.hp = player.hp - self.enemy.damage
            print(f"\nEnemy does {self.enemy.damage} damage. You have {player.hp} HP remaining.\n")


class VictoryTile(MapTile):
    def modify_player(self, player):
        player.victory = True

    def intro_text(self):
        return """
        You see a bright light in the distance...
        ... it grows as you get closer! It's sunlight!
        Victory is yours
        """


class FindGoldTile(MapTile):
    def __init__(self, x, y):
        self.gold = random.randint(1, 50)
        self.gold_claimed = False
        super().__init__(x, y)

    def modify_player(self, player):
        if not self.gold_claimed:
            self.gold_claimed = True
            player.gold = player.gold + self.gold
            print(f"+{self.gold} gold added.")

    def intro_text(self):
        if self.gold_claimed:
            return """
            Another unremarkable part of the labyrinth. You must proceed ahead.
            """
        else:
            return """
            Someone dropped some gold. You pick it up.
            """


class EmptyTile(MapTile):
    def __init__(self, x, y):
        super().__init__(x, y)

    def intro_text(self):
        return """
            Another unremarkable part of the labyrinth. You must proceed ahead.
            """


class TraderTile(MapTile):
    def __init__(self, x, y):
        self.trader = npc.Trader()
        super().__init__(x, y)

    def check_if_trade(self, player):
        while True:
            print("Would you like to (B)uy, (S)ell, or (Q)uit?")
            user_input = input()
            if user_input in ['Q', 'q']:
                return
            elif user_input in ['B', 'b']:
                print("Here's whats available to buy: ")
                self.trade(buyer=player, seller=self.trader)
            elif user_input in ['S', 's']:
                print("Here's whats available to sell: ")
                self.trade(buyer=self.trader, seller=player)
            else:
                print("Invalid choice!")

    def trade(self, buyer, seller):
        for i, item in enumerate(seller.inventory, 1):
            print(f"{i}. {item.name} - {item.value} Gold")
        while True:
            user_input = input("Choose an item or press Q to exit: ")
            if user_input in ['Q', 'q']:
                return
            else:
                try:
                    choice = int(user_input)
                    to_swap = seller.inventory[choice - 1]
                    self.swap(seller, buyer, to_swap)
                except ValueError:
                    print("Invalid choice!")

    def swap(self, seller, buyer, item):
        if item.value > buyer.gold:
            print("That's too expensive")
            return
        seller.inventory.remove(item)
        buyer.inventory.append(item)
        seller.gold = seller.gold + item.value
        buyer.gold = buyer.gold - item.value
        print("Trade complete!")

    def intro_text(self):
        return """
        A strange not-quite-human, not-quite-creature squats in the corner
        clinking his gold coins together. He looks willing to trade.
        """


# the world map
world_dsl = """
|VT|EN|FG|EN|EN|ET|
|EN|  |  |  |EN|FG|
|EN|FG|EN|  |  |EN|
|TT|EN|FG|FG|EN|FG|
|FG|  |EN|  |ET|EN|
|EN|EN|FG|EN|EN|FG|
|FG|  |EN|  |ST|EN|
|ET|EN|FG|EN|ET|FG|
"""


# world map validator
def is_dsl_valid(dsl):
    if dsl.count("|ST|") != 1:  # look for exactly 1 StartTile
        return False
    if dsl.count("|VT|") == 0:  # look for more than 1 VictoryTile
        return False
    lines = dsl.splitlines()    # splits a string into a list. The splitting is done at line breaks
    lines = [l for l in lines if l]     #
    pipe_counts = [line.count("|") for line in lines]
    for count in pipe_counts:
        if count != pipe_counts[0]:
            return False

    return True


tile_type_dict = {"VT": VictoryTile,
                  "EN": EnemyTile,
                  "ST": StartTile,
                  "FG": FindGoldTile,
                  "ET": EmptyTile,
                  "TT": TraderTile,
                  "  ": None}

world_map = []

start_tile_location = None


def parse_world_dsl():
    if not is_dsl_valid(world_dsl):
        raise SyntaxError("DSL is invalid!")

    dsl_lines = world_dsl.splitlines()      # makes world map tiles to lists []
    dsl_lines = [x for x in dsl_lines if x]     # for each list in that world map lists

    for y, dsl_row in enumerate(dsl_lines):     # enumerates each row
        row = []
        dsl_cells = dsl_row.split("|")      # split the rows
        dsl_cells = [c for c in dsl_cells if c]
        for x, dsl_cell in enumerate(dsl_cells):    # enumerate the cells
            tile_type = tile_type_dict[dsl_cell]    # gets the name of the title and the number
            if tile_type == StartTile:
                global start_tile_location
                start_tile_location = x, y
            row.append(tile_type(x, y) if tile_type else None)

        world_map.append(row)


def tile_at(x, y):
    if x < 0 or y < 0:
        return None
    try:
        return world_map[y][x]
    except IndexError:
        return None
