import logging
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


class WorkingAgent(DefaultParty):
    def __init__(self):
        super().__init__()
        self.logger: ReportToLogger = self.getReporter()

        self.domain: Domain = None
        self.parameters: Parameters = None
        self.profile: LinearAdditiveUtilitySpace = None
        self.progress: ProgressTime = None
        self.me: PartyId = None
        self.last_received_bid: Bid = None

        self.logger.log(logging.INFO, "WorkingAgent initialized")

    def notifyChange(self, data: Inform):
        if isinstance(data, Settings):
            self.progress = data.getProgress()
            self.me = data.getID()
            profile_conn = ProfileConnectionFactory.create(
                data.getProfile().getURI(), self.getReporter()
            )
            self.profile = profile_conn.getProfile()
            self.domain = self.profile.getDomain()
            profile_conn.close()

        elif isinstance(data, ActionDone):
            action = cast(ActionDone, data).getAction()
            if action.getActor() != self.me and isinstance(action, Offer):
                self.last_received_bid = cast(Offer, action).getBid()

        elif isinstance(data, YourTurn):
            self.my_turn()

        elif isinstance(data, Finished):
            self.logger.log(logging.INFO, "Negotiation finished.")
            super().terminate()

    def getCapabilities(self) -> Capabilities:
        return Capabilities(
            set(["SAOP"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    def send_action(self, action: Action):
        self.getConnection().send(action)

    def getDescription(self) -> str:
        return "Simple agent that offers high-utility bids and accepts near deadline."

    def my_turn(self):
        progress = self.progress.get(time() * 1000)
        self.logger.log(logging.INFO, f"Progress: {progress:.2f}")

        if self.last_received_bid:
            utility = self.profile.getUtility(self.last_received_bid)
            self.logger.log(logging.INFO, f"Received bid utility: {utility:.3f}")
            if utility > 0.8 and progress > 0.9:
                self.logger.log(logging.INFO, "Accepting bid.")
                self.send_action(Accept(self.me, self.last_received_bid))
                return

        bid = self.find_high_utility_bid()
        self.logger.log(logging.INFO, f"Offering bid with utility: {self.profile.getUtility(bid):.3f}")
        self.send_action(Offer(self.me, bid))
        
    def find_high_utility_bid(self) -> Bid:
        all_bids = AllBidsList(self.domain)
        good_bids = [b for b in all_bids if self.profile.getUtility(b) >= 0.9]

        if good_bids:
            return good_bids[randint(0, len(good_bids) - 1)]
        else:
            return max(all_bids, key=lambda b: self.profile.getUtility(b))
