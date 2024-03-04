import math
from ..util import get_direction
from game.models import Board, GameObject

class Tackle(object):
    def __init__(self):
        self.goal_position = None
        self.previous_position = (None, None)
        self.turn_direction = 1

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties

        # Analyze new state
        if props.diamonds > 2:
            # Move to base if we are full of diamonds
            base = props.base
            self.goal_position = base
        elif (props.milliseconds_left < 5000):
            if (board_bot.position.x == props.base.x and board_bot.position.y == props.base.y):
                self.goal_position = board.diamonds[0].position
            else:
                base = props.base
                self.goal_position = base
        else:
            # Move towards first diamond on board

            # ALGORITMA YANG DIUBAH DISINI AJA YAK
            ## algoritma yg baru gw tambahin masih penghitung jarak diamond terdekat
            ### masih belum konsiderasi diamond merah atau biru (todo) (dan kayanya gabisa)
            ### dan belum konsiderasi penggunaan portal (todo)

            ## perhitungkan diamond kotak merah
            ### kalo diamond merah dan biru kejauhan, incar diamond kotak

            # for i in range(len(board.game_objects)):
            #     print("ini anggota board nya ", board.game_objects[i].type)
            print("tackle")
            min = int(-1)
            for i in range (len(board.bots)):
                if((board_bot.position.x != board.bots[i].position.x or board_bot.position.y != board.bots[i].position.y) and (board.bots[i].properties.diamonds > 1)):
                    if(min == -1):
                        min = i
                    xMinDist = (abs(board_bot.position.x - board.bots[min].position.x)) 
                    yMinDist = (abs(board_bot.position.y - board.bots[min].position.y)) 
                    xNewDist = (abs(board_bot.position.x - board.bots[i].position.x)) 
                    yNewDist = (abs(board_bot.position.y - board.bots[i].position.y)) 
                    minDist = math.sqrt(xMinDist * xMinDist + yMinDist * yMinDist)
                    newDist = math.sqrt(xNewDist * xNewDist + yNewDist + yNewDist)
                    if (newDist < minDist):
                        min = i
            if(min == -1):
                self.goal_position = board.diamonds[0].position
            else:
                print("tes")
                self.goal_position = board.bots[min].position

        if self.goal_position:
            # Calculate move according to goal position
            current_position = board_bot.position
            cur_x = current_position.x
            cur_y = current_position.y
            delta_x, delta_y = get_direction(
                cur_x,
                cur_y,
                self.goal_position.x,
                self.goal_position.y,
            )

            if (cur_x, cur_y) == self.previous_position:
                # We did not manage to move, lets take a turn to hopefully get out stuck position
                if delta_x != 0:
                    delta_y = delta_x * self.turn_direction
                    delta_x = 0
                elif delta_y != 0:
                    delta_x = delta_y * self.turn_direction
                    delta_y = 0
                # Switch turn direction for next time
                self.turn_direction = -self.turn_direction
            self.previous_position = (cur_x, cur_y)

            return delta_x, delta_y

        return 0, 0