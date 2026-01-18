from neo4j import GraphDatabase
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Connect to Neo4j (update password if needed)
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "K1g@li2025!"))

def get_data(query, params=None):
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]

# Task 5: Key Metrics (KPIs)
query_kpis = """
MATCH (i:Intersection)
WITH count(i) AS totalIntersections
MATCH ()-[r:ROAD]->()
RETURN totalIntersections, count(r) AS totalRoads;
"""
kpis = get_data(query_kpis)[0]
total_intersections = kpis["totalIntersections"]
total_roads = kpis["totalRoads"]

# Task 6: Degree Distribution Bar Chart
query_degree = """
MATCH (n:Intersection)
WITH n, COUNT{ (n)-[:ROAD]-() } AS degree
RETURN degree, count(n) AS Frequency
ORDER BY degree ASC
"""
df_degree = pd.DataFrame(get_data(query_degree))

fig_degree = px.bar(
    df_degree, x="degree", y="Frequency",
    title="Degree Distribution",
    labels={"degree": "Degree", "Frequency": "Intersections"},
    log_y=True  # Better for skewed distributions
)
fig_degree.update_traces(
    marker_color='#4A90E2',
    marker_line_color='#2E5C8A',
    marker_line_width=1,
    name="Degree Distribution",
    showlegend=True,
    hovertemplate='<b>Degree:</b> %{x}<br><b>Intersections:</b> %{y:,}<extra></extra>'
)
fig_degree.update_layout(
    font_size=12,
    xaxis_tickangle=-45,
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)'
)

# Task 7: Top 10 Most Connected
query_top10 = """
MATCH (n:Intersection)
WITH n, COUNT{ (n)-[:ROAD]-() } AS degree
RETURN toString(n.id) AS IntersectionID, degree
ORDER BY degree DESC
LIMIT 10
"""
df_top10 = pd.DataFrame(get_data(query_top10))

fig_top10 = px.bar(
    df_top10, x="IntersectionID", y="degree",
    title="Top 10 Most Connected Intersections",
    labels={"degree": "Degree", "IntersectionID": "Intersection ID"},
)
fig_top10.update_traces(
    marker_color='#E94B59',
    marker_line_color='#B83742',
    marker_line_width=1,
    name="Top 10 Intersections",
    showlegend=True,
    hovertemplate='<b>Intersection ID:</b> %{x}<br><b>Degree:</b> %{y}<extra></extra>'
)
fig_top10.update_layout(
    font_size=12,
    xaxis_tickangle=-45,
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)'
)

# Task 8: Categories by Degree (Pie)
query_cats = """
MATCH (n:Intersection)
WITH n, COUNT{ (n)-[:ROAD]-() } AS degree
WITH CASE
  WHEN degree <= 2 THEN 'Low Connectivity'
  WHEN degree <= 4 THEN 'Medium Connectivity'
  ELSE 'High Connectivity'
END AS Category
RETURN Category, count(*) AS Count
ORDER BY Count DESC
"""
df_cats = pd.DataFrame(get_data(query_cats))

fig_cats = px.pie(
    df_cats, values="Count", names="Category",
    title="Intersection Connectivity Categories",
    hole=0.4,  # Donut style for better visibility
    color_discrete_sequence=['#50C878', '#FFB347', '#FF6B6B']  # Green, Orange, Red
)
fig_cats.update_traces(
    textposition='inside',
    textinfo='percent+label',
    textfont_size=14,
    marker=dict(line=dict(color='#FFFFFF', width=2)),
    hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
)
fig_cats.update_layout(
    font_size=12,
    showlegend=True,
    legend=dict(
        orientation="v",
        yanchor="middle",
        y=0.5,
        xanchor="left",
        x=1.05
    )
)

# Prepare Key Metrics as bar chart data
metrics_data = {
    "Metric": ["Total Intersections", "Total Roads"],
    "Value": [total_intersections, total_roads]
}
df_metrics = pd.DataFrame(metrics_data)
max_value = max(total_intersections, total_roads)
y_max_with_padding = max_value * 1.2  # Add 20% padding at top for text labels

fig_metrics = px.bar(
    df_metrics, x="Metric", y="Value",
    title="Key Metrics",
    labels={"Value": "Count", "Metric": "Metric"},
    color="Metric",  # Add color mapping for legend
    color_discrete_sequence=['#4ECDC4', '#FFE66D']  # Teal and Yellow
)
fig_metrics.update_traces(
    marker_line_color='#2E7D7A',
    marker_line_width=1.5,
    texttemplate='<b>%{y:,}</b>',
    textposition='outside',
    textfont_size=11,  # Slightly smaller text
    hovertemplate='<b>%{x}</b><br>Count: %{y:,}<extra></extra>'
)
fig_metrics.update_layout(
    font_size=12,
    showlegend=True,
    plot_bgcolor='rgba(0,0,0,0)',
    yaxis=dict(tickformat=','),
    margin=dict(b=60, t=20)  # Add bottom margin for text
)

# Build dashboard with all graphs stacked on left side (4 rows, 2 cols - only using left column)
dashboard = make_subplots(
    rows=4, cols=2,
    specs=[
        [{"type": "xy"}, None],
        [{"type": "xy"}, None],
        [{"type": "xy"}, None],
        [{"type": "domain"}, None],
    ],
    subplot_titles=(
        "Key Metrics", "Degree Distribution",
        "Top 10 Connected Intersections", "Connectivity Categories"
    ),
    vertical_spacing=0.10,
    horizontal_spacing=0.08,
    column_widths=[0.65, 0.35],  # Left column wider, right empty
    row_heights=[0.20, 0.20, 0.20, 0.40]  # Make pie chart (row 4) bigger, bar charts smaller
)

