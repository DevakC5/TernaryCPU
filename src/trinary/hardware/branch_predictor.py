"""Branch predictor — static and dynamic prediction."""


class BranchPredictor:
    """Branch predictor with static and 2-bit saturating counter modes.

    Modes:
      'always_taken' — predict taken always
      'always_not_taken' — predict not taken always
      'two_bit' — 2-bit saturating counters per branch address
    """

    def __init__(self, mode='two_bit', penalty_cycles=2):
        self.mode = mode
        self.penalty_cycles = penalty_cycles
        self._counters = {}
        self._history = {}
        self.predictions = 0
        self.mispredictions = 0
        self.taken_predictions = 0
        self.not_taken_predictions = 0

    def predict(self, branch_addr):
        """Predict whether a branch at addr will be taken.

        Returns:
            bool: True if taken, False if not taken.
        """
        self.predictions += 1
        if self.mode == 'always_taken':
            self.taken_predictions += 1
            return True
        elif self.mode == 'always_not_taken':
            self.not_taken_predictions += 1
            return False
        elif self.mode == 'two_bit':
            counter = self._counters.get(branch_addr, 2)
            taken = counter >= 2
            if taken:
                self.taken_predictions += 1
            else:
                self.not_taken_predictions += 1
            return taken
        return False

    def update(self, branch_addr, actually_taken):
        """Update predictor state after actual branch outcome."""
        if actually_taken:
            self._history[branch_addr] = self._history.get(branch_addr, 0) + 1
        if self.mode == 'two_bit':
            counter = self._counters.get(branch_addr, 2)
            if actually_taken:
                counter = min(3, counter + 1)
            else:
                counter = max(0, counter - 1)
            self._counters[branch_addr] = counter

    def record_mispredict(self):
        self.mispredictions += 1

    @property
    def accuracy(self):
        if self.predictions == 0:
            return 1.0
        return 1.0 - (self.mispredictions / self.predictions)

    def reset(self):
        self._counters.clear()
        self._history.clear()
        self.predictions = 0
        self.mispredictions = 0
        self.taken_predictions = 0
        self.not_taken_predictions = 0

    def stats(self):
        return {
            "mode": self.mode,
            "predictions": self.predictions,
            "mispredictions": self.mispredictions,
            "accuracy": self.accuracy,
            "penalty_cycles": self.penalty_cycles,
        }
