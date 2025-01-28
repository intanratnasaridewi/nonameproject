import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go




def format_number(value):
        """Format the value to a more readable string (e.g., 1000 -> 1K, 1000000 -> 1M)."""
        if value >= 1_000_000_000:  
            return f"{value / 1_00_000_000}B" if formatted_value.is_integer() else f"{formatted_value:.1f}B"
        elif value >= 1_000_000:
            formatted_value = value / 1_000_000
            return f"{int(formatted_value)}M" if formatted_value.is_integer() else f"{formatted_value:.1f}M"
        elif value >= 1_000:
            formatted_value = value / 1_000
            return f"{int(formatted_value)}K" if formatted_value.is_integer() else f"{formatted_value:.1f}K"
        else:
            return str(value)
        
class DashboardCardNoDelta:
    def __init__(self, title_1, title_2, total, description, status_color):
        self.title_1 = title_1
        self.title_2 = title_2
        self.total = total
        self.description = description
        self.status_color = status_color

    def render(self):
        st.markdown("""
            <style>
            .dashboard-card {
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                border-radius: 15px;
                background: linear-gradient(145deg, #f3f4f6, #ffffff);
                box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.1);
                height: 180px;
                transition: transform 0.3s ease-in-out;
            }
            .dashboard-card:hover {
                transform: scale(1.05);
            }
            .dashboard-card .title-1 {
                font-size: 20px;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
            }
            .dashboard-card .title-2 {
                font-size: 14px;
                color: #555555;
                text-align: center;
            }
            .dashboard-card .total {
                font-size: 36px;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
            }
            .dashboard-card .description {
                font-size: 12px;
                color: #333333;
                text-align: center;
            }
            dashboard-card .description.red {
                background-color: #FF5722;
            }
            .dashboard-card .description.green {
                color: #4CAF50;
            }
            </style>
        """, unsafe_allow_html=True)
     

        # Render the card content
        st.markdown(
            f"""
            <div class="dashboard-card">
                <div class="title-1">{self.title_1}</div>
                <div class="title-2">{self.title_2}</div>
                <div class="total">{self.total}</div>
                <div class="description {self.status_color}">{self.description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
class ChatCard:
    def __init__(self,  link):
        self.link = link

    def render(self):
        # HTML dan CSS untuk logo saja
        st.markdown(
            """
            <style>
            .container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 50px;
            }
            .text {
                font-size: 18px;
                margin-right: 15px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
            }
            .logo {
                width: 50px;
                height: 50px;
                border-radius: 50%;
                background-color: #ffffff;
                padding: 5px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                cursor: pointer;
                transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            }
            .logo:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
            }
            </style>
            <div class="container">
                <div class="text">Membutuhkan bantuan? Klik Asisten Warehouse</div>
                <a href={self.link} target="_blank">
                    <img class="logo" src="https://upload.wikimedia.org/wikipedia/commons/8/85/Circle-icons-chat.svg" alt="Chat Logo">
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

