from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os

# ---------------------------
# GLOBAL FONT (Roboto)
# ---------------------------
FONT_FAMILY = "Roboto, Segoe UI, Arial, sans-serif"
CARD_LIGHT_BLUE = "#DAE5F9" 

# Plotly defaults
px.defaults.template = "plotly_white"
px.defaults.color_continuous_scale = "Blues"

# ---------------------------
# Load Excel once
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "Walmart_LA_Final_Dataset.xlsx")
print(DATA_PATH)
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
# --- Revenue: current year vs last year (with delta color) ---
df_rev = df_StoreProductFact.copy()

# Detect year from common columns
if "Year" in df_rev.columns:
    df_rev["__year"] = df_rev["Year"].astype(int)
elif "Month" in df_rev.columns:
    df_rev["Month"] = pd.to_datetime(df_rev["Month"])
    df_rev["__year"] = df_rev["Month"].dt.year
else:
    df_rev["__year"] = None

if df_rev["__year"].notna().any():
    current_year = int(df_rev["__year"].max())
    last_year = current_year - 1

    revenue_current = df_rev.loc[df_rev["__year"] == current_year, "Revenue"].sum()
    revenue_last = df_rev.loc[df_rev["__year"] == last_year, "Revenue"].sum()

    revenue_delta = revenue_current - revenue_last
    revenue_pct = (revenue_delta / revenue_last) if revenue_last != 0 else None
else:
    # fallback if no time column
    current_year = None
    last_year = None
    revenue_current = df_rev["Revenue"].sum()
    revenue_last = None
    revenue_delta = None
    revenue_pct = None

# Color for delta (green if up, red if down)
if revenue_delta is None:
    revenue_delta_color = "#6c757d"  # gray
else:
    revenue_delta_color = "#2E7D32" if revenue_delta >= 0 else "#D9534F"
# ---------------------------
# MANUAL last year revenue (because dataset has no year column)
# ---------------------------
last_year = 2024
revenue_last = 1_916_950  # $1,916,950

revenue_delta = revenue_current - revenue_last
revenue_pct = revenue_delta / revenue_last

# Re-assign color based on manual delta
revenue_delta_color = "#2E7D32" if revenue_delta >= 0 else "#D9534F"

# ---------------------------
# MANUAL last year avg inventory turnover
# ---------------------------
avg_turnover = df_TimeSeries["MonthlyTurnoverRate"].mean()
turnover_last_year = 2024
turnover_last = 1.47   # <-- số last year bạn muốn dùng

turnover_current = avg_turnover   # avg_turnover bạn đã tính trước đó
turnover_delta = turnover_current - turnover_last
turnover_pct = turnover_delta / turnover_last

# Color for turnover delta
turnover_delta_color = "#2E7D32" if turnover_delta >= 0 else "#D9534F"

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
    # KPI 1: Revenue
html.Div(
    [
        html.Div(
            [
                html.Span("Revenue: ", style={"fontSize": "22px", "fontWeight": "700", "color": "#000000"}),
                html.Span(f"${revenue_current:,.0f}", style={"fontSize": "22px", "fontWeight": "800", "color": "#D9534F"})
            ],
            style={"textAlign": "center"}
        ),
        html.Div("Total revenue (12 months)", style={"fontSize": "12px", "opacity": "0.7", "textAlign": "center"}),

        # Last year + delta
        (html.Div(
            [
                html.Span(
                    f"Last year ({last_year}): ${revenue_last:,.0f}  |  ",
                    style={"fontSize": "12px", "opacity": "0.75"}
                ),
                html.Span(
                    f"Δ {revenue_delta:,.0f}" + (f" ({revenue_pct:.1%})" if revenue_pct is not None else ""),
                    style={"fontSize": "12px", "fontWeight": "700", "color": revenue_delta_color}
                )
            ],
            style={"textAlign": "center"}
        ) if revenue_last is not None else html.Div(
            "Last year: N/A",
            style={"fontSize": "12px", "opacity": "0.75", "textAlign": "center"}
        ))
    ],
    style={
        "backgroundColor": "white",
        "padding": "14px 18px",
        "borderRadius": "12px",
        "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
        "width": "30%"
    }
),
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

        # KPI 3: Avg Inventory Turnover
