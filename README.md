# Automated Negotiation Agent

This repository contains a custom AI negotiation agent built using the GeniusWeb framework. The agent is designed to participate in bilateral negotiations under the Stacked Alternating Offers Protocol (SAOP) and was developed to compete within the Automated Negotiation League (ANL) 2023 environment.

The core implementation of the custom agent is located in the `working_agent/` directory.

## Overview

The primary goal of this project is to build an adaptive AI agent capable of maximizing utility and reaching Pareto-efficient agreements against various unknown opponent agents across multiple negotiation domains. 

### Key Features

* **Adaptive Bidding Strategy:** The agent utilizes custom decision-making logic to propose offers based on utility maximization and time-dependent constraints.
* **Opponent Modeling:** Dynamically models the opponent's preferences and negotiation strategy to adapt offers in real-time.
* **Smart Acceptance Criteria:** Employs dynamic thresholds to evaluate and accept or reject incoming offers based on current utility and remaining negotiation time.
* **Evaluation Framework:** Includes scripts to run standalone negotiation sessions or full round-robin tournaments to measure social welfare, Pareto efficiency, and individual utility.

## Repository Structure

* `working_agent/`: Contains the core logic, bidding strategy, and opponent modeling for the custom agent.
* `results/`: Output directory for tournament and simulation logs.

## Installation

It is highly recommended to use **Python 3.9** to ensure full compatibility with the GeniusWeb framework. 

```bash
# Create and activate a virtual environment
python3.9 -m venv .venv

# On macOS/Linux:
source .venv/bin/activate  

# On Windows:
# .venv\Scripts\activate

# Install the required dependencies
pip install -r requirements.txt
