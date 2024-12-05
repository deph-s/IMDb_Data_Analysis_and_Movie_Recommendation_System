import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def plot_radial_chart(labels, values):
    fig = go.Figure(go.Barpolar(
    r=values,  # Count of occurrences or mean duration or some real parameters
    theta=labels,  # Genre names often
    width=1,  # Bar are way too big initially, 1 seems to make things more readable
    marker=dict(color=values, colorscale='Viridis', opacity=0.7), 
    text=values,  # Optional: Display counts as text on the plot
    ))

    # Update the layout for a better polar chart display
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values)],
                tickfont=dict(color='black')
            ),
            angularaxis=dict(
                tickfont=dict(color='white', size=14, family='Arial')  # Customize font properties
            )
        ),
        showlegend=False,
        # Increase the plot size
        width=800,  # Set the width of the plot
        height=800  # Set the height of the plot
    )
    return fig

def plot_bar_chart(labels, values): # Gets two lists as input
    
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(color=values, colorscale='Viridis')))

    fig.update_layout(
        xaxis_title='Genres',
        yaxis_title='Values',
        xaxis_tickangle=-90,
        showlegend=False,
    )

    return fig