html.Div(
    [
        html.Div(
            [
                html.Span(
                    "Avg Inventory Turnover: ",
                    style={"fontSize": "22px", "fontWeight": "700", "color": "#000000"}
                ),
                html.Span(
                    f"{turnover_current:.2f}",
                    style={"fontSize": "22px", "fontWeight": "800", "color": "#D9534F"}
                )
            ],
            style={"textAlign": "center"}
        ),

        html.Div(
            "Avg monthly turnover rate",
            style={"fontSize": "12px", "opacity": "0.7", "textAlign": "center"}
        ),

        html.Div(
            [
                html.Span(
                    f"Last year ({turnover_last_year}): {turnover_last:.2f}  |  ",
                    style={"fontSize": "12px", "opacity": "0.75"}
                ),
                html.Span(
                    f"Δ {turnover_delta:+.2f} ({turnover_pct:.1%})",
                    style={
                        "fontSize": "12px",
                        "fontWeight": "700",
                        "color": turnover_delta_color
                    }
                )
            ],
            style={"textAlign": "center"}
        )
    ],
    style={
        "backgroundColor": "white",
        "padding": "14px 18px",
        "borderRadius": "12px",
        "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
        "width": "30%"
    }
),    
], style={
        "display": "flex",
        "justifyContent": "space-between",
        "gap": "12px",
        "padding": "14px 18px",
        "backgroundColor": "#F3F6FA",
        "marginBottom": "12px"
    }),

    # ===== ROW 1 =====
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

    # Line Chart (2-level filter: category -> multi products)
    html.Div([
        html.Div("Inventory Turnover Trend", style=CHART_HEADER_STYLE),
        html.Div([
            # Dropdown 1: Category
            dcc.Dropdown(
                id="turnover-category",
                options=[{"label": c, "value": c} for c in sorted(df_Products["Category"].dropna().unique())],
                value=sorted(df_Products["Category"].dropna().unique())[0],
                clearable=False
            ),

            # Dropdown 2: Products (multi-select)
            dcc.Dropdown(
                id="turnover-products",
                options=[],
                value=[],
                multi=True,
                clearable=True,
                placeholder="Choose 1+ products (optional)"
            ),

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
    fig.update_yaxes(title_text=met, showgrid=False)
    fig.update_xaxes(title_text="Warehouse Space Occupied", showgrid=False)
    fig.update_coloraxes(colorbar_title="Warehouse Space Occupied")


    fig.update_layout(margin=dict(l=60, r=20, t=40, b=80))
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_layout(plot_bgcolor=CARD_LIGHT_BLUE)
    fig.update_layout(paper_bgcolor=CARD_LIGHT_BLUE)

    avg_space = df_grouped["WarehouseSpaceOccupied"].mean()
    fig.add_vline(x=avg_space, line_color="red", line_width=2)

    fig = apply_roboto_font(fig)   # ✅ APPLY ROBOTO
    return fig

@app.callback(
    Output("turnover-products", "options"),
    Output("turnover-products", "value"),
    Input("turnover-category", "value"),
)
def update_turnover_products(selected_category):
    products = (
        df_Products.loc[df_Products["Category"] == selected_category, "ProductName"]
        .dropna()
        .unique()
    )
    products = sorted(products)

    options = [{"label": p, "value": p} for p in products]

    # reset selection when category changes
    return options, []

# ---------------------------
# CALLBACK: Line Plot
# ---------------------------
@app.callback(
    Output("line-chart", "figure"),
    Input("turnover-category", "value"),
    Input("turnover-products", "value"),
)
def update_line(selected_category, selected_products):

    df_ts = df_TimeSeries.copy()

    # Case A: chọn nhiều product -> vẽ nhiều line theo ProductName
    if selected_products and len(selected_products) > 0:
        df_line = (
            df_ts[
                (df_ts["Category"] == selected_category) &
                (df_ts["ProductName"].isin(selected_products))
            ]
            .groupby(["Month", "ProductName"], as_index=False)["MonthlyTurnoverRate"]
            .mean()
        )

        fig = px.line(
            df_line,
            x="Month",
            y="MonthlyTurnoverRate",
            color="ProductName",
            title=f"Inventory Turnover Trend - Selected Products ({selected_category})",
            color_discrete_sequence=px.colors.qualitative.Alphabet
        )

    # Case B: chưa chọn product -> chỉ vẽ 1 line trung bình theo category
    else:
        df_line = (
            df_ts[df_ts["Category"] == selected_category]
            .groupby("Month", as_index=False)["MonthlyTurnoverRate"]
            .mean()
        )

        fig = px.line(
            df_line,
            x="Month",
            y="MonthlyTurnoverRate",
            title=f"Inventory Turnover Trend - Category Average ({selected_category})"
        )

    fig.update_layout(margin=dict(l=60, r=20, t=40, b=60))
    fig.update_yaxes(title_text="Monthly Turnover Rate")
    fig.update_layout(plot_bgcolor="#C3D3EE")
    fig.update_layout(paper_bgcolor="#DAE5F9")

    fig = apply_roboto_font(fig)
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
        aspect="auto"
    )

    fig.update_traces(
        hovertemplate=
            "Product=%{x}<br>"
            "Store=%{y}<br>" +
            "Units Sold=%{z}<extra></extra>"
    )

    fig.update_layout(
        title=None,
        margin=dict(l=60, r=20, t=20, b=60)
    )
    fig.update_xaxes(side="top", automargin=True, title_text="")
    fig.update_yaxes(automargin=True)
    fig.update_layout(paper_bgcolor="#DAE5F9")

    fig = apply_roboto_font(fig)   # ✅ APPLY ROBOTO
    return fig


# ---------------------------
# Run App
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
