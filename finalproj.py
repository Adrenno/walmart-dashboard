from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

# ---------------------------
# GLOBAL FONT (Roboto)
# ---------------------------
FONT_FAMILY = "Roboto, Segoe UI, Arial, sans-serif"

# Plotly defaults
px.defaults.template = "plotly_white"
px.defaults.color_continuous_scale = "Blues"

# ---------------------------
# Load Excel once
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "Walmart_LA_Final_Dataset.xlsx")

df_StoreProductFact = pd.read_excel(DATA_PATH, sheet_name="StoreProductFact")
df_Products = pd.read_excel(DATA_PATH, sheet_name="Products")
df_Inventory = pd.read_excel(DATA_PATH, sheet_name="Inventory")
df_TimeSeries = pd.read_excel(DATA_PATH, sheet_name="TimeSeries")
df_WarehouseProductFact = pd.read_excel(DATA_PATH, sheet_name="WarehouseProductFact")

# merge for Category
df_TimeSeries = df_TimeSeries.merge(
    df_Products[["ProductID", "ProductName", "Category"]],
    on="ProductID",
    how="left"
)

app = Dash(__name__)  # assets folder auto-loaded
server = app.server

# ---------------------------
# KPI Calculations
# ---------------------------
total_revenue = df_StoreProductFact["Revenue"].sum()
avg_turnover = df_TimeSeries["MonthlyTurnoverRate"].mean()

kpi_revenue = f"Revenue: ${total_revenue:,.0f}"
kpi_space = "Warehouse Space Allocated: 100%"
kpi_turnover = f"Avg Inventory Turnover: {avg_turnover:.2f}"

# ---------------------------
# Global Styles
# ---------------------------
PAGE_STYLE = {
    "backgroundColor": "#F3F6FA",
    "fontFamily": FONT_FAMILY,     # ✅ Roboto here
    "padding": "18px 22px"
}

CARD_STYLE = {
    "backgroundColor": "#568EEF",
    "borderRadius": "14px",
    "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
    "padding": "14px 16px",
    "marginBottom": "14px"
}

CHART_HEADER_STYLE = {
    "backgroundColor": "#0053E2",  # Walmart blue
    "color": "white",
    "fontFamily": FONT_FAMILY,     # ✅ Roboto here
    "fontWeight": "800",
    "fontSize": "16px",
    "padding": "8px 14px",
    "borderRadius": "12px 12px 0 0",
    "letterSpacing": "0.4px",
    "textAlign": "center",
    "width": "96%"
}

CHART_BODY_STYLE = {
    "backgroundColor": "white",
    "padding": "12px 14px",
    "borderRadius": "0 0 12px 12px",
    "boxShadow": "0 6px 18px rgba(0,0,0,0.08)"
}

# ---------------------------
# Helper: apply Roboto to all Plotly figures
# ---------------------------
def apply_roboto_font(fig):
    fig.update_layout(
        font=dict(
            family=FONT_FAMILY,
            size=12,
            color="#111111"
        ),
        title=dict(
            font=dict(
                family=FONT_FAMILY,
                size=14,
                color="#111111"
            )
        ),
        legend=dict(
            font=dict(
                family=FONT_FAMILY,
                size=12
            )
        )
    )

    fig.update_xaxes(
        title_font=dict(family=FONT_FAMILY, size=12),
        tickfont=dict(family=FONT_FAMILY, size=11)
    )

    fig.update_yaxes(
        title_font=dict(family=FONT_FAMILY, size=12),
        tickfont=dict(family=FONT_FAMILY, size=11)
    )

    return fig


