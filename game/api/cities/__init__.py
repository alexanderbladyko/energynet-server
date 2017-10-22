from game.api.base import ApiStepRunner
from game.api.cities.buy import steps as cities_buy_steps


cities_buy = ApiStepRunner(cities_buy_steps)
