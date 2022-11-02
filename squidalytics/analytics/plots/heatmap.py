import pandas as pd
import plotly.graph_objects as go


def heatmap(
    df: pd.DataFrame,
    counts: pd.DataFrame | None = None,
    fillna_value: float | None = 0.5,
    color: str = "RdYlGn",
) -> go.Figure:
    """Generates a heatmap of the winrate for the given dataframe.

    Args:
        df (pd.DataFrame): The dataframe to generate the heatmap for.
        counts (pd.DataFrame | None): The number of games played for each cell.
            If None, then the number of games played will not be shown. Defaults
            to None.
        fillna_value (float | None): The value to fill NaN values with. If None,
            then NaN values will not be filled. Defaults to float.
        color (str): The color scheme to use for the heatmap. Defaults to
            "RdYlGn".

    Returns:
        go.Figure: Plotly figure of the heatmap.
    """
    df = df.copy()
    if fillna_value is not None:
        df = df.fillna(fillna_value)
    fig = go.Figure()
    x_name = df.columns.name
    y_name = df.index.name
    hovertemplate = (
        "<b>" + y_name + "</b>: %{y}<br>"
        "<b>" + x_name + "</b>: %{x}<br>"
        "<b>Winrate</b>: %{z:.2%}<br>"
    )
    if counts is not None:
        hovertemplate += "<b>Games Played</b>: %{customdata:,}<br>"
    hovertemplate += "<extra></extra>"
    fig.add_trace(
        go.Heatmap(
            z=df.values,
            x=df.columns.tolist(),
            y=df.index.tolist(),
            colorscale=color,
            colorbar_tickformat=".0%",
            zmin=0.0,
            zmax=1.0,
            hovertemplate=hovertemplate,
            customdata=counts.values if counts is not None else None,
            text=counts.values if counts is not None else None,
            texttemplate="%{text:,}",
        )
    )
    fig.update_layout(
        title_text="<i><b>Winrate</b></i>",
        plot_bgcolor="white",
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        margin=dict(t=50, l=200),
    )
    fig.add_annotation(
        dict(
            font=dict(color="black", size=14),
            x=0.5,
            y=-0.15,
            showarrow=False,
            text=x_name,
            xref="paper",
            yref="paper",
        )
    )
    fig.add_annotation(
        dict(
            font=dict(color="black", size=14),
            x=-0.3,
            y=0.5,
            showarrow=False,
            text=y_name,
            textangle=-90,
            xref="paper",
            yref="paper",
        )
    )
    return fig
