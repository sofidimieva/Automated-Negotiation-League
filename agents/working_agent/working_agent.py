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

from .utils.opponent_model import OpponentModel

from typing import List


class WorkingAgent(DefaultParty):
    """
    Template of a Python geniusweb agent.
    """

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
        self.logger.log(logging.INFO, "party is initialized")

    def notifyChange(self, data: Inform):
        """MUST BE IMPLEMENTED
        This is the entry point of all interaction with your agent after is has been initialised.
        How to handle the received data is based on its class type.

        Args:
            info (Inform): Contains either a request for action or information.
        """

        # a Settings message is the first message that will be send to your
        # agent containing all the information about the negotiation session.
        if isinstance(data, Settings):
            self.settings = cast(Settings, data)
            self.me = self.settings.getID()

            # progress towards the deadline has to be tracked manually through the use of the Progress object
            self.progress = self.settings.getProgress()

            self.parameters = self.settings.getParameters()
            self.storage_dir = self.parameters.get("storage_dir")

            # the profile contains the preferences of the agent over the domain
            profile_connection = ProfileConnectionFactory.create(
                data.getProfile().getURI(), self.getReporter()
            )
            self.profile = profile_connection.getProfile()
            self.domain = self.profile.getDomain()
            profile_connection.close()

        # ActionDone informs you of an action (an offer or an accept)
        # that is performed by one of the agents (including yourself).
        elif isinstance(data, ActionDone):
            action = cast(ActionDone, data).getAction()
            actor = action.getActor()

            # ignore action if it is our action
            if actor != self.me:
                # obtain the name of the opponent, cutting of the position ID.
                self.other = str(actor).rsplit("_", 1)[0]

                # process action done by opponent
                self.opponent_action(action)
        # YourTurn notifies you that it is your turn to act
        elif isinstance(data, YourTurn):
            # execute a turn
            self.my_turn()

        # Finished will be send if the negotiation has ended (through agreement or deadline)
        elif isinstance(data, Finished):
            self.save_data()
            # terminate the agent MUST BE CALLED
            self.logger.log(logging.INFO, "party is terminating:")
            super().terminate()
        else:
            self.logger.log(logging.WARNING, "Ignoring unknown info " + str(data))

    def getCapabilities(self) -> Capabilities:
        """MUST BE IMPLEMENTED
        Method to indicate to the protocol what the capabilities of this agent are.
        Leave it as is for the ANL 2022 competition

        Returns:
            Capabilities: Capabilities representation class
        """
        return Capabilities(
            set(["SAOP"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    def send_action(self, action: Action):
        """Sends an action to the opponent(s)

        Args:
            action (Action): action of this agent
        """
        self.getConnection().send(action)

    # give a description of your agent
    def getDescription(self) -> str:
        """MUST BE IMPLEMENTED
        Returns a description of your agent. 1 or 2 sentences.

        Returns:
            str: Agent description
        """
        return "Template agent for the ANL 2022 competition"

    def opponent_action(self, action):
        """Process an action that was received from the opponent.

        Args:
            action (Action): action of opponent
        """
        # if it is an offer, set the last received bid
        if isinstance(action, Offer):
            # create opponent model if it was not yet initialised
            if self.opponent_model is None:
                self.opponent_model = OpponentModel(self.domain)

            bid = cast(Offer, action).getBid()

            # update opponent model with bid
            self.opponent_model.update(bid)
            # set bid as last received
            self.last_received_bid = bid

    def my_turn(self):
        """This method is called when it is our turn. It should decide upon an action
        to perform and send this action to the opponent.
        """
        # check if the last received offer is good enough
        if self.accept_condition(self.last_received_bid):
            # if so, accept the offer
            action = Accept(self.me, self.last_received_bid)
        else:
            # if not, find a bid to propose as counter offer
            bid = self.find_bid()
            action = Offer(self.me, bid)

        # send the action
        self.send_action(action)

    def save_data(self):
        """This method is called after the negotiation is finished. It can be used to store data
        for learning capabilities. Note that no extensive calculations can be done within this method.
        Taking too much time might result in your agent being killed, so use it for storage only.
        """
        data = "Data for learning (see README.md)"
        with open(f"{self.storage_dir}/data.md", "w") as f:
            f.write(data)

    ###########################################################################################
    ################################## Example methods below ##################################
    ###########################################################################################

    def accept_condition(self, bid: Bid) -> bool:
        if bid is None:
            return False

        progress = self.progress.get(time() * 1000)
        our_util = float(self.profile.getUtility(bid))
        opp_util = float(self.opponent_model.get_predicted_utility(bid))
        
        # Generate sample bids and compute Pareto frontier
        sample = self._generate_bid_sample(5000)
        pareto_bids = self._compute_pareto_frontier(sample)
        
        # Calculate maximum possible Nash product in current frontier
        max_nash = max(
            float(self.profile.getUtility(b)) * float(self.opponent_model.get_predicted_utility(b))
            for b in pareto_bids
        ) if pareto_bids else 0
        
        current_nash = our_util * opp_util
        
        # Accept if either:
        # 1. Current Nash is within 95% of maximum possible (with time-based tolerance)
        # 2. Time is running out and offer is better than our reservation value
        time_pressure = progress ** 3  # more aggressive concession near deadline
        nash_threshold = max_nash * (0.95 - 0.25 * time_pressure)
        min_utility = 0.7 - 0.3 * time_pressure
        
        return current_nash >= nash_threshold and our_util >= min_utility

   

    def find_bid(self) -> Bid:
        # Generate large sample of bids
        sample_bids = self._generate_bid_sample(5000)
        
        # Compute Pareto frontier
        pareto_bids = self._compute_pareto_frontier(sample_bids)
        
        # If no Pareto bids (early in negotiation), return random good bid
        if not pareto_bids:
            return self._generate_bid_sample(1)[0]
        
        # Find bid with maximum Nash product
        max_nash = -1
        best_bid = None
        for bid in pareto_bids:
            our_util = float(self.profile.getUtility(bid))
            opp_util = float(self.opponent_model.get_predicted_utility(bid))
            nash = our_util * opp_util
            if nash > max_nash:
                max_nash = nash
                best_bid = bid
        
        # Fallback if no good bid found
        return best_bid if best_bid else self._generate_bid_sample(1)[0]

    def _generate_bid_sample(self, num_bids: int) -> List[Bid]:
        """Generate a sample of bids using AllBidsList for random selection."""

        all_bids = AllBidsList(self.domain)
        return [all_bids.get(randint(0, all_bids.size() - 1)) for _ in range(num_bids)]


    def _compute_pareto_frontier(self, bids: List[Bid]) -> List[Bid]:
        utilities = []
        for bid in bids:
            our_util = float(self.profile.getUtility(bid))
            opp_util = float(self.opponent_model.get_predicted_utility(bid))
            utilities.append((our_util, opp_util, bid))
        
        # Sort by descending our utility
        sorted_utils = sorted(utilities, key=lambda x: (-x[0], -x[1]))
        
        # Extract Pareto optimal bids
        pareto = []
        max_opp = -1
        for util in sorted_utils:
            if util[1] > max_opp:
                pareto.append(util[2])
                max_opp = util[1]
        return pareto

    