class DashboardCard:
    def __init__(self, title_1, title_2, total, delta, delta_status="neutral"):
        self.title_1 = title_1
        self.title_2 = title_2
        self.total = total
        self.delta = delta
        self.delta_status = delta_status

    def render(self):
        # Apply custom styles with updated padding, margin, and colors
        st.markdown("""
            <style>

            .dashboard-card {
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
                padding: 15px;
                border-radius: 15px;
                background: linear-gradient(145deg, #f3f4f6, #ffffff);
                box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.1);
                height: 180px;
                margin-top:0px;
                margin-bottom:15px;
                transition: transform 0.3s ease-in-out;
            }
            .dashboard-card:hover {
                transform: scale(1.05);
            }
            .dashboard-card .title-1 {
                font-size: 20px;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
            }
            .dashboard-card .title-2 {
                font-size: 18px;
                color: #555555;
                text-align: center;
            }
            .dashboard-card .total {
                font-size: 36px;
                font-weight: bold;
                color: #1E3A8A;
                text-align: center;
            }

            .dashboard-card .delta {
                font-size: 14px;
                color: #333333;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-top: 3px;
            }
            .dashboard-card .delta.up {
                color: #4CAF50;  /* Green for increase */
            }
            .dashboard-card .delta.down {
                color: #FF5722;  /* Red for decrease */
            }
            .dashboard-card .delta .arrow {
                font-size: 8px;
                margin-right: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Delta status (arrow icons)
        delta_arrow = ""
        if self.delta_status == "up":
            delta_arrow = "▲"
        elif self.delta_status == "down":
            delta_arrow = "▼"

        # Render HTML card with updated design
        st.markdown(f"""
        <div class="dashboard-card">
            <div class="title-1">{self.title_1}</div>
            <div class="title-2">{self.title_2}</div>
            <div class="total">{self.total}</div>
            <div class="delta {self.delta_status}">
                <span class="arrow">{delta_arrow}</span>
                {self.delta}
            </div>
        </div>
        """, unsafe_allow_html=True)
      
class BarChart:
    def __init__(self, data, x_column, y_column, custom_labels=None, title=None, height=None):
        self.data = data
        self.x_column = x_column
        self.y_column = y_column
        self.title = title
        self.height=height
        self.labels = custom_labels if custom_labels else {x_column: x_column, y_column: y_column}

    def render(self):
        if self.data.empty:
            # Handle empty data
            fig = px.bar(
                pd.DataFrame({self.x_column: ["No Data"], self.y_column: [0]}),
                x=self.x_column,
                y=self.y_column,
                labels=self.labels,
                title=self.title,
                color_discrete_sequence=["#d3d3d3"], 
            )
        else:
            fig = px.bar(
                self.data,
                x=self.x_column,
                y=self.y_column,
                labels=self.labels,
                title=self.title,
                color=self.x_column,
                color_discrete_sequence=px.colors.sequential.Viridis,
            )
        fig.update_layout(
        legend=dict(
            orientation="h",  
            x=0.5,            
            y=-0.7,           
            xanchor="center", 
            yanchor="top",    
        ),
        title=dict(
        text=self.title,
        x=0.5,
        xanchor="center",
        font=dict(size=16, color="black", family="Arial"),
        ),
        margin=dict(t=20, b=70, l=20, r=20),  # Adjust margins
        height=self.height,  # Adjust chart height if necessary
        width=350,   # Adjust chart width if necessary
    )

        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

class HorizontalBarChart:
    def __init__(self, data, x_column, y_column, custom_labels=None, title=None, color=None, height=None):
        self.data = data
        self.x_column = x_column
        self.y_column = y_column
        self.height=height
        self.title = title
        self.color=color
        self.labels = custom_labels if custom_labels else {x_column: x_column, y_column: y_column}

    def render(self):
        if self.data.empty:
            # Handle empty data
            fig = px.bar(
                pd.DataFrame({self.y_column: ["No Data"], self.x_column: [0]}),
                x=self.x_column,
                y=self.y_column,
                labels=self.labels,
                title=self.title,
                orientation='h',  # Horizontal orientation
                color_discrete_sequence=["#d3d3d3"],  # Gray color for no data
            )
        else:
            fig = px.bar(
                self.data,
                x=self.x_column,
                y=self.y_column,
                labels=self.labels,
                title=self.title,
                orientation='h',  # Horizontal orientation
                color=self.color,
                color_discrete_sequence=px.colors.sequential.Viridis,
                
   )

        fig.update_layout(
            # legend=dict(
            #     orientation="h",  # Horizontal legend
            #     x=0.2,
            #     y=-0.2,
            #     xanchor="center",
            #     yanchor="top",
            # ),
            title=dict(
                text=self.title,
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="black", family="Arial"),
            ),
            margin=dict(t=20, b=70, l=20, r=20),  # Adjust margins
            height=self.height,  # Adjust chart height if necessary
            width=350,   # Adjust chart width if necessary
        )

        
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)


class DonutChart:
    def __init__(self, labels, values, title=None, colors=None, total=None, text=None):
        self.labels = labels
        self.values = values
        self.total = total
        self.title = title
        self.text = text
        self.colors = colors if colors else ["#4285F4", "#EA4335"]  # Default colors
    def render(self):
        # Filter out categories with zero values
        filtered_labels = [label for label, value in zip(self.labels, self.values) if value > 0]
        filtered_values = [value for value in self.values if value > 0]

        # Handle empty chart
        if not filtered_values:
            filtered_labels = ["No Data"]
            filtered_values = [1]  
            self.colors = ["#d3d3d3"]  

        # Create the donut chart
        fig = go.Figure(data=[go.Pie(
            labels=filtered_labels,
            values=filtered_values,  # Use the numeric values for the chart
            hole=0.6,
            marker=dict(colors=px.colors.sequential.Plasma),
            textinfo="percent" if len(filtered_values) > 1 else "none",
            textfont=dict(size=10),
            pull=[0.05 if v > 0 else 0 for v in filtered_values],
        )])

        # Format the values for the category description
        category_description =  ", ".join([f"{label}: {value}" for label, value in zip(filtered_labels, filtered_values)])
     

        # Update the layout with total and category description
        fig.update_layout(
            annotations=[
                dict(
                    text=f'Total {self.text}<br><b>{self.total}</b>',
                    x=0.5, y=0.5,
                    font=dict(size=12),
                    showarrow=False,
                ),
                dict(
                    text=f"<b>Categories:</b> {category_description}",
                    x=0.5, y=-0.15,  
                    font=dict(size=12),
                    showarrow=False,
                    xref="paper", yref="paper"
                ),
            ],
            showlegend=True,
            legend=dict(orientation="h", x=0.1, y=-0.2),
            margin=dict(t=20, b=40, l=20, r=20),
            height=250,
            width=300,
            title=dict(text=self.title, x=0.5, xanchor="center", font=dict(size=16)),
        )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

class LineChart:
    def __init__(self, data, x_column, y_column, category_column, custom_labels=None, title=None, height=None):
        self.data = data
        self.x_column = x_column
        self.y_column = y_column
        self.category_column = category_column
        self.title = title
        self.height=height
        self.labels = custom_labels if custom_labels else {x_column: x_column, y_column: y_column}


    def render(self):
        fig = go.Figure()

        # Iterate through each category in the category column and create a line for each
      # Iterate through each category in the category column and create a line for each
        categories = self.data[self.category_column].unique()
        
        for category in categories:
            category_data = self.data[self.data[self.category_column] == category]

            # Format y values for consistent display
            category_data[self.y_column] = category_data[self.y_column]

            
            fig.add_trace(go.Scatter(
                x=category_data[self.x_column],
                y=category_data[self.y_column],
                mode='lines+markers',  # Adding markers to each line
                name=category,  # The category name will appear in the legend
                line=dict(width=2),
                marker=dict(size=8),  # Customize the markers
            ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=self.title,
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="black", family="Arial"),
            ),
            margin=dict(t=20, b=70, l=20, r=20),
            height=self.height,
            width=450,
        )

        # Display in Streamlit
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
class PieChart:
    def __init__(self, labels, values, title=None, colors=None):
        self.labels = labels
        self.values = values
        self.title = title
        self.colors = colors if colors else ["#4285F4", "#EA4335"]  # Default colors


    def render(self):
        # Filter out categories with zero values
        filtered_labels = [label for label, value in zip(self.labels, self.values) if value > 0]
        filtered_values = [value for value in self.values if value > 0]

        # Handle empty chart
        if not filtered_values:
            filtered_labels = ["No Data"]
            filtered_values = [1]  # Placeholder for empty chart
            self.colors = ["#d3d3d3"]  # Gray color for empty data

        fig = go.Figure(data=[go.Pie(
            labels=filtered_labels,
            values=filtered_values,
            marker=dict(colors=px.colors.sequential.Plasma),
            textinfo="percent" if len(filtered_values) > 1 else "none",
            textfont=dict(size=10),
            pull=[0.05 if v > 0 else 0 for v in filtered_values],  # Pull only non-zero values
        )])

        # Add total annotation in the center
        category_description = ", ".join([f"{label}: {format_number(value)}" for label, value in zip(filtered_labels, filtered_values)])
     

        fig.update_layout(
            annotations=[ 

        dict(
            text=f"<b>Categories:</b> {category_description}",
            x=0.5, y=-0.15,  # Position the text above the legend
            font=dict(size=12),
            showarrow=False,
            xref="paper", yref="paper"
        ),],
            showlegend=True,
            legend=dict(orientation="h", x=0.1, y=-0.2),
            margin=dict(t=20, b=40, l=20, r=20),
            height=250,
            width=300,
            title=dict(text=self.title, x=0.5,xanchor="center", font=dict(size=16)),
        )
        st.plotly_chart(fig, use_container_width=True)
class GanttChart:
    def __init__(self, data, task_column, start_column, end_column, resource_column=None, title=None):
        self.data = data
        self.task_column = task_column
        self.start_column = start_column
        self.end_column = end_column
        self.resource_column = resource_column
        self.title = title

    def render(self):
        if self.data.empty:
            st.warning("The data for the Gantt chart is empty. Please provide valid data.")
            return

        fig = px.timeline(
            self.data,
            x_start=self.start_column,
            x_end=self.end_column,
            y=self.task_column,
            color=self.resource_column if self.resource_column else None,
            title=self.title,
            labels={
                self.task_column: "Task",
                self.start_column: "Start Date",
                self.end_column: "End Date",
            },
            color_discrete_sequence=px.colors.sequential.Plasma,
        )

        fig.update_layout(
            title=dict(
                text=self.title,
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="black", family="Arial"),
            ),
            xaxis_title="Timeline",
            yaxis_title="Tasks",
            margin=dict(t=20, b=40, l=40, r=40),
            height=250,  # Adjust chart height if necessary
        )

        fig.update_yaxes(autorange="reversed")  # Reverse the y-axis for Gantt-style visualization

        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

class FunnelChart:
    def __init__(self, data, x_column, y_column, custom_labels=None, title=None):
        self.data = data
        self.x_column = x_column
        self.y_column = y_column
        self.title = title
        self.labels = custom_labels if custom_labels else {x_column: x_column, y_column: y_column}

    def render(self):
        if self.data.empty:
            # Handle empty data
            funnel_data = pd.DataFrame({self.x_column: ["No Data"], self.y_column: [0]})
        else:
            funnel_data = self.data
            #funnel_data = self.data.sort_values(by=self.y_column, ascending=False)

        fig = go.Figure(
            go.Funnel(
                x=funnel_data[self.y_column],
                y=funnel_data[self.x_column]
            )
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text=self.title or "Funnel Chart",
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="black", family="Arial"),
            ),
            margin=dict(t=20, b=50, l=20, r=20),  # Adjust margins
            height=300,  # Adjust chart height
        )

        # Display the chart in Streamlit
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

class HorizontalBarChartWithLine:
    def __init__(self, data, x_bar, y_bar, x_line, y_line, bar_label=None, line_label=None, title=None):
        self.data = data
        self.x_bar = x_bar
        self.y_bar = y_bar
        self.x_line = x_line
        self.y_line = y_line
        self.bar_label = bar_label if bar_label else "Bar Data"
        self.line_label = line_label if line_label else "Line Data"
        self.title = title

    def render(self):
        if self.data.empty:
            # Handle empty data
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=[0],
                    y=["No Data"],
                    name=self.bar_label,
                    orientation="h",
                    marker=dict(color="#d3d3d3"),
                )
            )
        else:
            # Create bar trace
            bar_trace = go.Bar(
                x=self.data[self.x_bar],
                y=self.data[self.y_bar],
                name=self.bar_label,
                orientation="h",
                marker=dict(color=px.colors.sequential.Plasma),
            )

            # Create line trace
            line_trace = go.Scatter(
                x=self.data[self.x_line],
                y=self.data[self.y_line],
                mode="lines+markers",
                name=self.line_label,
                line=dict(color="lightsteelblue"),
            )

            # Combine traces
            fig = go.Figure(data=[bar_trace, line_trace])

        # Update layout
        fig.update_layout(
            title=dict(
                text=self.title,
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="black", family="Arial"),
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                y=-0.2,
                xanchor="center",
                yanchor="top",
            ),
            margin=dict(t=20, b=70, l=20, r=20),
            height=250,
            width=600,
        )

        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

class DonutChart2:
    def __init__(self, labels, values, title=None, colors=None, total=None, text=None):
        self.labels = labels
        self.values = values
        self.total = total
        self.title = title
        self.text = text
        self.colors = colors if colors else ["#4285F4", "#EA4335"]  # Default colors

    def render(self):
        # Filter out categories with zero values
        filtered_labels = [label for label, value in zip(self.labels, self.values) if value > 0]
        filtered_values = [value for value in self.values if value > 0]

        # Handle empty chart
        if not filtered_values:
            filtered_labels = ["No Data"]
            filtered_values = [1]  
            self.colors = ["#d3d3d3"]  

        fig = go.Figure(data=[go.Pie(
            labels=filtered_labels,
            values=filtered_values,
            hole=0.6,  # Adjusted hole size to make the donut bigger
            marker=dict(colors=px.colors.sequential.Plasma),  # Use the specified colors
            textinfo="percent" if len(filtered_values) > 1 else "none",
            textfont=dict(size=10),
            pull=[0.05 if v > 0 else 0 for v in filtered_values],  # Pull only non-zero values
        )])

        # Add total annotation in the center
        category_description = ", ".join([f"{label}: {format_number(value)}" for label, value in zip(filtered_labels, filtered_values)])
        total = sum(self.values)

        fig.update_layout(
            annotations=[
                dict(
                    text=f'Total {self.text}<br><b>{self.total}</b>',
                    x=0.5, y=0.5,
                    font=dict(size=12),
                    showarrow=False,
                ),
                dict(
                    text=f"<b>Categories:</b><br>{category_description}",  # Teks kategori dengan <br> untuk pemisah baris
                    x=0.5, y=-0.15,  # Menempatkan teks di sebelah kanan dan sedikit lebih rendah
                    font=dict(size=12, color="darkblue"),
                    showarrow=False,
                    xref="paper", yref="paper",
                    xanchor="left", yanchor="bottom",
                    textangle=0  # Mengatur orientasi teks secara vertikal
                )
            ],
            showlegend=True,
            legend=dict(
                orientation="v",  # Vertikal
                x=1.05, y=0.9,      # Menempatkan legenda di kanan atas
                xanchor="left",   # Menjaga agar legend terikat ke kiri
                yanchor="top",    # Menjaga agar legend terikat ke atas
                traceorder='normal'
            ),
            margin=dict(t=20, b=40, l=20, r=20),
            height=250,  # Keep the overall height
            width=600,   # Keep the overall width
            title=dict(text=self.title, x=0.5, xanchor="center", font=dict(size=16)),
        )
        st.plotly_chart(fig, use_container_width=True)
class GenderBarChart:
    def __init__(self, data, x_column, y_column, custom_labels=None, title=None, height=None):
        self.data = data
        self.x_column = x_column
        self.y_column = y_column
        self.title = title
        self.height = height
        self.labels = custom_labels if custom_labels else {x_column: x_column, y_column: y_column}
    
    def render(self):
        # If no data exists, show a placeholder chart
        if self.data.empty:
            fig = px.bar(
                pd.DataFrame({self.x_column: ["No Data"], self.y_column: [0]}),
                x=self.x_column,
                y=self.y_column,
                labels=self.labels,
                title=self.title,
                color_discrete_sequence=["#d3d3d3"],
            )
        else:
            # Plot bar chart with gender-based colors (Laki-laki and Perempuan)
            fig = px.bar(
                self.data,
                x=self.x_column,
                y=self.y_column,
                color="jenis_kelamin",  # Group by gender
                labels=self.labels,
                title=self.title,
                barmode="group",  # Grouping bars for each department
                color_discrete_map={"Laki-laki": "blue", "Perempuan": "pink"},  # Color mapping for gender
                text=self.y_column,
            )

        # Update chart layout
        fig.update_layout(
            title=dict(
                text=self.title,
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="black", family="Arial"),
            ),
            margin=dict(t=20, b=70, l=20, r=20),  # Adjust margins
            height=self.height,  # Adjust chart height if necessary
            width=700,  # Adjust chart width if necessary
        )
        fig.update_traces(
            textposition="inside",  # Position text above the bars
            texttemplate="%{text:.0f}",  # Format text as integer (no decimals)
        )
        # Display the chart in Streamlit
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
class GenderAgeBarChart:
    def __init__(self, data, x_column, y_column, category_column, custom_labels=None, title=None, height=None):
        self.data = data
        self.x_column = x_column
        self.y_column = y_column
        self.category_column = category_column
        self.title = title
        self.height = height
        self.labels = custom_labels if custom_labels else {x_column: x_column, y_column: y_column, category_column: category_column}
    
    def render(self):
        # Plot bar chart dengan menggunakan binned usia dan gender
        fig = px.bar(
            self.data,
            x=self.x_column,
            y=self.y_column,
            color=self.category_column,  # Menentukan kategori berdasarkan jenis_kelamin
            labels=self.labels,
            title=self.title,
            barmode="group",  # Menampilkan bar secara berdampingan
            color_discrete_map={"Laki-laki": "blue", "Perempuan": "pink"},  # Pewarnaan berdasarkan jenis_kelamin
        )

        # Update layout untuk chart
        fig.update_layout(
            title=dict(
                text=self.title,
                x=0.5,
                xanchor="center",
                font=dict(size=16, color="black", family="Arial"),
            ),
            margin=dict(t=20, b=70, l=20, r=20),  # Adjust margins
            height=self.height,  # Adjust chart height if necessary
            width=700,  # Adjust chart width if necessary
        )

        # Menampilkan chart di Streamlit
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