# Add Key Metrics bar chart
for tr in fig_metrics.data:
    dashboard.add_trace(tr, row=1, col=1)

# Add charts on left side (stacked vertically)
for tr in fig_degree.data:
    dashboard.add_trace(tr, row=2, col=1)
for tr in fig_top10.data:
    dashboard.add_trace(tr, row=3, col=1)
for tr in fig_cats.data:
    dashboard.add_trace(tr, row=4, col=1)

# Global layout tweaks
dashboard.update_layout(
    title={
        'text': "US Road Network Dashboard<br><sub style='font-size:18px; color:#666;'>Neo4j Graph Analytics Visualization</sub>",
        'x': 0.5,  # Center the title
        'xanchor': 'center',
        'y': 0.98,
        'yanchor': 'top',
        'font': {'size': 38, 'family': 'Arial Black, sans-serif', 'color': '#1a1a1a'}  # Bold and bigger
    },
    height=1500,  # Taller for stacked graphs
    width=1700,  # Bigger width for larger graphs
    showlegend=True,  # Show legends for bar charts
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.98,
        xanchor="left",
        x=1.02,
        font=dict(size=11, color='#333'),
        bgcolor='rgba(255,255,255,0.8)',
        bordercolor='#ddd',
        borderwidth=1
    ),
    annotations=[dict(
        font_size=16,
        font=dict(weight='bold', size=16, color='#2c3e50'),
        bgcolor='rgba(255,255,255,0.7)',
        bordercolor='#ddd',
        borderwidth=1,
        borderpad=4
    ) for i in dashboard.layout.annotations],  # Bold and styled subtitles
    margin=dict(l=70, r=70, t=130, b=50),  # More space for title and margins
    paper_bgcolor="#f8f9fa",  # Light gray background
    plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot backgrounds
    autosize=True,  # Responsive
    hovermode='closest'
)

# Update individual graph sizes and formatting - make them more presentable
# Key Metrics (row 1)
dashboard.update_xaxes(
    row=1, col=1,
    title_text="Metric",
    title_font_size=14,
    title_font_color='#2c3e50',
    tickfont_size=12,
    tickfont_color='#555',
    showgrid=True,
    gridwidth=1,
    gridcolor='rgba(128,128,128,0.2)',
    showline=True,
    linewidth=2,
    linecolor='#4a5568',
    mirror=True,
    zeroline=False
)
dashboard.update_yaxes(
    row=1, col=1,
    title_text="Count",
    title_font_size=14,
    title_font_color='#2c3e50',
    tickfont_size=12,
    tickfont_color='#555',
    tickformat=',',
    showgrid=True,
    gridwidth=1,
    gridcolor='rgba(128,128,128,0.2)',
    showline=True,
    linewidth=2,
    linecolor='#4a5568',
    mirror=True,
    zeroline=True,
    zerolinecolor='#4a5568',
    zerolinewidth=1,
    range=[0, y_max_with_padding]  # Add padding at top for text labels
)

# Degree Distribution (row 2)
dashboard.update_xaxes(
    row=2, col=1,
    title_text="Degree",
    title_font_size=14,
    title_font_color='#2c3e50',
    tickfont_size=12,
    tickfont_color='#555',
    showgrid=True,
    gridwidth=1,
    gridcolor='rgba(128,128,128,0.2)',
    showline=True,
    linewidth=2,
    linecolor='#4a5568',
    mirror=True,
    zeroline=False
)
dashboard.update_yaxes(
    row=2, col=1,
    title_text="Number of Intersections",
    title_font_size=14,
    title_font_color='#2c3e50',
    tickfont_size=12,
    tickfont_color='#555',
    tickformat=',',
    showgrid=True,
    gridwidth=1,
    gridcolor='rgba(128,128,128,0.2)',
    showline=True,
    linewidth=2,
    linecolor='#4a5568',
    mirror=True,
    zeroline=True,
    zerolinecolor='#4a5568',
    zerolinewidth=1
)

# Top 10 Intersections (row 3)
dashboard.update_xaxes(
    row=3, col=1,
    title_text="Intersection ID",
    title_font_size=14,
    title_font_color='#2c3e50',
    tickfont_size=11,
    tickfont_color='#555',
    showgrid=True,
    gridwidth=1,
    gridcolor='rgba(128,128,128,0.2)',
    showline=True,
    linewidth=2,
    linecolor='#4a5568',
    mirror=True,
    zeroline=False
)
dashboard.update_yaxes(
    row=3, col=1,
    title_text="Degree",
    title_font_size=14,
    title_font_color='#2c3e50',
    tickfont_size=12,
    tickfont_color='#555',
    tickformat=',',
    showgrid=True,
    gridwidth=1,
    gridcolor='rgba(128,128,128,0.2)',
    showline=True,
    linewidth=2,
    linecolor='#4a5568',
    mirror=True,
    zeroline=True,
    zerolinecolor='#4a5568',
    zerolinewidth=1
)

# Save and open
output_file = "us_road_network_dashboard.html"
dashboard.write_html(output_file, auto_open=True, include_plotlyjs='cdn', full_html=True, config={'responsive': True})

driver.close()
print(f"Dashboard saved to {output_file}")