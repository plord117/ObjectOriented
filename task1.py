import random
import sys
import time
from enum import Enum, unique
from abc import ABCMeta, abstractmethod
from util import Util

Boss_dic = {"health": 15, "attack": 5, "defence": 3}
Monster_dic = {"health": 7, "attack": 3, "defence": 2}
Player_dic = {"health": 15, "attack": 5, "defence": 2}
rate = [4, 3, 2, 1]


class Character:

    def __init__(self, name, health, attack, defence):
        self.__name = name
        self.__health = [health, health]
        self.__attack = attack
        self.__defence = defence

    def add_attack(self, num: int):
        self.__attack += num

    def add_defence(self, num: int):
        self.__defence += num

    def add_max_health(self, num):
        self.__health[1] += num

    def recover(self, num: int):
        self.__health[0] = self.__health[1] if self.__health[0] + num >= self.__health[1] else self.__health[0] + num

    def injured(self, num: int):
        self.__health[0] -= num if self.__health[0] >= num else self.__health[0]

    def get_current_health(self):
        return self.__health[0]

    def get_max_health(self):
        return self.__health[1]

    def get_attack(self):
        return self.__attack

    def get_defence(self):
        return self.__defence

    def get_name(self):
        return self.__name

    def is_alive(self):
        return self.__health[0] != 0

    def __str__(self):
        s = f"Name: {self.__name}\n" \
            f"Health: {self.__health}\n" \
            f"Attack: {self.__attack}\n" \
            f"Defence: {self.__defence}\n"
        return s


class Player(Character):
    def __init__(self, name, health, attack, defence):
        super(Player, self).__init__(name, health, attack, defence)


class Enemy(Character):
    def passive_skill(self):
        pass


class Boss(Enemy):
    def __init__(self, name, health, attack, defence):
        super(Boss, self).__init__(name, health, attack, defence)

    def passive_skill(self):
        print(f"触发被动，{self.get_name()}恢复1点血量")
        self.recover(1)


class Monster(Enemy):
    def __init__(self, name, health, attack, defence):
        super(Monster, self).__init__(name, health, attack, defence)
        self.skill_flg = True

    def passive_skill(self):
        if self.skill_flg:
            print(f"触发被动，{self.get_name()}提升一点防御")
            self.add_defence(1)
            self.skill_flg = False


@unique
class RoomType(Enum):
    NOTHING = 0
    TRAP = 1
    STORE = 2
    OTHER = 3


class Room:
    def __init__(self, room_type, character=None):
        self.__room_type = room_type
        self.__character = character
        self.__has_check = False

    def get_room_type(self):
        return self.__room_type

    def get_character(self):
        return self.__character

    def has_character(self):
        return self.__character is not None

    def has_check(self):
        return self.__has_check

    def set_check(self):
        self.__has_check = True

    def action(self, character: Character):
        pass

    def __str__(self):
        return f"Room Type: {self.__room_type}"


class Nothing(Room):
    def __init__(self):
        super(Nothing, self).__init__(RoomType.NOTHING)


class Trap(Room):
    def __init__(self):
        super(Trap, self).__init__(RoomType.TRAP)
        self.trap_flg = True

    def trap(self, character):
        if self.trap_flg:
            character.injured(1)
            self.trap_flg = False


class Store(Room):
    def __init__(self):
        super(Store, self).__init__(RoomType.STORE)

    def choice_upgrade(self, character: Character):
        while True:
            print("1.升级攻击")
            print("2.升级防御")

            n = input("请选择升级\n")
            if n not in ["1", "2"]:
                continue

            if n == "1":
                character.add_attack(1)
            else:
                character.add_defence(1)
            break


class Other(Room):
    def __init__(self, character):
        super(Other, self).__init__(RoomType.OTHER, character)


