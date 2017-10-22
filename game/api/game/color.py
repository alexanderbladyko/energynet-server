from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game, Player
from game.api.base import BaseStep, TurnCheckStep


class ColorsTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.COLORS

    def __init__(self):
        super()
        self.check_turn = False


class ColorIsValidCheckStep(BaseStep):
    game_fields = [Game.map]

    def check_parameters(self, color, *args, **kwargs):
        if color not in self.map_config.get('colors'):
            raise EnergynetException(message='Color is invalid')


class PlayerHasNoColorCheckStep(BaseStep):
    player_fields = [Player.color]

    def check_parameters(self, *args, **kwargs):
        if self.player.color is not None:
            raise EnergynetException(message='Player has color')


class ColorIsTakenCheckStep(BaseStep):
    game_fields = [Game.reserved_colors]

    def check_parameters(self, color, *args, **kwargs):
        if color in self.game.reserved_colors:
            raise EnergynetException(message='Color is taken')


class AddColorStep(BaseStep):
    def action(self, pipe, color):
        pipe.sadd(Game.reserved_colors.key(self.game.id), color)
        pipe.set(Player.color.key(self.player.id), color)


class AuctionIfEverybodyHasColorStep(BaseStep):
    def action(self, pipe, color):
        users_count = pipe.scard(Game.user_ids.key(self.game.id))
        colors_count = pipe.scard(Game.reserved_colors.key(self.game.id))
        if colors_count == users_count:
            Game.step.write(pipe, StepTypes.AUCTION, self.game.id)


steps = [
    ColorsTurnCheckStep(),
    ColorIsValidCheckStep(),
    PlayerHasNoColorCheckStep(),
    ColorIsTakenCheckStep(),
    AddColorStep(),
    AuctionIfEverybodyHasColorStep(),
]
