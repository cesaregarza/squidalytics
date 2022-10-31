import pandas as pd
import plotly.graph_objects as go


def generate_winrate_grid(df: pd.DataFrame) -> go.Figure:
    df = df.copy().fillna(0.5)
    fig = go.Figure()
    x_name = df.columns.name
    y_name = df.index.name
    hovertemplate = (
        "<b>" + y_name + "</b>: %{y}<br>"
        "<b>" + x_name + "</b>: %{x}<br>"
        "<b>Winrate</b>: %{z:.2%}<br>"
    )
    fig.add_trace(
        go.Heatmap(
            z=df.values,
            x=df.columns.tolist(),
            y=df.index.tolist(),
            colorscale="Viridis",
            hovertemplate=hovertemplate,
        )
    )
    fig.update_layout(
        title_text="<i><b>Winrate</b></i>",
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
