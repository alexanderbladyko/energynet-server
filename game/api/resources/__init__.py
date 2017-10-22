from game.api.base import ApiStepRunner
from game.api.resources.buy import steps as resources_buy_steps


resources_buy = ApiStepRunner(resources_buy_steps)
