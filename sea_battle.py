from random import randint, choice, sample
import itertools
import copy


class ShipException(Exception):
    pass


class ShipDirectionError(ShipException):
    def __str__(self):
        return ('Неправильная ориентация корабля (возможна только 1, 2, 3, 4). Попробуйте снова!')


class ShipLengthError(ShipException):
    def __str__(self):
        return ('Неправильная длина корабля (в нашей игре только длины 1, 2, 3). Попробуйте снова!')


class ShipCollisionError(ShipException):
    def __str__(self):
        return ('Расположение корабля конфликтует с другими. Попробуйте снова!')


class DotException(Exception):
    def __str__(self):
        return ('Точка вне доски! Попробуйте снова!')


class InputError(Exception):
    def __str__(self):
        return ('Ошибка ввода! Попробуйте снова!')


class NotEmptySpaceError(Exception):
    def __str__(self):
        return ('Упс! Так корабли не влезут :(  Попробуйте сначала!')


class AlreadyShoot(Exception):
    def __str__(self):
        return ('В клетку уже стреляли. Попробуйте снова!')


class Board:
    def __init__(self, player_ships, ai_ships):
        self.field_1 = [['О' for _ in range(6)] for _ in range(6)]
        self.field_2 = [['О' for _ in range(6)] for _ in range(6)]

        for ship in player_ships:
            for dot in ship.coordinates:
                self.field_1[dot[0]][dot[1]] = '■'

        for ship in ai_ships:
            for dot in ship.coordinates:
                self.field_2[dot[0]][dot[1]] = '■'

    def __str__(self):
        sep = '                  '
        print()
        print(f'   | 1 | 2 | 3 | 4 | 5 | 6 |{sep}   | 1 | 2 | 3 | 4 | 5 | 6 |\n')
        for k in range(6):
            print(
                f'{k + 1}  | {self.field_1[k][0]} | {self.field_1[k][1]} | {self.field_1[k][2]} | {self.field_1[k][3]} | {self.field_1[k][4]} | {self.field_1[k][5]} |{sep}{k + 1}  | {self.field_2[k][0]} | {self.field_2[k][1]} | {self.field_2[k][2]} | {self.field_2[k][3]} | {self.field_2[k][4]} | {self.field_2[k][5]} |\n')

    def shoot(self, dot):
        dot = (dot[0] - 1, dot[1] - 1)
        if (self.field_2[dot[0]][dot[1]] == 'X') or (self.field_2[dot[0]][dot[1]] == 'T'):
            raise Exception('В клетку уже стреляли!')

        elif self.field_2[dot[0]][dot[1]] == 'О':
            self.field_2[dot[0]][dot[1]] = 'T'
            return

        elif self.field_2[dot[0]][dot[1]] == '■':
            self.field_2[dot[0]][dot[1]] = 'X'
            return

    def ai_turn(self):
        available_cells = []
        for row in range(6):
            for col in range(6):
                if (self.field_1[row][col] != 'X') and (self.field_1[row][col] != 'T'):
                    available_cells.append((row, col))
        dot = choice(available_cells)
        if self.field_1[dot[0]][dot[1]] == 'О':
            self.field_1[dot[0]][dot[1]] = 'T'
        else:
            self.field_1[dot[0]][dot[1]] = 'X'

    def check_winner(self):
        winner1, winner2 = True, True
        for row in range(6):
            for col in range(6):
                if self.field_2[row][col] == '■':
                    winner1 = False
                if self.field_1[row][col] == '■':
                    winner2 = False
        if winner1:
            return 1
        elif winner2:
            return 2
        else:
            return 0


class Dot:
    def __init__(self, x, y):
        if (x > 5) or (x < 0) or (y > 5) or (y < 0):
            raise DotException()
        self.x = x
        self.y = y

    def __str__(self):
        return (f'Dot( {self.x} , {self.y} )')

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)


class Ship:
    def __init__(self, start_dot, direction, length, aveliable_cells):
        if direction not in [1, 2, 3, 4]:
            raise ShipDirectionError()
        if length not in [1, 2, 3]:
            raise ShipLengthError()

        self.coordinates = [start_dot]
        for k in range(1, length):
            if direction == 1:
                self.coordinates.append(Dot(start_dot.x - k, start_dot.y))
            elif direction == 2:
                self.coordinates.append(Dot(start_dot.x, start_dot.y + k))
            elif direction == 3:
                self.coordinates.append(Dot(start_dot.x + k, start_dot.y))
            else:
                self.coordinates.append(Dot(start_dot.x, start_dot.y - k))
        for dot in self.coordinates:
            if dot not in aveliable_cells:
                raise ShipCollisionError()

    def get_coordinates(self):
        return self.coordinates


