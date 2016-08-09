class EnergynetException(Exception):
    def __init__(self, message):
        super(EnergynetException, self).__init__(message)
        self.message = message
