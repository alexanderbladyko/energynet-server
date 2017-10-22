from game.api.base import ApiStepRunner
from game.api.game.color import steps as color_steps


choose_color = ApiStepRunner(color_steps)
