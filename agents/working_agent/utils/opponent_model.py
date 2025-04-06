from collections import defaultdict

from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.DiscreteValueSet import DiscreteValueSet
from geniusweb.issuevalue.Domain import Domain
from geniusweb.issuevalue.Value import Value


class OpponentModel:
    def __init__(self, domain: Domain, decay_factor: float = 0.2):
        self.offers = []
        self.domain = domain
        self.decay_factor = decay_factor

        self.issue_estimators = {
            i: IssueEstimator(v, decay_factor) for i, v in domain.getIssuesValues().items()
        }

    def update(self, bid: Bid):
        # keep track of all bids received
        self.offers.append(bid)

        # update all issue estimators with the value that is offered for that issue
        for issue_id, issue_estimator in self.issue_estimators.items():
            issue_estimator.update(bid.getValue(issue_id))

    def get_predicted_utility(self, bid: Bid):
        if len(self.offers) == 0 or bid is None:
            return 0

        value_utilities = []
        issue_weights = []

        for issue_id, issue_estimator in self.issue_estimators.items():
            value = bid.getValue(issue_id)

            value_utilities.append(issue_estimator.get_value_utility(value))
            issue_weights.append(issue_estimator.weight)

        # Calculate predicted utility using a hard-headed frequency-based approach
        predicted_utility = sum([iw * vu for iw, vu in zip(issue_weights, value_utilities)])

        return predicted_utility


class IssueEstimator:
    def __init__(self, value_set: DiscreteValueSet, decay_factor: float):
        if not isinstance(value_set, DiscreteValueSet):
            raise TypeError("This issue estimator only supports issues with discrete values")

        self.bids_received = 0
        self.max_value_count = 0
        self.value_trackers = defaultdict(lambda: ValueEstimator(decay_factor))
        self.weight = 0
        self.decay_factor = decay_factor

    def update(self, value: Value):
        self.bids_received += 1

        # Apply decay to all value trackers before updating
        for tracker in self.value_trackers.values():
            tracker.apply_decay()

        value_tracker = self.value_trackers[value]
        value_tracker.update()

        self.max_value_count = max([value_tracker.count, self.max_value_count])

        # Update weight directly based on frequency of the most common value
        self.weight = self.max_value_count / self.bids_received

        # Recalculate utilities for all values
        for value_tracker in self.value_trackers.values():
            value_tracker.recalculate_utility(self.max_value_count)

    def get_value_utility(self, value: Value):
        if value in self.value_trackers:
            return self.value_trackers[value].utility
        return 0


class ValueEstimator:
    def __init__(self, decay_factor: float):
        self.count = 0.0  # Using float to accommodate decay effects
        self.utility = 0.0
        self.decay_factor = decay_factor

    def update(self):
        self.count += 1

    def apply_decay(self):
        # Apply decay to the count
        self.count *= (1 - self.decay_factor)

    def recalculate_utility(self, max_value_count: int):
        # Utility is calculated as a ratio of the value's count to the maximum count observed
        self.utility = self.count / max_value_count if max_value_count > 0 else 1
