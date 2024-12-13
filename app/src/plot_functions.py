import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import statsmodels.api as sm

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

def plt_hist(data, label, title, xaxis_range=[0, 200]):
    fig = px.histogram(data, x=label, title=title)
    
    xticks = list(range(xaxis_range[0], xaxis_range[1] + 1, 10)) # 10 minutes ticks with 200 of range gives nice results
    
    fig.update_layout(
        xaxis=dict(
            range=xaxis_range, # Explicitly gives him instruction for the range or else he fucks up i don't know why
            tickmode='array',   
            tickvals=xticks,    
            ticktext=[str(tick) for tick in xticks]  # Just to get the minutes values in text
        )
    )
    
    return fig


def plot_line_chart(data, x, y, title):

    X = data[x]
    Y = data[y]
    X = sm.add_constant(X)
    OLS_line = sm.OLS(Y, X).fit()
    data['Predicted Rating'] = OLS_line.predict(X)

    fig = px.line(
        data,
        x=x,
        y=y,
        title=title
    )
    fig.add_trace(
        go.Scatter(
            x=data['Year'],
            y=data['Predicted Rating'],
            mode='lines',
            name='OLS Regression Line',
            line=dict(dash='dash', color='red')
        )
    )
    return fig, OLS_line.pvalues[x], OLS_line.rsquared, OLS_line.params['Year']