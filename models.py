import logging
import numpy as np
import random

import settings


class DNA_ACTION(object):
    
    def __init__(self, init_sequence=None):
        if init_sequence is None:
            self._dna_sequence = [list(a) for a in
                                  zip(np.random.randint(0, 6, settings.DNA_ACTION_LENGTH),
                                     np.random.randint(0, 4, settings.DNA_ACTION_LENGTH))]
        else:
            self._dna_sequence = [(self._mutate_move(x), self._mutate_turn(y)) for x, y
                                  in init_sequence]

    def _mutate_move(self, gene):
        return (np.random.randint(0, 6)
            if np.random.randint(1, settings.MUTATION)==1 
            else gene)

    def _mutate_turn(self, gene):
        return (np.random.randint(0, 4)
            if np.random.randint(1, settings.MUTATION)==1
            else gene)

    def splice(self, dna_object):
        break_point = np.random.randint(0, settings.DNA_ACTION_LENGTH)
        child1 = self._dna_sequence[:break_point] +\
                 dna_object.get_sequence()[break_point:]
        child2 = dna_object.get_sequence()[:break_point] +\
                 self._dna_sequence[break_point:]
        return DNA_ACTION(child1), DNA_ACTION(child2)

    def get_sequence(self):
        return self._dna_sequence

    def get_gene(self, position):
        return self._dna_sequence[position]


class DNA_PERCEPTION(object):

    def __init__(self, init_sequence=None):
        if init_sequence is None:
            self._dna_sequence = self._dna_sequence = np.random.randint(0, 2, settings.DNA_PERCEPTION_LENGTH)
        else:
            self._dna_sequence = [self._mutate(x) for x in init_sequence]

    def _mutate(self, gene):
        return (np.random.randint(0, 2)
                if np.random.randint(1, settings.MUTATION) == 1
                else gene)

    def splice(self, dna_object):
        child1 = random.choice([
            self._dna_sequence,
            dna_object.get_sequence()])
        child2 = random.choice([
            self._dna_sequence,
            dna_object.get_sequence()])
        return DNA_PERCEPTION(child1), DNA_PERCEPTION(child2)

    def get_sequence(self):
        return self._dna_sequence

    def get_gene(self, position):
        return self._dna_sequence[position]


