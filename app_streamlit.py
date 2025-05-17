import streamlit as st
import pandas as pd
import plotly.express as px
import random

st.set_page_config(page_title="Data Visualization Dashboard", layout="wide")

# Add developer info at the top
st.markdown("""
### [@dev Prabesh Rai](https://github.com/RaiPrabesh)
""")

# Add custom CSS to center all content and style the dataframe
st.markdown("""
<style>
    .stApp {
        padding: 1rem;
    }
    /* Center only the plotly chart container */
    .plot-container.plotly {
        display: flex;
        justify-content: center;
        margin: auto;
    }
    /* Style for distinct values dataframe */
    [data-testid="stDataFrame"] div[data-testid="stHorizontalBlock"] {
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

st.title("Data Visualization Dashboard")

# File upload
uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Display raw data with column configuration
        st.subheader("Raw Data Preview")
        # Get the first 10 columns if there are more than 10
        display_cols = df.columns[:10] if len(df.columns) > 10 else df.columns
        st.dataframe(df[display_cols], height=400, use_container_width=True)

        # Add a divider line
        st.markdown("<hr style='border: 2px solid #e6e6e6; border-radius: 5px; margin: 2rem 0;'>", unsafe_allow_html=True)

        # Dataset Information Section
        st.subheader("Dataset Information")
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Total Rows", df.shape[0])
        with metrics_col2:
            st.metric("Total Columns", df.shape[1])
        
        # Display number and actual distinct values for each column
        st.write("Distinct Values per Column:")
        distinct_values_df = pd.DataFrame({
            'Column Name': df.columns,
            'Count of Distinct Values': [df[col].nunique() for col in df.columns],
            'Distinct Values': [', '.join(map(str, df[col].unique())) for col in df.columns]
        })
        # Calculate column widths based on content
        max_col_name_len = max(len(str(col)) for col in df.columns)
        max_count_len = max(len(str(count)) for count in distinct_values_df['Count of Distinct Values'])
        
        column_config = {
            'Column Name': st.column_config.Column(width=max_col_name_len - 10), 
            'Count of Distinct Values': st.column_config.Column(width=len('Count of Distinct Values')),
            'Distinct Values': st.column_config.Column(width='auto')
        }
        st.dataframe(distinct_values_df, use_container_width=True, height=300, column_config=column_config)

        # Add a divider line
        st.markdown("<hr style='border: 2px solid #e6e6e6; border-radius: 5px; margin: 2rem 0;'>", unsafe_allow_html=True)

        # Column selection for visualization
        st.subheader("Create Visualization")
        all_cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        # Create controls for visualization in a single row
        col1, col2, col3, col4 = st.columns([1, 1.5, 1.5, 1])
        with col1:
            chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Clustered Bar Chart", "Scatter Plot", "Line Chart", "Histogram", "Stacked Histogram", "Side-by-side Histogram"])
        with col2:
            x_col = st.selectbox("Select X-axis Column", all_cols)
        with col3:
            if chart_type not in ["Histogram", "Stacked Histogram", "Side-by-side Histogram"]:
                # For Bar Charts and Clustered Bar Chart, exclude the selected x_col from y-axis options
                if chart_type in ["Bar Chart", "Clustered Bar Chart"]:
                    available_y_cols = [col for col in numeric_cols if col != x_col]
                else:
                    available_y_cols = numeric_cols
                y_col = st.selectbox("Select Y-axis Column", available_y_cols)
            elif chart_type in ["Stacked Histogram", "Side-by-side Histogram"]:
                color_col = st.selectbox("Select Category Column", [col for col in all_cols if col != x_col])
            else:
                color_col = None  # Initialize color_col for simple histogram
        with col4:
            if chart_type not in ["Histogram", "Stacked Histogram", "Side-by-side Histogram"]:
                agg_method = st.selectbox("Aggregation Method", ["None", "Average", "Total"])

        # Create another row for axis values selection
        if chart_type == "Clustered Bar Chart":
            # Add category column selection for Clustered Bar Chart
            col5, col6 = st.columns(2)
            with col5:
                category_col = st.selectbox("Select Category Column", [col for col in all_cols if col not in [x_col, y_col]])
            
            with col6:
                if pd.api.types.is_numeric_dtype(df[category_col]):
                    cat_min, cat_max = float(df[category_col].min()), float(df[category_col].max())
                    cat_range = st.slider(
                        f"Select {category_col} Range",
                        min_value=cat_min,
                        max_value=cat_max,
                        value=(cat_min, cat_max),
                        key=f"cat_range_{chart_type.lower().replace(' ', '_')}_{category_col}"
                    )
                    category_values = df[(df[category_col] >= cat_range[0]) & (df[category_col] <= cat_range[1])][category_col].unique()
                else:
                    category_values = st.multiselect(
                        f"Select {category_col} Values",
                        df[category_col].unique(),
                        default=df[category_col].unique()[:5] if len(df[category_col].unique()) > 5 else df[category_col].unique(),
                        key=f"cat_values_{chart_type.lower().replace(' ', '_')}_{category_col}"
                    )

        # Create another row for axis values selection for other chart types
        if chart_type in ["Histogram", "Stacked Histogram", "Side-by-side Histogram"]:
            col_left, col_right = st.columns(2)
            with col_left:
                if pd.api.types.is_numeric_dtype(df[x_col]):
                    x_min, x_max = float(df[x_col].min()), float(df[x_col].max())
                    x_range = st.slider(
                        "Select X-axis Range",
                        min_value=x_min,
                        max_value=x_max,
                        value=(x_min, x_max),
                        key=f"x_range_{chart_type.lower().replace(' ', '_')}_{x_col}"
                    )
                    x_values = df[(df[x_col] >= x_range[0]) & (df[x_col] <= x_range[1])][x_col].unique()
                else:
                    x_values = st.multiselect(
                        "Select X-axis Values",
                        df[x_col].unique(),
                        default=df[x_col].unique()[:5] if len(df[x_col].unique()) > 5 else df[x_col].unique(),
                        key=f"x_values_{chart_type.lower().replace(' ', '_')}_{x_col}"
                    )
            with col_right:
                if chart_type in ["Stacked Histogram", "Side-by-side Histogram"] and color_col is not None:
                    if pd.api.types.is_numeric_dtype(df[color_col]):
                        color_min, color_max = float(df[color_col].min()), float(df[color_col].max())
                        color_range = st.slider(
                            f"Select {color_col} Range",
                            min_value=color_min,
                            max_value=color_max,
                            value=(color_min, color_max),
                            key=f"color_range_{chart_type.lower().replace(' ', '_')}_{color_col}"
                        )
                        color_values = df[(df[color_col] >= color_range[0]) & (df[color_col] <= color_range[1])][color_col].unique()
                    else:
                        color_values = st.multiselect(
                            f"Select {color_col} Values",
                            df[color_col].unique(),
                            default=df[color_col].unique()[:5] if len(df[color_col].unique()) > 5 else df[color_col].unique(),
                            key=f"color_values_{chart_type.lower().replace(' ', '_')}_{x_col}_{color_col}"
                        )
        else:
            col3, col4 = st.columns(2)
            with col3:
                if pd.api.types.is_numeric_dtype(df[x_col]):
                    x_min, x_max = float(df[x_col].min()), float(df[x_col].max())
                    x_range = st.slider(
                        "Select X-axis Range",
                        min_value=x_min,
                        max_value=x_max,
                        value=(x_min, x_max),
                        key=f"x_range_{chart_type.lower().replace(' ', '_')}_{x_col}_{y_col}"
                    )
                    x_values = df[(df[x_col] >= x_range[0]) & (df[x_col] <= x_range[1])][x_col].unique()
                else:
                    x_values = st.multiselect(
                        "Select X-axis Values",
                        df[x_col].unique(),
                        default=df[x_col].unique()[:5] if len(df[x_col].unique()) > 5 else df[x_col].unique(),
                        key=f"x_values_{chart_type.lower().replace(' ', '_')}_{x_col}"
                    )
            with col4:
                if pd.api.types.is_numeric_dtype(df[y_col]):
                    y_min, y_max = float(df[y_col].min()), float(df[y_col].max())
                    y_range = st.slider(
                        "Select Y-axis Range",
                        min_value=y_min,
                        max_value=y_max,
                        value=(y_min, y_max),
                        key=f"y_range_{chart_type.lower().replace(' ', '_')}_{x_col}_{y_col}"
                    )
                    y_values = df[(df[y_col] >= y_range[0]) & (df[y_col] <= y_range[1])][y_col].unique()
                else:
                    y_values = st.multiselect(
                        "Select Y-axis Values",
                        df[y_col].unique(),
                        default=df[y_col].unique()[:5] if len(df[y_col].unique()) > 5 else df[y_col].unique(),
                        key=f"y_values_{chart_type.lower().replace(' ', '_')}_{y_col}"
                    )

        # Create visualization based on selection
        if chart_type in ["Histogram", "Stacked Histogram", "Side-by-side Histogram"]:
            # For histograms, handle numeric x values properly
            if pd.api.types.is_numeric_dtype(df[x_col]):
                hist_df = df[(df[x_col] >= x_range[0]) & (df[x_col] <= x_range[1])]
            else:
                hist_df = df[df[x_col].isin(x_values)]
            
            if chart_type == "Histogram":
                # Handle both numeric and categorical x values
                if pd.api.types.is_numeric_dtype(df[x_col]):
                    hist_df = df[(df[x_col] >= x_range[0]) & (df[x_col] <= x_range[1])]
                else:
                    hist_df = df[df[x_col].isin(x_values)]
                fig = px.histogram(hist_df, x=x_col, nbins=30, title=f"Distribution of {x_col}")
                # Get the number of bins and generate random colors for each
                n_bins = len(fig.data[0].x)
                colors = [f'rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})' for _ in range(n_bins)]
                fig.update_traces(marker=dict(color=colors), showlegend=False, 
                                 texttemplate='%{y}', textposition='outside')
            elif chart_type in ["Stacked Histogram", "Side-by-side Histogram"]:
                # For histograms, filter both x values and color values
                hist_df = df[df[x_col].isin(x_values)]
                if pd.api.types.is_numeric_dtype(df[color_col]):
                    hist_df = hist_df[(hist_df[color_col] >= color_range[0]) & (hist_df[color_col] <= color_range[1])]
                else:
                    hist_df = hist_df[hist_df[color_col].isin(color_values)]
                
                if len(hist_df[color_col].unique()) > 10:
                    # If too many categories, take top 10 by frequency
                    top_categories = hist_df[color_col].value_counts().nlargest(10).index
                    hist_df = hist_df[hist_df[color_col].isin(top_categories)]
                
                barmode = 'stack' if chart_type == "Stacked Histogram" else 'group'
                fig = px.histogram(hist_df, x=x_col, color=color_col, nbins=30,
                                 title=f"{chart_type.replace('-', ' ')} of {x_col} by {color_col}",
                                 barmode=barmode)
            
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title="Count",
                bargap=0.1
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Filter data based on selected x, y, and category values
            # Filter data based on x values, handling numeric types properly
            if pd.api.types.is_numeric_dtype(df[x_col]):
                filtered_df = df[(df[x_col] >= x_range[0]) & (df[x_col] <= x_range[1])]
            else:
                filtered_df = df[df[x_col].isin(x_values)]
            filtered_df = filtered_df[filtered_df[y_col].isin(y_values)]
            
            # For Clustered Bar Chart, also filter by category values
            if chart_type == "Clustered Bar Chart":
                if pd.api.types.is_numeric_dtype(df[category_col]):
                    filtered_df = filtered_df[(filtered_df[category_col] >= cat_range[0]) & (filtered_df[category_col] <= cat_range[1])]
                else:
                    filtered_df = filtered_df[filtered_df[category_col].isin(category_values)]
            
            # Apply aggregation if selected
            if agg_method != "None" and chart_type == "Clustered Bar Chart":
                # For Clustered Bar Chart, group by both x_col and category_col
                if agg_method == "Average":
                    filtered_df = filtered_df.groupby([x_col, category_col])[y_col].mean().reset_index()
                elif agg_method == "Total":
                    filtered_df = filtered_df.groupby([x_col, category_col])[y_col].sum().reset_index()
            elif agg_method != "None":
                if agg_method == "Average":
                    filtered_df = filtered_df.groupby(x_col)[y_col].mean().reset_index()
                elif agg_method == "Total":
                    filtered_df = filtered_df.groupby(x_col)[y_col].sum().reset_index()
            
            if chart_type == "Scatter Plot":
                fig = px.scatter(filtered_df, x=x_col, y=y_col,
                                title=f"{agg_method} of {x_col} vs {y_col}" if agg_method != "None" else f"{x_col} vs {y_col}")
            elif chart_type == "Line Chart":
                fig = px.line(filtered_df, x=x_col, y=y_col,
                            title=f"{agg_method} of {x_col} vs {y_col}" if agg_method != "None" else f"{x_col} vs {y_col}")
            elif chart_type == "Clustered Bar Chart":
                fig = px.bar(filtered_df, x=x_col, y=y_col, color=category_col,
                            title=f"{agg_method} of {x_col} vs {y_col} by {category_col}" if agg_method != "None" else f"{x_col} vs {y_col} by {category_col}",
                            barmode='group')
            else:  # Bar Chart
                fig = px.bar(filtered_df, x=x_col, y=y_col,
                            title=f"{agg_method} of {x_col} vs {y_col}" if agg_method != "None" else f"{x_col} vs {y_col}")
                # Generate random colors for each bar
                n_bars = len(filtered_df)
                colors = [f'rgb({random.randint(0,255)}, {random.randint(0,255)}, {random.randint(0,255)})' for _ in range(n_bars)]
                fig.update_traces(marker=dict(color=colors), texttemplate='%{y}', textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)

        # Center the main visualization
        st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

else:
    st.info("Please upload a data file to begin visualization")