class Player:
    def __init__(self):
        self.hide = False
        self.ships = []
        self.field = [['О' for _ in range(6)] for _ in range(6)]
        self.aveliable_cells = []

    def check_defeat(self):
        defeat = True
        for row in range(6):
            for col in range(6):
                if self.field[row][col] == '■':
                    defeat = False
        return defeat

    def make_white_list(self):
        self.available_cells = []
        for row in range(6):
            for col in range(6):
                self.available_cells.append(Dot(row, col))

        for row in range(6):
            for col in range(6):
                for i in itertools.product([1, -1, 0], [1, -1, 0]):
                    try:
                        for ship in self.ships:

                            if Dot(row + i[0], col + i[1]) in ship.get_coordinates():
                                self.available_cells.remove(Dot(row, col))
                                break
                    except:
                        pass
        return

    def shoot_down(self, shoot_dot):
        if (self.field[shoot_dot.x][shoot_dot.y] == 'О'):
            self.field[shoot_dot.x][shoot_dot.y] = 'T'
            return False
        elif (self.field[shoot_dot.x][shoot_dot.y] == '■'):
            self.field[shoot_dot.x][shoot_dot.y] = 'X'
            if self.hide:
                l = []
                if shoot_dot.x + 1 < 6:
                    l.append(self.field[shoot_dot.x + 1][shoot_dot.y])
                if shoot_dot.x - 1 >= 0:
                    l.append(self.field[shoot_dot.x - 1][shoot_dot.y])
                if shoot_dot.y + 1 < 6:
                    l.append(self.field[shoot_dot.x][shoot_dot.y + 1])
                if shoot_dot.y - 1 >= 0:
                    l.append(self.field[shoot_dot.x][shoot_dot.y - 1])
                if '■' in l:
                    print('Ранен!')
                else:
                    print('Убит')

            return True
        else:
            raise AlreadyShoot()

    def make_random_ships(self):
        def make_3_cells_ship():
            orientation = randint(0, 1)  # 0 - горизонтально 1 - вертикально

            if orientation:
                start_dot = Dot(randint(0, 3), randint(0, 5))
                ship3 = Ship(start_dot, orientation + 2, 3, self.available_cells)
            else:
                start_dot = Dot(randint(0, 5), randint(0, 3))
                ship3 = Ship(start_dot, orientation + 2, 3, self.available_cells)
            return ship3

        def make_2_cells_ship():
            self.make_white_list()
            trigger = True
            while trigger:
                start_dot = choice(self.available_cells)
                orientations = sample([1, 2, 3, 4], 4)
                for orientation in orientations:
                    try:
                        ship2 = Ship(start_dot, orientation, 2, self.available_cells)
                        trigger = False
                        break
                    except:
                        pass
            return ship2

        def make_1_cell_ship():
            self.make_white_list()
            start_dot = choice(self.available_cells)
            return Ship(start_dot, 1, 1, self.available_cells)

        trigger = True

        while trigger:
            try:
                self.make_white_list()
                self.ships.append(make_3_cells_ship())
                self.ships.append(make_2_cells_ship())
                self.ships.append(make_2_cells_ship())
                self.ships.append(make_1_cell_ship())
                self.ships.append(make_1_cell_ship())
                self.ships.append(make_1_cell_ship())
                self.ships.append(make_1_cell_ship())
                trigger = False
            except:
                self.ships.clear()  # Если не влезли последние корабли, попробуем по-другому
                self.make_white_list()

        return self.ships

    def __str__(self):
        for ship in self.ships:
            for dot in ship.get_coordinates():
                if self.field[dot.x][dot.y] == 'О':
                    self.field[dot.x][dot.y] = '■'

        shadow_field = copy.deepcopy(self.field)
        if self.hide:
            for row in range(6):
                for col in range(6):
                    if self.field[row][col] == '■':
                        self.field[row][col] = 'O'

        field_string = f'\n   | 1 | 2 | 3 | 4 | 5 | 6 \n\n'
        for k in range(6):
            field_string += f'{k + 1}  | {self.field[k][0]} | {self.field[k][1]} | {self.field[k][2]} | {self.field[k][3]} | {self.field[k][4]} | {self.field[k][5]} \n'
        self.field = copy.deepcopy(shadow_field)

        return field_string


