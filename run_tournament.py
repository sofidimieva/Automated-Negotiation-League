import json
import os
from pathlib import Path
import time
import matplotlib.pyplot as plt
from utils.runners import run_tournament

RESULTS_DIR = Path("results", time.strftime('%Y%m%d-%H%M%S'))

# create results directory if it does not exist
if not RESULTS_DIR.exists():
    RESULTS_DIR.mkdir(parents=True)

# Settings to run a negotiation session:
#   You need to specify the classpath of 2 agents to start a negotiation. Parameters for the agent can be added as a dict (see example)
#   You need to specify the preference profiles for both agents. The first profile will be assigned to the first agent.
#   You need to specify a time deadline (is milliseconds (ms)) we are allowed to negotiate before we end without agreement.
tournament_settings = {
    "agents": [
        {
            "class": "agents.working_agent.working_agent.WorkingAgent",
            "parameters": {"storage_dir": "agent_storage/WorkingAgent"},
        },
        {
            "class": "agents.boulware_agent.boulware_agent.BoulwareAgent",
        },
        {
            "class": "agents.conceder_agent.conceder_agent.ConcederAgent",
        },
        {
            "class": "agents.hardliner_agent.hardliner_agent.HardlinerAgent",
        },
        {
            "class": "agents.linear_agent.linear_agent.LinearAgent",
        },
        {
            "class": "agents.random_agent.random_agent.RandomAgent",
        },
        {
            "class": "agents.stupid_agent.stupid_agent.StupidAgent",
        },
        {
            "class": "agents.CSE3210.agent2.agent2.Agent2",
        },
        {
            "class": "agents.CSE3210.agent3.agent3.Agent3",
        },
        {
            "class": "agents.CSE3210.agent7.agent7.Agent7",
        },
        {
            "class": "agents.CSE3210.agent11.agent11.Agent11",
        },
        {
            "class": "agents.CSE3210.agent14.agent14.Agent14",
        },
        {
            "class": "agents.CSE3210.agent18.agent18.Agent18",
        },
        {
            "class": "agents.CSE3210.agent19.agent19.Agent19",
        },
        {
            "class": "agents.CSE3210.agent22.agent22.Agent22",
        },
        # {
        #     "class": "agents.CSE3210.agent24.agent24.Agent24",
        # },
        # {
        #     "class": "agents.CSE3210.agent25.agent25.Agent25",
        # },
        # {
        #     "class": "agents.CSE3210.agent26.agent26.Agent26",
        # },
        # {
        #     "class": "agents.CSE3210.agent27.agent27.Agent27",
        # },
        # {
        #     "class": "agents.CSE3210.agent29.agent29.Agent29",
        # },
        # {
        #     "class": "agents.CSE3210.agent32.agent32.Agent32",
        # },
        # {
        #     "class": "agents.CSE3210.agent33.agent33.Agent33",
        # },
        # {
        #     "class": "agents.CSE3210.agent41.agent41.Agent41",
        # },
        # {
        #     "class": "agents.CSE3210.agent43.agent43.Agent43",
        # },
        # {
        #     "class": "agents.CSE3210.agent50.agent50.Agent50",
        # },
        # {
        #     "class": "agents.CSE3210.agent52.agent52.Agent52",
        # },
        # {
        #     "class": "agents.CSE3210.agent55.agent55.Agent55",
        # },
        # {
        #     "class": "agents.CSE3210.agent58.agent58.Agent58",
        # },
        # {
        #     "class": "agents.CSE3210.agent61.agent61.Agent61",
        # },
        # {
        #     "class": "agents.CSE3210.agent64.agent64.Agent64",
        # },
        # {
        #     "class": "agents.CSE3210.agent67.agent67.Agent67",
        # },
        # {
        #     "class": "agents.CSE3210.agent68.agent68.Agent68",
        # },
    ],
    "profile_sets": [
        ["domains/domain00/profileA.json", "domains/domain00/profileB.json"],
    ],
    "deadline_time_ms": 10000,
}

def plot_tournament_results(tournament_results_summary, results_dir):
    """Plot tournament results with sorted values and highlight WorkingAgent."""
    # Sort the DataFrame by each metric before plotting
    working_agent = "WorkingAgent"

    # Plot average utility
    sorted_avg_utility = tournament_results_summary.sort_values("avg_utility", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["orange" if working_agent in agent else "skyblue" for agent in sorted_avg_utility.index]
    sorted_avg_utility["avg_utility"].plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Average Utility per Agent")
    ax.set_xlabel("Agent")
    ax.set_ylabel("Average Utility")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(results_dir.joinpath("avg_utility_sorted.png"))
    plt.close()

    # Plot Nash product
    sorted_nash_product = tournament_results_summary.sort_values("avg_nash_product", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["orange" if working_agent in agent else "skyblue" for agent in sorted_nash_product.index]
    sorted_nash_product["avg_nash_product"].plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Average Nash Product per Agent")
    ax.set_xlabel("Agent")
    ax.set_ylabel("Average Nash Product")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(results_dir.joinpath("avg_nash_product_sorted.png"))
    plt.close()

    # Plot social welfare
    sorted_social_welfare = tournament_results_summary.sort_values("avg_social_welfare", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["orange" if working_agent in agent else "skyblue" for agent in sorted_social_welfare.index]
    sorted_social_welfare["avg_social_welfare"].plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Average Social Welfare per Agent")
    ax.set_xlabel("Agent")
    ax.set_ylabel("Average Social Welfare")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(results_dir.joinpath("avg_social_welfare_sorted.png"))
    plt.close()

    # Plot number of agreements
    sorted_agreements = tournament_results_summary.sort_values("agreement", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["orange" if working_agent in agent else "skyblue" for agent in sorted_agreements.index]
    sorted_agreements["agreement"].plot(kind="bar", ax=ax, color=colors)
    ax.set_title("Number of Agreements per Agent")
    ax.set_xlabel("Agent")
    ax.set_ylabel("Number of Agreements")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(results_dir.joinpath("agreements_sorted.png"))
    plt.close()


# run a session and obtain results in dictionaries
tournament_steps, tournament_results, tournament_results_summary = run_tournament(tournament_settings)




# save the tournament settings for reference
with open(RESULTS_DIR.joinpath("tournament_steps.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps(tournament_steps, indent=2))
# save the tournament results
with open(RESULTS_DIR.joinpath("tournament_results.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps(tournament_results, indent=2))
# save the tournament results summary
tournament_results_summary.to_csv(RESULTS_DIR.joinpath("tournament_results_summary.csv"))
# plot the tournament results
plot_tournament_results(tournament_results_summary, RESULTS_DIR)
