from game.api.base import ApiStepRunner
from game.api.stations.remove import steps as station_remove_steps


station_remove = ApiStepRunner(station_remove_steps)
