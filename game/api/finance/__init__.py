from game.api.base import ApiStepRunner
from game.api.finance.receive import steps as finance_receive_steps


finance_receive = ApiStepRunner(finance_receive_steps)