class UserPlayer(Player):
    def __init__(self, random_board):
        self.hide = False
        self.ships = []
        self.field = [['О' for _ in range(6)] for _ in range(6)]
        self.available_cells = []

        if random_board:
            self.ships = self.make_random_ships()

    def make_ships(self):
        space_true = True
        while space_true:
            try:
                self.ships = []
                print('''Расставьте корабли (1 трёхпалубный, 2 двухпалубных, 4 однопалубных). На каждый корабль введите три числа
через пробел: *вертикальная координата первой клетки корабля* *горизонтальная координата первой клетки корабля*
*ориентация (1 - вверх, 2 - вправо, 3 - вниз, 4 - влево)*
                      ''')

                self.make_white_list()
                trigger = True
                while trigger:
                    try:
                        print(self)
                        ship_features = list(map(int, input('Поставьте трёхпалубный: ').split()))

                        if len(ship_features) != 3:
                            raise InputError()
                        self.ships.append(Ship(Dot(ship_features[0] - 1, ship_features[1] - 1), ship_features[2], 3,
                                               self.available_cells))
                        trigger = False
                    except Exception as e:
                        print(e, '\n')

                print(self)
                for k in range(1, 3):
                    trigger = True
                    while trigger:
                        try:
                            self.make_white_list()
                            ship_features = list(map(int, input(f'Поставьте {k}-й двухпалубный: ').split()))
                            self.ships.append(Ship(Dot(ship_features[0] - 1, ship_features[1] - 1), ship_features[2], 2,
                                                   self.available_cells))
                            print(self)
                            trigger = False
                        except Exception as e:
                            print(e, '\n')

                print(self)
                for k in range(1, 5):
                    trigger = True
                    while trigger:
                        try:
                            self.make_white_list()

                            if len(self.available_cells) == 0:
                                raise NotEmptySpaceError()

                            ship_features = list(map(int, input(f'Поставьте {k}-й однопалубный: ').split()))
                            self.ships.append(Ship(Dot(ship_features[0] - 1, ship_features[1] - 1), ship_features[2], 1,
                                                   self.available_cells))
                            print(self)
                            trigger = False
                        except NotEmptySpaceError:
                            raise NotEmptySpaceError()
                        except Exception as e:
                            print(e, '\n')

                space_true = False
            except NotEmptySpaceError as e:
                print(e, '\n')
            except:
                print('Непредвиденная ошибка... Начните сначала')
                space_true = False


class AI(Player):
    def __init__(self):
        self.hide = True
        self.ships = []
        self.field = [['О' for _ in range(6)] for _ in range(6)]
        self.ships = self.make_random_ships()

    def shoot(self, opponent_field, opponent_ships):
        opponent_available_cells = []
        for row in range(6):
            for col in range(6):
                opponent_available_cells.append(Dot(row, col))
        for row in range(6):
            for col in range(6):
                try:
                    if (opponent_field[row][col] == 'T'):
                        opponent_available_cells.remove(Dot(row, col))
                    elif (opponent_field[row][col] == 'X'):
                        opponent_available_cells.remove(Dot(row, col))
                        for i in itertools.product([1, -1, 0], [1, -1, 0]):
                            opponent_available_cells.remove(Dot(row + i[0], col + i[1]))
                except:
                    pass
        shoot_dot = choice(opponent_available_cells)
        return shoot_dot


class Game:
    def __init__(self):
        print('Добро пожаловать в игру Морской бой!')
        random_board = input('Создать случайную расстановку корблей? y/n : ')
        if (random_board == 'y') or (random_board == 'Y'):
            self.user = UserPlayer(True)
        else:
            self.user = UserPlayer(False)
            self.user.make_ships()

        self.ai = AI()

        print(self)

    def start(self):
        while True:
            trigger = True
            while trigger:
                try:
                    dot = Dot(*list(map(lambda x: int(x) - 1, input('Ваш ход, стреляйте!: ').split())))
                    if self.ai.shoot_down(dot):
                        if self.ai.check_defeat():
                            print('Победа за вами! Игра окончена.')
                            trigger = False
                        print(self)
                    else:
                        print('Мимо!')
                        trigger = False


                except:
                    print('Неверные координаты! Попробуйте снова')
            if self.ai.check_defeat():
                break

            print(self)
            print('Ход компьютера:')
            trigger = True
            while trigger:
                if self.user.shoot_down(self.ai.shoot(self.user.field, self.user.ships)):
                    if self.user.check_defeat():
                        print('Вы проиграли! Игра окончена.')
                        trigger = False
                        break
                    print(self)
                    print('В вас попали! Снова ход компьютера: ')

                else:

                    trigger = False

            print(self)
            if self.user.check_defeat():
                break

    def __str__(self):
        board = ''
        part1 = self.user.__str__().split('\n')
        part2 = self.ai.__str__().split('\n')
        sep = '                  '
        for k in range(len(part1)):
            board += part1[k] + sep + part2[k] + '\n'
        return board


g = Game()
g.start()