# ---------------------------
# Layout
# ---------------------------
app.layout = html.Div([

    # ===== DASHBOARD TITLE (with logo left) =====
    html.Div(
        [
            # LOGO (left)
            html.Img(
                src="/assets/walmart_logo.png",
                style={
                    "height": "42px",
                    "position": "absolute",
                    "left": "24px",
                    "top": "50%",
                    "transform": "translateY(-50%)"
                }
            ),

            # TITLE (center)
            html.Div(
                "Walmart LA Inventory & Sales Performance Dashboard",
                style={
                    "fontFamily": FONT_FAMILY,   # ✅ Roboto here
                    "fontSize": "28px",
                    "fontWeight": "800",
                    "color": "white",
                    "textAlign": "center"
                }
            )
        ],
        style={
            "backgroundColor": "#0053E2",
            "position": "relative",
            "padding": "18px 0",
            "marginBottom": "18px",
            "borderRadius": "10px"
        }
    ),

    # ===== TOP KPIs =====
    html.Div([

        # KPI 1: Revenue (only number red)
        html.Div([
            html.Div([
                html.Span("Revenue: ", style={"fontSize": "22px", "fontWeight": "700", "color": "#000000"}),
                html.Span(f"${total_revenue:,.0f}", style={"fontSize": "22px", "fontWeight": "800", "color": "#D9534F"})
            ], style={"textAlign": "center"}),
            html.Div("Total revenue (12 months)", style={"fontSize": "12px", "opacity": "0.7", "textAlign": "center"})
        ], style={
            "backgroundColor": "white",
            "padding": "14px 18px",
            "borderRadius": "12px",
            "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
            "width": "30%"
        }),

        # KPI 2: Warehouse Space (only number red)
        html.Div([
            html.Div([
                html.Span("Warehouse Space Allocated: ", style={"fontSize": "22px", "fontWeight": "700", "color": "#000000"}),
                html.Span("100%", style={"fontSize": "22px", "fontWeight": "800", "color": "#D9534F"})
            ], style={"textAlign": "center"}),
            html.Div("Warehouse allocation", style={"fontSize": "12px", "opacity": "0.7", "textAlign": "center"})
        ], style={
            "backgroundColor": "white",
            "padding": "14px 18px",
            "borderRadius": "12px",
            "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
            "width": "30%"
        }),

        # KPI 3: Avg Turnover (only number red)
        html.Div([
            html.Div([
                html.Span("Avg Inventory Turnover: ", style={"fontSize": "22px", "fontWeight": "700", "color": "#000000"}),
                html.Span(f"{avg_turnover:.2f}", style={"fontSize": "22px", "fontWeight": "800", "color": "#D9534F"})
            ], style={"textAlign": "center"}),
            html.Div("Avg monthly turnover rate", style={"fontSize": "12px", "opacity": "0.7", "textAlign": "center"})
        ], style={
            "backgroundColor": "white",
            "padding": "14px 18px",
            "borderRadius": "12px",
            "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
            "width": "30%"
        }),

    ], style={
        "display": "flex",
        "justifyContent": "space-between",
        "gap": "12px",
        "padding": "14px 18px",
        "backgroundColor": "#F3F6FA",
        "marginBottom": "12px"
    }),

    # ===== ROW 1 =====
    html.Div([

        # Space Bar Chart
        html.Div([
            html.Div("Warehouse Space Occupied by Product", style=CHART_HEADER_STYLE),
            html.Div([
                dcc.Dropdown(
                    id="space-y-selector",
                    options=[
                        {"label": "Product Name", "value": "ProductName"},
                        {"label": "Category", "value": "Category"},
                    ],
                    value="ProductName",
                    clearable=False
                ),
                dcc.Graph(id="space-bar", style={"height": "420px"})
            ], style=CHART_BODY_STYLE)
        ], style={"width": "48%"}),

        # Line Chart
        html.Div([
            html.Div("Inventory Turnover Trend (Monthly by Category)", style=CHART_HEADER_STYLE),
            html.Div([
                dcc.Graph(id="line-chart", style={"height": "420px"})
            ], style=CHART_BODY_STYLE)
        ], style={"width": "48%"}),

    ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "12px"}),

    # ===== ROW 2 =====
    html.Div([

        # Revenue Bar Chart
        html.Div([
            html.Div("Revenue Contribution by Product", style=CHART_HEADER_STYLE),
            html.Div([
                dcc.Dropdown(
                    id="revenue-x-selector",
                    options=[
                        {"label": "Product Name", "value": "ProductName"},
                        {"label": "Category", "value": "Category"},
                    ],
                    value="ProductName",
                    clearable=False
                ),
                dcc.Graph(id="revenue-bar", style={"height": "420px"})
            ], style=CHART_BODY_STYLE)
        ], style={"width": "48%"}),

        # Heatmap
        html.Div([
            html.Div("Store × Product Sales Heatmap (Top 5 Products)", style=CHART_HEADER_STYLE),
            html.Div([
                dcc.Graph(id="heatmap", style={"height": "420px"})
            ], style=CHART_BODY_STYLE)
        ], style={"width": "48%"}),

    ], style={"display": "flex", "justifyContent": "space-between"}),

], style=PAGE_STYLE)


