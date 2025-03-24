# Negotiation Practical Assignment

This repository contains our implementation for the **Negotiation Practical Assignment** as part of the Automated Negotiation League (ANL) 2023, using the GeniusWeb framework. Our custom negotiation agent is located in the `working_agent/` directory.

## Overview

This project aims to develop an AI negotiation agent capable of participating in bilateral negotiations under the Stacked Alternating Offers Protocol (SAOP). The agent is evaluated across multiple negotiation domains and against various opponent agents.

The project is organized into the following key phases:

### 1. Project Approach

- **Research & Planning**

  - Study negotiation strategies, opponent modeling, and the GeniusWeb framework.
  - Review relevant academic literature.
  - Design the agent’s architecture and strategy.

- **Implementation**

  - Develop the agent's decision-making and negotiation logic.
  - Implement opponent modeling and adaptive behavior.
  - Integrate offer acceptance and rejection criteria.

- **Evaluation & Reporting**

  - Run tournaments and simulations to evaluate agent performance.
  - Analyze results using negotiation metrics such as utility, social welfare, and Pareto efficiency.
  - Document methodology, results, and analysis in a final report.

## Agent Location

Our custom agent is developed in the `working_agent/` directory. It is based on the competition's template agent and expanded with new strategies and opponent modeling techniques.

## Installation

We recommend using Python 3.9, as this version is used in the competition environment. To install dependencies:

```bash
python3.9 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Running Experiments

To test a single negotiation session with the agent:

```bash
python run.py
```

To run a full tournament where each agent negotiates with every other agent:

```bash
python run_tournament.py
```

Results are generated in the results folder and the plots can be visualized using Live Server
