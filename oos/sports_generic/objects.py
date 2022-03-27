# AUTOGENERATED! DO NOT EDIT! File to edit: 01_sports_generic.objects.ipynb (unless otherwise specified).

__all__ = ['Team', 'Player', 'Game']

# Cell

import uuid
# from handlers.players import Players
from ..base import Base_Object

class Team(Base_Object):
    '''
    Simple class to hold team info
    '''

    # _object_id = None
    _name = None
    _name_id = None
    _division = None
    _seed = None
    _players = None
    _ids = None

    def __init__(self, object_id=None, name=None, division=None,
                 seed=None, players=None):
        self._name = str(name) if name else 'Unknown'
        self._name_id = str(uuid.uuid3(uuid.NAMESPACE_OID, self._name))
        object_id = object_id if object_id \
                                    else self._name_id
        super().__init__(object_id=object_id)
        self._division = str(division) if division is not None \
                                       else None
        self._seed = seed
        if players is not None:
            self._players = players
        else:
            self._players = None

        self._ids = list(set([self._name, self._name_id, self._object_id]))

    @property
    def name(self):
        '''
        name of team
        '''
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name
        self._name_id = str(uuid.uuid3(uuid.NAMESPACE_OID, self._name))

    @property
    def division(self):
        return self._division

    @property
    def seed(self):
        return self._seed

    @property
    def division(self):
        return self._division

    @property
    def encoding(self):
        return {self._name: self._object_id}

    @property
    def decoding(self):
        return {self._object_id: self._name}


    def __repr__(self):
        return f'{self.name}'

    def get_players(self):
        return self._players

    def set_players(self, players):
        assert isinstance(players, type(Players()))
        self._players = players

    def add_alt_id(self, alt_id):
        alt_id = str(alt_id)
        if alt_id in self._ids:
            return
        self._ids.append(alt_id)

    def remove_alt_id(self, alt_id):
        alt_id = str(alt_id)
        if alt_id in self._ids:
            self._ids.remove(alt_id)

    def get_alt_ids(self):
        return self._ids


# Cell

class Player(Base_Object):
    '''
    Game class is an object for each tournament slot that is
    populated as the tournament continues. It also holds functions
    relavent to a game like updating teams from the results dict
    and returning a winner based on the predictions from the
    submission class.
    '''

    _name = None
    _name_id = None
    _age = None
    _position = None
    _height = None
    _weight = None
    _college = None
    _team_id = None

    def __init__(self, object_id=None, name=None, age=None, position=None,
                 height = None, weight=None, college=None,
                 team_id=None):

        self._name= str(name) if name else 'Unknown'
        self._name_id = str(uuid.uuid3(uuid.NAMESPACE_OID, self._name))
        self._object_id = self._object_id if self._object_id \
                                          else self._name_id

        super().__init__(object_id=self._object_id)
        self._age = int(age) if age else None
        self._position = str(position) if position else None
        self._height = float(height) if height else None
        self._weight = float(weight) if weight else None
        self._college = str(college) if college else None
        self._team_id = str(team_id) if team_id else None

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self._age

    @property
    def position(self):
        return self._position

    @property
    def height(self):
        return self._height

    @property
    def weight(self):
        return self._weight

    @property
    def college(self):
        return self._college

    @property
    def team_id(self):
        return self._team_id

    def __repr__(self):
        return self._name

# Cell

class Game(Base_Object):
    '''
    Game class is an object for each tournament slot that is
    populated as the tournament continues. It also holds functions
    relavent to a game like updating teams from the results dict
    and returning a winner based on the predictions from the
    submission class.
    '''

    _object_id = None
    _t1_id = None
    _t2_id = None
    _t1_score = None
    _t2_score = None
    _win_id = None
    _day = None
    _year = None
    _location = None

    def __init__(self, object_id=None, t1_id=None, t2_id=None,
                 t1_score=None, t2_score=None, win_id=None,
                 day=None, year=None, location=None, teams=None,
                 players=None):
        self._object_id = self._object_id if self._object_id \
                                          else str(uuid.uuid4())

        super().__init__(object_id=self._object_id)
        self._t1_id = str(t1_id) if t1_id else None
        self._t2_id = str(t2_id) if t2_id else None
        self._t1_score = int(t1_score) if t1_score else None
        self._t2_score = int(t2_score) if t2_score else None
        self._t2_score = str(win_id) if win_id else None
        self._day = day if day else None
        self._year = year if year else None
        self._location = location if location else None
        if teams is not None:
            self._teams = teams.query(
                f'object_id in {[self._t1_id, self._t2_id]}'
                )
            self._t1_name = self._teams.objects.get(self._t1_id).name
            self._t2_name = self._teams.objects.get(self._t2_id).name

        if players is not None:
            self._t1_players = teams.query(f'team_id == {self._t1_id}')
            self._t2_players = teams.query(f'team_id == {self._t2_id}')

    @property
    def t1_id(self):
        return self._t1_id

    @property
    def t2_id(self):
        return self._t2_id

    @property
    def t1_score(self):
        return self._t1_score

    @property
    def t2_score(self):
        return self._t2_score

    @property
    def win_id(self):
        return self._win_id

    @property
    def day(self):
        return self._day

    @property
    def year(self):
        return self._year

    @property
    def location(self):
        return self._location

    def __repr__(self):
        if self._teams is not None:
            return f'{self._t1_name} vs. {self._t2_name}'