# ---------------------------
# CALLBACK: Space Bar Chart
# ---------------------------
@app.callback(
    Output("space-bar", "figure"),
    Input("space-y-selector", "value")
)
def update_space_bar(y_metric):

    if y_metric == "ProductName":
        met = "Product Name"
        df_grouped = df_WarehouseProductFact.groupby("ProductName", as_index=False)["WarehouseSpaceOccupied"].sum()
    else:
        met = "Category"
        df_grouped = df_WarehouseProductFact.groupby("Category", as_index=False)["WarehouseSpaceOccupied"].sum()

    fig = px.bar(
        df_grouped,
        y=y_metric,
        x="WarehouseSpaceOccupied",
        color="WarehouseSpaceOccupied",
        color_continuous_scale="Blues",
        title="Space Occupied per " + met,
        text="WarehouseSpaceOccupied",
    )
    fig.update_traces(
        texttemplate='%{text:.3f}',  # ← limit to 2 decimals
        textposition='outside',
        cliponaxis=False
    )
    fig.update_yaxes(title_text="Product Name")
    fig.update_xaxes(title_text="Warehouse Space Occupied")
    fig.update_coloraxes(colorbar_title="Warehouse Space Occupied")


    fig.update_layout(margin=dict(l=60, r=20, t=40, b=80))
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_layout(plot_bgcolor="#8FB3F2")
    fig.update_layout(paper_bgcolor="#DAE5F9")

    avg_space = df_grouped["WarehouseSpaceOccupied"].mean()
    fig.add_vline(x=avg_space, line_color="red", line_width=2)
    fig.add_vrect(x0=0.05, x1=0.12, fillcolor="red", opacity=0.08, line_width=0)

    fig = apply_roboto_font(fig)   # ✅ APPLY ROBOTO
    return fig


# ---------------------------
# CALLBACK: Line Plot
# ---------------------------
@app.callback(
    Output("line-chart", "figure"),
    Input("space-y-selector", "value")  # dùng để trigger load
)
def update_line(_):
    df_line = (
        df_TimeSeries
        .groupby(["Month", "Category"], as_index=False)["MonthlyTurnoverRate"]
        .mean()
    )

    fig = px.line(
        df_line,
        x="Month",
        y="MonthlyTurnoverRate",
        color="Category"
    )

    fig.update_layout(margin=dict(l=60, r=20, t=40, b=60))
    fig.update_layout(plot_bgcolor="#C3D3EE")
    fig.update_layout(paper_bgcolor="#DAE5F9")

    fig = apply_roboto_font(fig)   # ✅ APPLY ROBOTO
    return fig


# ---------------------------
# CALLBACK: Revenue Bar Chart
# ---------------------------
@app.callback(
    Output("revenue-bar", "figure"),
    Input("revenue-x-selector", "value")
)
def update_revenue_bar(x_metric):

    if x_metric == "ProductName":
        met = "Product Name"
        df_grouped = df_StoreProductFact.groupby("ProductName", as_index=False)["Revenue"].sum()
    else:
        met = "Category"
        df_grouped = df_StoreProductFact.groupby("Category", as_index=False)["Revenue"].sum()

    fig = px.bar(
        df_grouped,
        x=x_metric,
        y="Revenue",
        color="Revenue",
        color_continuous_scale="Blues",
        title=f"Revenue per {met}",
        text="Revenue",
    )
    fig.update_traces(
        texttemplate='%{text:.2s}',
        textposition='outside',
        cliponaxis=False
    )
    fig.update_xaxes(title_text="Product Name")
    fig.update_yaxes(title_text="Total Revenue ($)")
    fig.update_layout(plot_bgcolor="#8FB3F2")
    fig.update_layout(paper_bgcolor="#DAE5F9")

    fig.update_layout(margin=dict(l=60, r=20, t=40, b=80))
    fig.update_layout(yaxis_title='Total Revenue ($)', xaxis={'categoryorder': 'total ascending'})
    

    fig = apply_roboto_font(fig)   # ✅ APPLY ROBOTO
    return fig


# ---------------------------
# CALLBACK: Heatmap
# ---------------------------
@app.callback(
    Output("heatmap", "figure"),
    Input("space-y-selector", "value")
)
def update_heatmap(_):

    top5_products = (
        df_StoreProductFact.groupby("ProductName", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
        .head(5)["ProductName"]
        .tolist()
    )

    df_top5 = df_StoreProductFact[df_StoreProductFact["ProductName"].isin(top5_products)]

    heat_table = df_top5.pivot_table(
        index="StoreID",
        columns="ProductName",
        values="UnitsSold",
        aggfunc="sum"
    )

    fig = px.imshow(
        heat_table,
        labels=dict(x=" ", y="Store", color="Units Sold"),
        aspect="auto"
    )

    fig.update_layout(
        title=None,
        margin=dict(l=60, r=20, t=20, b=60)
    )
    fig.update_xaxes(side="top", automargin=True)
    fig.update_yaxes(automargin=True)
    fig.update_layout(paper_bgcolor="#DAE5F9")

    fig = apply_roboto_font(fig)   # ✅ APPLY ROBOTO
    return fig


# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=False)