class Robby(object):

    def __init__(self, dna_action=None, dna_perception=None):
        if dna_action is None:
            self._dna_action = DNA_ACTION()
        else:
            self._dna_action = dna_action
        if dna_perception is None:
            self._dna_perception = DNA_PERCEPTION()
        else:
            self._dna_perception = dna_perception
        self._fitness = 0
        self._position = {'y': 0, 'x': 0}
        self._actions = {
            0: self._move_north,
            1: self._move_east,
            2: self._move_west,
            3: self._move_south,
            4: self._move_random,
            5: self._pick_up
        }
        self._turned = 3
        self._turns = {
            0: self._turn_north,
            1: self._turn_south,
            2: self._turn_west,
            3: self._turn_east}

    def mate(self, partner):
        dna_act1, dna_act2 = self._dna_action.splice(partner.get_dna_act())
        dna_perc1, dna_perc2 = self._dna_perception.splice(partner.get_dna_perc())
        return Robby(dna_act1, dna_perc1), Robby(dna_act2, dna_perc2)

    def get_dna_act(self):
        return self._dna_action

    def get_dna_perc(self):
        return self._dna_perception

    def live(self):
        scores = []
        for i in range(0, settings.TRIES):
            trial_fitness = 0
            board = Board()
            self._position = {'y': 0, 'x': 0}
            for step in range(0, settings.LIFESPAN):
                scenario = board.get_scenario(**self._position)
                translated_scenario = self.env_to_color_translation(scenario)
                sense_making_scenario = self.sense_making(translated_scenario)
                sense_making_scenario_index = self.sense_making_scenario_index(sense_making_scenario)
                gene_move, gene_turn = self._dna_action.get_gene(sense_making_scenario_index)
                trial_fitness = self._actions[gene_move](board, trial_fitness)
                self._turned = gene_turn
            self._turned = 3
            scores.append(trial_fitness)
        self._fitness = np.array(scores).mean()
        logging.debug("Individual Fitness {}".format(self._fitness))
                    
    def get_fitness(self):
        return self._fitness

    def _move_north(self, board, fitness):
        if self._position['x']==0:
            fitness -= settings.CRASH_PENALTY
        else:
            self._position['x'] -= 1
        return fitness

    def _move_east(self, board, fitness):
        x, y = board.get_size()
        if self._position['y'] == y-1:
            fitness -= settings.CRASH_PENALTY
        else:
            self._position['y'] += 1
        return fitness

    def _move_west(self, board, fitness):
        if self._position['y']==0:
            fitness -= settings.CRASH_PENALTY
        else:
            self._position['y'] -= 1
        return fitness
        
    def _move_south(self, board, fitness):
        x, y = board.get_size()
        if self._position['x']==x-1:
            fitness -= settings.CRASH_PENALTY
        else:
            self._position['x'] += 1
        return fitness

    def _move_random(self, board, fitness):
        action = np.random.choice([
            self._move_north,
            self._move_east,
            self._move_west,
            self._move_south
        ])
        return action(board, fitness)

    def _pick_up(self, board, fitness):
        fitness -= settings.PICKUP_PENALTY
        soda_amount = board._board[self._position['x'], self._position['y']]
        fitness += settings.PICKUP_POINTS[soda_amount]
        board.cleanup_site(**self._position)
        return fitness

    def _turn_north(self):
        self._turned = 0

    def _turn_south(self):
        self._turned = 1

    def _turn_west(self):
        self._turned = 2

    def _turn_east(self):
        self._turned = 3

    def env_to_color_translation(self, scenario):
        color_perc = [2 if pos==-1 else int(self._dna_perception.get_gene(pos)) for pos in scenario]
        return color_perc

    def sense_making(self, color_scenario):
        self_pos_index = 4
        turned_to_pos_index = self._turned
        sense_making_scenario = ()
        for i, num in enumerate(color_scenario):
            if i == self_pos_index or i == turned_to_pos_index:
                sense_making_scenario += (num,)
            else:
                sense_making_scenario += (None,)
        return sense_making_scenario

    def sense_making_scenario_index(self, sense_making_scenario):
        states = settings.STATES
        state_index = None
        for i, state in enumerate(states):
            if sense_making_scenario == state:
                state_index = i
        return state_index



class Board(object):
    
    def __init__(self):
        self._board = np.random.randint(11, size=(10,10))

    def get_scenario(self, x, y):
        """Return a base-10 integer that is the equivalent of the 5-digit 
        base-3 number that corresponds to one of 234 possible scenarios.

        The trit positions mean:
        North - south - West - east - Current
        3^4   - 3^3  - 3^2  - 3^1   - 3^0

        Trit value meanings:
        -1 - wall
        0-10 - amount of water

        Arguments:
        x -- x-coordinate
        y -- y-coordinate

        """
        
        scenario = [
            self._get_amount(x - 1, y),
            self._get_amount(x + 1, y),
            self._get_amount(x, y-1),
            self._get_amount(x, y+1),
            self._get_amount(x, y)
        ]
        return scenario
        #return base3_to_base10(''.join(scenario))

    def _get_amount(self, x, y):
        if -1<x<10 and -1<y<10:
            return self._board[x, y]
        else:
            return -1

    def cleanup_site(self, x, y):
        self._board[x, y] = 0

    def get_size(self):
        return self._board.shape


def base3_to_base10(base3_str):
    strlen = len(base3_str)
    base10_int = 0
    for index, value in enumerate(base3_str):
        base10_int += int(value) * 3**(strlen-1-index)
    return base10_int