class Maze:
    def __init__(self, N):
        self.N = N
        self.graph = None
        self.player_pos = None
        self.__player = None
        self.__generate_maze()

    def get_player(self):
        return self.__player

    def __generate_maze(self):
        self.graph = Util.get_ori_graph(self.N, None)
        self.__generate_boss()
        self.__generate_player()

        for i in range(self.N):
            for j in range(self.N):
                if self.graph[i][j] is None:
                    self.__set_room(i, j)

    def __set_room(self, m, n):
        room = self.__get_random_room()
        self.graph[m][n] = room

    def __generate_boss(self):
        room = Other(Boss("Boss", Boss_dic["health"], Boss_dic["attack"], Boss_dic["defence"]))
        self.__set_random_room(room)

    def __generate_player(self):
        self.__player = Player("Player", Player_dic["health"], Player_dic["attack"], Player_dic["defence"])
        room = Other(self.__player)
        room.set_check()
        self.player_pos = self.__set_random_room(room)

    def __set_random_room(self, room):
        while True:
            M, N = Util.get_pos(self.N)
            if self.graph[M][N] is None:
                self.graph[M][N] = room
                return M, N

    def __get_random_room(self):
        index = random.randint(1, 100)
        if index <= 10 * rate[0]:
            return Nothing()
        elif 10 * rate[0] <= index < 10 * (rate[0] + rate[1]):
            return Store()
        elif 10 * (rate[0] + rate[1]) <= index < 10 * (rate[0] + rate[1] + rate[2]):
            return Other(Monster("Monster", Monster_dic['health'], Monster_dic["attack"], Monster_dic["defence"]))
        else:
            return Trap()

    def check_range(self, m, n):
        if m < 0 or n < 0 or m >= self.N or n >= self.N:
            return False
        return True

    def print_graph(self):
        res = []
        for i in range(self.N):
            tmp = []
            for j in range(self.N):
                if not self.graph[i][j].has_check():
                    tmp.append("X")
                else:
                    tmp.append(self.graph[i][j].get_room_type().name)
            res.append(tmp)

        res[self.player_pos[0]][self.player_pos[1]] = "p"
        s = ""
        for i in res:
            s += "\t".join(i)
            s += '\n'

        s.strip("\n")
        print(s)


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class Battle:
    def settlement(self, player: Player, monster):
        if player.is_alive() and monster.is_alive():
            return
        elif not monster.is_alive():
            self.__send_message(f"player成功击杀{monster.get_name()}")
            return True
        elif not player.is_alive():
            self.__send_message("战斗失败")
            return False

    def battle(self, player: Player, monster: Enemy):
        counter = 1
        print(f"战斗开始")
        while True:
            print(f"第{counter}回合")
            print(f"当前状态")
            print(player)
            print(monster)
            time.sleep(1)

            player_damage = player.get_attack() - monster.get_defence() if player.get_attack() > monster.get_defence() else 1
            monster.injured(player_damage)
            self.__send_message(f"player对{monster.get_name()}造成了{player_damage}点伤害")
            time.sleep(1)

            flg = self.settlement(player, monster)
            if flg is not None:
                return flg

            monster_damage = monster.get_attack() - player.get_defence() if monster.get_attack() > player.get_defence() else 1
            player.injured(monster_damage)
            self.__send_message(f"{monster.get_name()}对player造成了{monster_damage}点伤害")
            time.sleep(1)

            flg = self.settlement(player, monster)
            if flg is not None:
                return flg

            monster.passive_skill()
            time.sleep(1)
            counter += 1
            print()

    def __send_message(self, msg):
        print(msg)


@Singleton
class Game:
    def __init__(self, n):
        self.__maze = Maze(n)
        self.__battle_sys = Battle()

    def start_game(self):
        num = ['w', 'a', 's', 'd', 'e']
        while True:

            self.__print_graph()
            print()
            self.__print_menu()
            print()
            n = input("请输入命令：")
            print()
            if n.lower() not in num:
                continue
            if n.lower() == 'e':
                self.__print_status()
            else:
                self.move(n.lower())

    def __print_status(self):
        print("************属性***********")
        print()
        print(self.__maze.get_player())
        print("**************************")
        print()

    def __print_menu(self):
        print("************菜单***********")
        print()
        print("w: 向上运动")
        print("s: 向下运动")
        print("a: 向左运动")
        print("d: 向右运动")
        print("e. 显示当前状态")
        print()
        print("**************************")

    def __print_graph(self):
        print("************地图***********")
        print()
        self.__maze.print_graph()
        print("**************************")

    def move(self, n):
        if n == "w":
            flg = self.__move_up()
        elif n == 's':
            flg = self.__move_down()
        elif n == 'a':
            flg = self.__move_left()
        else:
            flg = self.__move_right()

        m, n = self.__maze.player_pos
        room = self.__maze.graph[m][n]
        if flg and not room.has_check():
            self.__check_room()

    def __check_room(self):
        m, n = self.__maze.player_pos
        room = self.__maze.graph[m][n]
        player = self.__maze.get_player()

        if room.get_room_type() == RoomType.NOTHING:
            pass
        elif room.get_room_type() == RoomType.STORE:
            room.choice_upgrade(player)
        elif room.get_room_type() == RoomType.TRAP:
            room.trap(player)
            print("遇到陷阱，失去一点血")
            if not player.is_alive():
                self.__failure("被陷阱杀死")
            self.__maze.graph[m][n].set_check()
        else:
            monster = room.get_character()
            flg = self.__battle_sys.battle(player, monster)
            if not flg:
                self.__failure(f"与{monster.get_name()}战斗死亡")
            else:
                if isinstance(monster, Boss):
                    self.__successful()

        self.__maze.graph[m][n].set_check()

    def __failure(self, meg):
        print(f"你失败了，死因{meg}")
        sys.exit()

    def __successful(self):
        print("你成功解救了公主")
        sys.exit()

    def __move_up(self):
        m, n = self.__maze.player_pos
        if self.__maze.check_range(m - 1, n):
            self.__maze.player_pos = m - 1, n
            return True

    def __move_down(self):
        m, n = self.__maze.player_pos
        if self.__maze.check_range(m + 1, n):
            self.__maze.player_pos = m + 1, n
            return True

    def __move_left(self):
        m, n = self.__maze.player_pos
        if self.__maze.check_range(m, n - 1):
            self.__maze.player_pos = m, n - 1
            return True

    def __move_right(self):
        m, n = self.__maze.player_pos
        if self.__maze.check_range(m, n + 1):
            self.__maze.player_pos = m, n + 1
            return True


if __name__ == '__main__':
    game = Game(5)
    game.start_game()
