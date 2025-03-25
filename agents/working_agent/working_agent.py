import logging
import math
from random import randint
from time import time
from typing import cast

from geniusweb.actions.Accept import Accept
from geniusweb.actions.Action import Action
from geniusweb.actions.Offer import Offer
from geniusweb.actions.PartyId import PartyId
from geniusweb.bidspace.AllBidsList import AllBidsList
from geniusweb.inform.ActionDone import ActionDone
from geniusweb.inform.Finished import Finished
from geniusweb.inform.Inform import Inform
from geniusweb.inform.Settings import Settings
from geniusweb.inform.YourTurn import YourTurn
from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.Domain import Domain
from geniusweb.party.Capabilities import Capabilities
from geniusweb.party.DefaultParty import DefaultParty
from geniusweb.profile.utilityspace.LinearAdditiveUtilitySpace import (
    LinearAdditiveUtilitySpace,
)
from geniusweb.profileconnection.ProfileConnectionFactory import (
    ProfileConnectionFactory,
)
from geniusweb.progress.ProgressTime import ProgressTime
from geniusweb.references.Parameters import Parameters
from tudelft_utilities_logging.ReportToLogger import ReportToLogger

from .utils.opponent_model import OpponentModel


class WorkingAgent(DefaultParty):
    def __init__(self):
        super().__init__()
        self.logger: ReportToLogger = self.getReporter()

        self.domain: Domain = None
        self.parameters: Parameters = None
        self.profile: LinearAdditiveUtilitySpace = None
        self.progress: ProgressTime = None
        self.me: PartyId = None
        self.other: str = None
        self.settings: Settings = None
        self.storage_dir: str = None

        self.last_received_bid: Bid = None
        self.opponent_model: OpponentModel = None
        self.logger.log(logging.INFO, "WorkingAgent initialized.")

    def notifyChange(self, data: Inform):
        if isinstance(data, Settings):
            self.settings = cast(Settings, data)
            self.me = self.settings.getID()
            self.progress = self.settings.getProgress()
            self.parameters = self.settings.getParameters()
            self.storage_dir = self.parameters.get("storage_dir")

            profile_connection = ProfileConnectionFactory.create(
                data.getProfile().getURI(), self.getReporter()
            )
            self.profile = profile_connection.getProfile()
            self.domain = self.profile.getDomain()
            profile_connection.close()

        elif isinstance(data, ActionDone):
            action = cast(ActionDone, data).getAction()
            actor = action.getActor()

            if actor != self.me:
                self.other = str(actor).rsplit("_", 1)[0]
                self.opponent_action(action)

        elif isinstance(data, YourTurn):
            self.my_turn()

        elif isinstance(data, Finished):
            self.logger.log(logging.INFO, "Negotiation finished.")
            super().terminate()
        else:
            self.logger.log(logging.WARNING, f"Unknown inform type: {data}")

    def getCapabilities(self) -> Capabilities:
        return Capabilities(
            set(["SAOP"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    def getDescription(self) -> str:
        return "Agent inspired by interest-based negotiation and Pareto-efficiency."

    def send_action(self, action: Action):
        self.getConnection().send(action)

    def opponent_action(self, action):
        if isinstance(action, Offer):
            if self.opponent_model is None:
                self.opponent_model = OpponentModel(self.domain)

            bid = cast(Offer, action).getBid()
            self.opponent_model.update(bid)
            self.last_received_bid = bid

    def my_turn(self):
        if self.accept_condition(self.last_received_bid):
            self.send_action(Accept(self.me, self.last_received_bid))
        else:
            offer = self.find_bid()
            self.send_action(Offer(self.me, offer))

    def accept_condition(self, bid: Bid) -> bool:
        if bid is None:
            return False

        progress = self.progress.get(time() * 1000)
        utility = float(self.profile.getUtility(bid))

        # Smoother sigmoid threshold curve to allow earlier agreements
        threshold = 0.9 * (1 - 1 / (1 + math.exp(-10 * (progress - 0.7))))
        return utility >= threshold

    def find_bid(self) -> Bid:
        domain = self.profile.getDomain()
        all_bids = AllBidsList(domain)

        # Maintain top-N best-scoring bids for diversity and opponent friendliness
        scored_bids = []
        for _ in range(500):
            bid = all_bids.get(randint(0, all_bids.size() - 1))
            score = self.score_bid(bid)
            scored_bids.append((score, bid))

        # Sort by score (Pareto-inspired)
        scored_bids.sort(reverse=True)
        top_bids = [bid for _, bid in scored_bids[:10]]

        # Pick one of top bids with slight randomness (avoid sticking to same bids)
        return top_bids[randint(0, len(top_bids) - 1)]

    def score_bid(self, bid: Bid) -> float:
        progress = self.progress.get(time() * 1000)
        our_utility = float(self.profile.getUtility(bid))

        if self.opponent_model is not None:
            opponent_utility = self.opponent_model.get_predicted_utility(bid)
        else:
            opponent_utility = 0.0

        # Nash Product as optimization criterion (win-win)
        nash_product = our_utility * opponent_utility

        # Balance own interest and joint benefit depending on progress
        alpha = 0.85 - 0.5 * progress  # shift from selfish to collaborative
        return alpha * our_utility + (1 - alpha) * nash_product
