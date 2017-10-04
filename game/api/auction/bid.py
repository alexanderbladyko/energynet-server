from base.exceptions import EnergynetException
from core.constants import StepTypes
from core.models import Game
from game.api.base import BaseStep, TurnCheckStep, StationCheckStep


class AuctionTurnCheckStep(TurnCheckStep):
    step_type = StepTypes.AUCTION


class AuctionBidCheckStep(BaseStep):
    game_fields = [Game.auction]

    def before_action(self, station, bid, *args, **kwargs):
        import pdb; pdb.set_trace()
        previous_bid = self.game.auction.get('bid')
        if previous_bid and previous_bid >= bid:
            raise EnergynetException('Bid is less than previous bid')
        if bid < station:
            raise EnergynetException('Bid is less than station price')


steps = [
    AuctionTurnCheckStep(),
    StationCheckStep(),
    AuctionBidCheckStep(),
]
