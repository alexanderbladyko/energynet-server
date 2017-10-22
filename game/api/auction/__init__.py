from game.api.base import ApiStepRunner
from game.api.auction.bid_action import steps as bid_steps
from game.api.auction.pass_action import steps as pass_steps


auction_bid = ApiStepRunner(bid_steps)
auction_pass = ApiStepRunner(pass_steps)
