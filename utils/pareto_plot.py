import os
from collections import defaultdict
import plotly.graph_objects as go
import numpy as np

def is_pareto_efficient(points):
    """Find the Pareto frontier from a set of points."""
    points = np.array(points)
    pareto = np.ones(points.shape[0], dtype=bool)
    for i, point in enumerate(points):
        if pareto[i]:
            pareto[pareto] = np.any(points[pareto] > point, axis=1)
            pareto[i] = True
    return points[pareto]

def find_nash_point(points):
    """Find the Nash bargaining solution by maximizing the Nash product (u1 * u2)."""
    points = np.array(points)
    nash_index = np.argmax(points[:, 0] * points[:, 1])
    return points[nash_index]

def plot_trace_pareto(results_trace: dict, plot_file: str):
    utilities = []
    agreements = []
    
    for action in results_trace["actions"]:
        if "Offer" in action:
            offer = action["Offer"]
            utility_values = list(offer["utilities"].values())
            utilities.append(utility_values)
        elif "Accept" in action:
            offer = action["Accept"]
            utility_values = list(offer["utilities"].values())
            agreements.append(utility_values)
    
    # Compute Pareto Frontier
    pareto_frontier = is_pareto_efficient(utilities)
    pareto_frontier = pareto_frontier[np.argsort(pareto_frontier[:, 0])]  # Sort for line plot
    
    # Compute Nash point
    nash_point = find_nash_point(pareto_frontier)
    
    fig = go.Figure()
    
    # Plot all offers
    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=[u[0] for u in utilities],
            y=[u[1] for u in utilities],
            name="Offers",
            marker={"color": "blue", "size": 5},
            hoverinfo="text",
        )
    )
    
    # Plot agreements with bigger green markers
    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=[a[0] for a in agreements],
            y=[a[1] for a in agreements],
            name="Agreements",
            marker={"color": "green", "size": 15},
            hoverinfo="text",
        )
    )
    
    # Plot Pareto frontier as a connected line
    fig.add_trace(
        go.Scatter(
            mode="lines+markers",
            x=[p[0] for p in pareto_frontier],
            y=[p[1] for p in pareto_frontier],
            name="Pareto frontier",
            marker={"color": "purple", "size": 8},
            line={"color": "purple", "width": 2},
            hoverinfo="text",
        )
    )
    
    # Plot Nash bargaining solution
    fig.add_trace(
        go.Scatter(
            mode="markers",
            x=[nash_point[0]],
            y=[nash_point[1]],
            name="Nash Product",
            marker={"color": "red", "size": 15, "symbol": "star"},
            hoverinfo="text",
        )
    )
    
    fig.update_layout(
        xaxis_title="Opponent's Utility",
        yaxis_title="Our Utility",
        height=800,
        legend={
            "yanchor": "bottom",
            "y": 1,
            "xanchor": "left",
            "x": 0,
        },
    )
    fig.write_html(f"{os.path.splitext(plot_file)[0]}_utility_space.html")
