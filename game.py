import random
import math
from enums import RoundType
from events import events


class Game:
    def __init__(self, owner_name, owner_id, title: str):
        self.owner_name = owner_name
        self.owner_id = owner_id
        self.title = title
        self.players = []
        self.players_alive = []
        self.players_dead = []
        self.players_dead_today = []
        self.players_available = set()
        self.day = 1
        self.started = False
        self.days_since_last_event = 0
        self.rounds_without_deaths = 0
        self.bloodbath_passed = False
        self.day_passed = False
        self.fallen_passed = False
        self.night_passed = False

    def add_player(self, new_player):
        self.players.append(new_player)

    def name_exists(self, name):
        for p in self.players:
            if p.name == name:
                return True
        return False

    def start(self):
        for p in self.players:
            self.players_alive.append(p)
        self.started = True

    def step(self):

        if len(self.players_alive) is 1:
            self.started = False
            return {'winner': self.players_alive[0].name, 'district': self.players_alive[0].district}

        if self.night_passed:
            self.day += 1
            self.days_since_last_event += 1
            self.day_passed = False
            self.fallen_passed = False
            self.night_passed = False

        feast_chance = 100 * (math.pow(self.days_since_last_event, 2) / 55.0) + (9.0 / 55.0)
        fatality_factor = random.randint(2, 4) + self.rounds_without_deaths

        if self.day is 1 and not self.bloodbath_passed:
            step_type = RoundType.BLOODBATH
            fatality_factor += 2
            self.bloodbath_passed = True
        elif not self.day_passed and random.randint(0, 100) < feast_chance:
            step_type = RoundType.FEAST
            self.days_since_last_event = 0
            fatality_factor += 2
        elif self.days_since_last_event > 0 and random.randint(1, 20) is 1:
            step_type = RoundType.ARENA
            self.days_since_last_event = 0
            fatality_factor += 1
        elif not self.day_passed:
            step_type = RoundType.DAY
            self.day_passed = True
        elif self.day_passed and not self.fallen_passed:
            step_type = RoundType.FALLEN
            self.fallen_passed = True
        else:
            step_type = RoundType.NIGHT
            self.night_passed = True

        self.players_available.clear()
        for p in self.players_alive:
            self.players_available.add(p)

        event = None
        if step_type is RoundType.FALLEN:
            messages = []
            for p in self.players_dead_today:
                messages.append("☠️ {0} | District {1}".format(p, p.district))
        else:
            if step_type is RoundType.ARENA:
                event = events['arena'][random.randint(0, len(events['arena']) - 1)]
            else:
                event = events[step_type.value]
            dead_players_now = len(self.players_dead)
            messages = self.__generate_messages(fatality_factor, event)
            if len(self.players_dead) == dead_players_now:
                self.rounds_without_deaths += 1
            else:
                self.rounds_without_deaths = 0

        summary = {
            'day': self.day,
            'roundType': step_type.value,
            'messages': messages,
            'footer': "Tributes Remaining: {0}/{1} | Host: {2}"
                      .format(len(self.players_alive), len(self.players), self.owner_name)
        }

        if step_type is RoundType.FALLEN:
            summary['title'] = "{0} | {1}".format(self.title, "Fallen Tributes {0}".format(self.day))
            if len(self.players_dead_today) > 1:
                summary['description'] = "{0} cannon shots can be heard in the distance.".format(
                    len(self.players_dead_today))
                self.players_dead_today.clear()
            elif len(self.players_dead_today) is 1:
                summary['description'] = "1 cannon shot can be heard in the distance."
                self.players_dead_today.clear()
            else:
                summary['description'] = "No cannon shots are heard."
            summary['color'] = 0xaaaaaa
        else:
            summary['title'] = "{0} | {1}".format(self.title, event['title'].format(self.day))
            summary['description'] = event['description']
            summary['color'] = event['color']

        return summary

    def __generate_messages(self, fatality_factor, event):
        messages = []
        while len(self.players_available) > 0:
            f = random.randint(0, 10)
            if f < fatality_factor and len(self.players_alive) > 1:
                # time to die
                action = random.choice(event['fatal'])
                if action['killed'] is list and len(action['killed']) >= len(self.players_alive):
                    # must have one player remaining
                    continue
            else:
                # live to see another round
                action = random.choice(event['nonfatal'])

            tributes = action['tributes']
            if tributes > len(self.players_available):
                # not enough tributes for this action
                continue

            p = random.choice(tuple(self.players_available))
            self.players_available.remove(p)
            active_players = [p]

            extra_tributes = tributes - 1
            while extra_tributes > 0:
                p = random.choice(tuple(self.players_available))
                self.players_available.remove(p)
                active_players.append(p)
                extra_tributes -= 1

            msg = action['msg'].format(*active_players)

            if action.get('killed') is not None:
                if action.get('killer') is not None:
                    for kr in action['killer']:
                        active_players[kr].kills += len(action['killed'])
                for kd in action['killed']:
                    active_players[kd].alive = False
                    self.players_dead.append(active_players[kd])
                    self.players_dead_today.append(active_players[kd])
                    self.players_alive.remove(active_players[kd])
                    active_players[kd].cause_of_death = msg

            messages.append(msg)
        return messages
