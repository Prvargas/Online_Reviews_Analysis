import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

#######################
# Page Configuration
st.set_page_config(page_title='Health Insurance Customer Reviews Dashboard', layout='wide')

#######################
# Load data
@st.cache_data
def load_data():
    '''Load the customer data'''
    df = pd.read_excel(r"03 - Updated_Synthetic_Merged_Data_with_Additional_Columns.xlsx")
    return df

df = load_data()

#######################
# Sidebar Filters
st.sidebar.title("Health Insurance Customer Reviews Dashboard")
st.sidebar.header("Filters")

# Year Slider
min_year = int(df['Review_Year'].min())
max_year = int(df['Review_Year'].max())
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

# MultiSelect filters
plan_types = st.sidebar.multiselect("Select Plan Types", options=df['Plan_Type'].unique())
genders = st.sidebar.multiselect("Select Genders", options=df['Gender'].unique())
age_groups = st.sidebar.multiselect("Select Age Groups", options=df['Age_Group'].unique())
regions = st.sidebar.multiselect("Select Regions", options=df['Region'].unique())
sentiments = st.sidebar.multiselect("Select Sentiments", options=df['Sentiment'].unique())

#######################
# Apply Filters
filtered_df = df[
    (df['Review_Year'].between(selected_years[0], selected_years[1])) &
    (df['Plan_Type'].isin(plan_types) if plan_types else True) &
    (df['Gender'].isin(genders) if genders else True) &
    (df['Age_Group'].isin(age_groups) if age_groups else True) &
    (df['Region'].isin(regions) if regions else True) &
    (df['Sentiment'].isin(sentiments) if sentiments else True)
]

#######################
# Dashboard Title
#st.title("Health Insurance Customer Reviews Dashboard")

#######################
# Visualization Functions
def create_year_over_year_avg_rating_chart_with_indicator(data):
    """
    Creates and displays a bar chart of year-over-year average ratings with an indicator for the most recent year.

    Parameters:
    data (DataFrame): A pandas DataFrame containing the columns 'Review_Year' and 'Rating'.

    Returns:
    Figure: A plotly Figure object
    """
    # Calculate the year-over-year average rating
    yearly_avg_rating = data.groupby('Review_Year')['Rating'].mean().reset_index()

    # Get the most recent year and the prior year average ratings
    most_recent_year = yearly_avg_rating['Review_Year'].max()
    prior_year = most_recent_year - 1

    most_recent_avg_rating = yearly_avg_rating.loc[yearly_avg_rating['Review_Year'] == most_recent_year, 'Rating'].values[0]
    prior_year_avg_rating = yearly_avg_rating.loc[yearly_avg_rating['Review_Year'] == prior_year, 'Rating'].values[0]

    # Create a bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=yearly_avg_rating['Review_Year'],
        y=yearly_avg_rating['Rating'],
        textposition='auto'
    ))

    # Add the indicator
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=round(most_recent_avg_rating, 2),
        delta={'reference': prior_year_avg_rating, 'relative': True, 'position': "top", 'valueformat': ".2%", 'font': {'size': 15}},
        title={"text": "CY Avg Rating"},
        domain={'x': [0.5, 0.5], 'y': [0.01, 1]},
        number={'font': {'size': 50}}
    ))

    # Update layout for KPI card size and style
    fig.update_layout(
        title=dict(text='YoY Avg Rating', font=dict(size=20), x=0.5, xanchor='center'),
        showlegend=False,  # Hide the legend to keep it clean
        margin=dict(l=20, r=20, t=50, b=20),  # Adjust margins to fit the card size
        height=200,  # Set a smaller height to fit a metric card
        width=300,  # Set a smaller width to fit a metric card
        template='plotly_white',
        yaxis=dict(range=[0, 5])  # Ensure the y-axis range is appropriate
    )

    return fig

def create_sentiment_donut_chart(data):
    """
    Creates and displays a donut pie chart showing the percentage split for the 'Sentiment' column based on review counts.

    Parameters:
    data (DataFrame): A pandas DataFrame containing the column 'Sentiment'.

    Returns:
    Figure: A plotly Figure object
    """
    # Calculate the percentage split for 'Sentiment'
    sentiment_counts = data['Sentiment'].value_counts(normalize=True) * 100
    sentiment_labels = sentiment_counts.index
    sentiment_values = sentiment_counts.values

    # Define color mapping
    color_mapping = {'negative': 'red', 'neutral': 'yellow', 'positive': 'green'}
    sentiment_colors = [color_mapping[sentiment] for sentiment in sentiment_labels]

    # Create the donut pie chart
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_labels,
        values=sentiment_values,
        hole=.5,  # Make the hole larger to emphasize the donut shape
        marker=dict(colors=sentiment_colors),
        textinfo='percent',  # Display both label and percentage
        textfont=dict(size=10),  # Adjust font size to fit inside the chart
        insidetextorientation='horizontal',  # Ensure text is horizontal
    )])

    # Update layout for KPI card size and style
    fig.update_layout(
        title=dict(text='Customer Sentiment', font=dict(size=15), x=0.5, xanchor='center', y=.9),
        annotations=[dict(text='Sentiment', x=0.5, y=0.5, font_size=10, showarrow=False)],
        showlegend=False,  # Hide the legend to keep it clean
        margin=dict(l=10, r=10, t=40, b=10),  # Adjust margins to fit the card size
        height=300,  # Set a smaller height to fit a metric card
        width=300,  # Set a smaller width to fit a metric card
    )

    return fig

def create_kpi_card(title, value, subtitle, color):
    """
    Creates a KPI card with the given information.
    
    Parameters:
    title (str): The title of the KPI
    value (str): The main value to display
    subtitle (str): Additional information to display below the value
    color (str): The color of the value text
    
    Returns:
    str: HTML string for the KPI card
    """
    return f"""
    <div class="kpi-card">
        <h3 class="kpi-title">{title}</h3>
        <p class="kpi-value" style="color: {color};">{value}</p>
        <p class="kpi-subtitle">{subtitle}</p>
    </div>
    """

def display_topic_metrics(filtered_df):
    """
    Calculate topic-related metrics and return KPI card HTML strings.
    
    Parameters:
    filtered_df (pd.DataFrame): DataFrame containing 'Topic' and 'Rating' columns.
    
    Returns:
    tuple: HTML strings for highest rated, lowest rated, and most popular topic KPI cards
    """
    # Calculate highest and lowest rated topics across all sentiments
    topic_ratings = filtered_df.groupby('Topic')['Rating'].mean()
    highest_rated_topic = topic_ratings.idxmax()
    highest_rating = topic_ratings.max()
    lowest_rated_topic = topic_ratings.idxmin()
    lowest_rating = topic_ratings.min()

    # Calculate most popular topic
    topic_counts = filtered_df['Topic'].value_counts()
    most_popular_topic = topic_counts.index[0] if not topic_counts.empty else "N/A"
    most_popular_count = topic_counts.iloc[0]

    highest_rated_card = create_kpi_card(
        "Highest Rated Topic",
        highest_rated_topic,
        f"Avg Rating: {highest_rating:.2f}",
        "#00FF00"
    )

    lowest_rated_card = create_kpi_card(
        "Lowest Rated Topic",
        lowest_rated_topic,
        f"Avg Rating: {lowest_rating:.2f}",
        "#FF4136"
    )

    most_popular_card = create_kpi_card(
        "Most Popular Topic",
        most_popular_topic,
        f"Count: {most_popular_count:,}",
        "#7FDBFF"
    )

    return highest_rated_card, lowest_rated_card, most_popular_card


def create_bubble_chart(filtered_df):
    """
    Creates a bubble chart for topic analysis with average rating vs. review count.
    Parameters:
    filtered_df (pd.DataFrame): A DataFrame containing the data with columns 'Topic', 'Rating', and 'Customer_ID_Reviews'.
    Returns:
    fig_bubble (plotly.graph_objs._figure.Figure): The Plotly figure object representing the bubble chart.
    The bubble chart displays the average rating and review count for each topic. 
    Topics are categorized into 'Negative', 'Neutral', and 'Positive' based on the average rating. 
    The size of the bubbles corresponds to the number of reviews, and colors indicate the rating category.
    """
    # Bubble Chart: Topics
    topic_data = filtered_df.groupby('Topic').agg({
        'Rating': 'mean',
        'Customer_ID_Reviews': 'count'
    }).reset_index()
    topic_data.columns = ['Topic', 'Average_Rating', 'Review_Count']
    def get_color_category(rating):
        if rating < 2.5:
            return 'Negative'
        elif 2.5 <= rating < 4:
            return 'Neutral'
        else:  # rating >= 4
            return 'Positive'
    topic_data['Color_Category'] = topic_data['Average_Rating'].apply(get_color_category)
    color_map_bubble = {
        'Negative': '#87CEFA',  # Light Sky Blue
        'Neutral': '#E6E6FA',   # Light Purple
        'Positive': '#9370DB'   # Medium Purple
    }
    fig_bubble = px.scatter(topic_data, 
                            x='Topic', 
                            y='Average_Rating', 
                            size='Review_Count', 
                            color='Color_Category',
                            color_discrete_map=color_map_bubble,
                            hover_name='Topic',
                            size_max=60,
                            title='Topic Analysis: Average Rating vs Review Count')
    fig_bubble.update_layout(
        xaxis_title='Topics',
        yaxis_title='Average Rating',
        xaxis={'categoryorder':'total descending'},
        legend_title_text='Rating Category',
        legend=dict(
            orientation='h',
            x=0.5,
            y=1,
            xanchor='left',
            yanchor='bottom'
        )
    )
    fig_bubble.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Average Rating: %{y:.2f}<br>Review Count: %{marker.size}<br>Category: %{color}'
    )
    fig_bubble.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')), selector=dict(mode='markers'))
    fig_bubble.update_xaxes(tickangle=45)
    
    return fig_bubble

##UNUSED PLOT TO AVOID SCROLLING
def create_region_topic_heatmap(filtered_df):
    """
    Creates a heatmap chart for average rating by region and topic.
    Parameters:
    filtered_df (pd.DataFrame): A DataFrame containing the data with columns 'Region', 'Topic', and 'Rating'.
    Returns:
    fig_heatmap (plotly.graph_objs._figure.Figure): The Plotly figure object representing the heatmap chart.
    The heatmap chart displays the average rating categorized by region and topic.
    """
    # Heatmap: Average Rating by Region and Topic
    heatmap_data = filtered_df.pivot_table(values='Rating', index='Region', columns='Topic', aggfunc='mean')
    fig_heatmap = px.imshow(heatmap_data, 
                            color_continuous_scale=px.colors.sequential.Purples,
                            title='Average Rating by Region and Topic')
    return fig_heatmap


def display_top_states(filtered_df):
    """
    Displays a dataframe with top states and their average ratings in Streamlit.

    Parameters:
    filtered_df (pd.DataFrame): A DataFrame containing the data with columns 'State' and 'Rating'.

    Returns:
    None

    The function groups the data by state, calculates the average rating, and displays a styled dataframe with columns for state and rating.
    """
    # Group by state and calculate mean rating
    states_ratings_df = filtered_df.groupby('State')['Rating'].mean().reset_index()

    # Round the ratings to two decimal places
    states_ratings_df['Rating'] = states_ratings_df['Rating'].round(2)

    # Sort the dataframe by Rating in descending order
    states_ratings_df = states_ratings_df.sort_values(by='Rating', ascending=False)


    # Determine the maximum rating for the progress column configuration
    max_rating = states_ratings_df['Rating'].max()

    st.markdown('#### Avg Rating by State')

    st.dataframe(states_ratings_df,
                 column_order=("State", "Rating"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "State": st.column_config.TextColumn(
                        "State",
                    ),
                    "Rating": st.column_config.ProgressColumn(
                        "Rating",
                        format="%0.2f",
                        min_value=0,
                        max_value=max_rating,
                     )}
                 )



def create_heatmap_chart(filtered_df):
    """
    Creates a heatmap chart for average rating by gender and age group.

    Parameters:
    filtered_df (pd.DataFrame): A DataFrame containing the data with columns 'Age_Group', 'Gender', and 'Rating'.

    Returns:
    fig_heatmap (plotly.graph_objs._figure.Figure): The Plotly figure object representing the heatmap chart.

    The heatmap chart displays the average rating categorized by gender and age group.
    """
    # Heatmap: Average Rating by Gender and Age Group
    heatmap_data = filtered_df.pivot_table(values='Rating', index='Age_Group', columns='Gender', aggfunc='mean')
    fig_heatmap = px.imshow(heatmap_data, 
                            color_continuous_scale=px.colors.sequential.Purples,
                            title='Demo Heatmap')
    
    # Remove whitespace and make the title closer to the chart
    fig_heatmap.update_layout(
        margin=dict(l=40, r=20, t=40, b=40),
        title=dict(
            y=.95,
            x=0.47,
            xanchor='center',
            yanchor='top'
        ),
        coloraxis_showscale=False,  # Removes the color scale legend
        xaxis_title=None,  # Removes the 'Gender' label
        yaxis_title=None,   # Removes the 'Age_Group' label
        height=300,  # Set the chart height
        width=400    # Set the chart width
    )

    # Add labels inside the heatmap
    fig_heatmap.update_traces(
        texttemplate='%{z:.2f}',
        textfont=dict(color='black'),
        hovertemplate=None
    )
    
    return fig_heatmap


import plotly.express as px
import pandas as pd

def create_region_heatmap_chart(filtered_df):
    """
    Creates a heatmap chart for average rating by plan type and region.

    Parameters:
    filtered_df (pd.DataFrame): A DataFrame containing the data with columns 'Region', 'Plan_Type', and 'Rating'.

    Returns:
    fig_heatmap (plotly.graph_objs._figure.Figure): The Plotly figure object representing the heatmap chart.

    The heatmap chart displays the average rating categorized by plan type and region.
    """
    # Heatmap: Average Rating by Plan Type and Region
    heatmap_data = filtered_df.pivot_table(values='Rating', index='Region', columns='Plan_Type', aggfunc='mean')
    fig_heatmap = px.imshow(heatmap_data, 
                            color_continuous_scale=px.colors.sequential.Purples,
                            title='Region Heatmap')
    
    # Remove whitespace and make the title closer to the chart
    fig_heatmap.update_layout(
        margin=dict(l=40, r=20, t=40, b=40),
        title=dict(
            y=0.95,
            x=0.5,
            xanchor='center',
            yanchor='top'
        ),
        coloraxis_showscale=False,  # Removes the color scale legend
        xaxis_title=None,  # Removes the 'Plan_Type' label
        yaxis_title=None,   # Removes the 'Region' label
        height=300,  # Set the chart height
        width=400    # Set the chart width
    )

    # Add labels inside the heatmap
    fig_heatmap.update_traces(
        texttemplate='%{z:.2f}',
        textfont=dict(color='black'),
        hovertemplate=None
    )
    
    return fig_heatmap









#PAGE STARTS HERE
#######################
# Apply custom CSS

st.markdown(    
    """
    <style>
.kpi-container {
    display: flex;
    justify-content: space-between;
    gap: 5px;
    margin-bottom: 10px;
    width: 100%;
}
.kpi-card {
    background-color: #333333;
    padding: 10px;
    border-radius: 5px;
    color: white;
    text-align: center;
    flex: 1;
    height: 100px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
}
.kpi-title {
    color: white !important;
    font-weight: bold;
    margin-bottom: -10px;
    font-size: 11px; /* Starting size */
}
.kpi-value {
    font-weight: bold;
    margin: -5px 0;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
    font-size: 15px; /* Starting size */
    line-height: 1.2;
}
.kpi-subtitle {
    color: #DDDDDD !important;
    margin-top: 5px;
    font-size: 10px; /* Starting size */
}
</style>

<script>
function autoFitText() {
    const elements = document.querySelectorAll('.kpi-title, .kpi-value, .kpi-subtitle');
    elements.forEach(el => {
        let fontSize = parseInt(window.getComputedStyle(el).fontSize);
        const maxSize = fontSize;
        const minSize = 8;
        const maxHeight = el.parentElement.clientHeight * (el.classList.contains('kpi-value') ? 0.5 : 0.25);
        
        while (el.scrollHeight > maxHeight && fontSize > minSize) {
            fontSize--;
            el.style.fontSize = fontSize + 'px';
        }
        
        while (el.scrollHeight < maxHeight && fontSize < maxSize) {
            fontSize++;
            el.style.fontSize = fontSize + 'px';
            if (el.scrollHeight > maxHeight) {
                el.style.fontSize = (fontSize - 1) + 'px';
                break;
            }
        }
    });
}

// Run on load and resize
window.addEventListener('load', autoFitText);
window.addEventListener('resize', autoFitText);

// If using Streamlit, you might need to trigger this when the Streamlit app updates
if (window.Streamlit) {
    Streamlit.onStreamlitLoaded(() => {
        setInterval(autoFitText, 1000); // Check every second
    });
}
</script>
    """,
    unsafe_allow_html=True
)



#######################
# Main Dashboard Layout
col1, col2, col3, col4 = st.columns((1.5, 4.5, 1.5, 2), gap='medium')

# Column 1
with col1:
    fig1 = create_year_over_year_avg_rating_chart_with_indicator(filtered_df)
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = create_sentiment_donut_chart(filtered_df)
    st.plotly_chart(fig2, use_container_width=True)

# Column 2
with col2:
    highest_rated_card, lowest_rated_card, most_popular_card = display_topic_metrics(filtered_df)
    
    st.markdown(
        f"""
        <div class="kpi-container">
            {highest_rated_card}
            {lowest_rated_card}
            {most_popular_card}
        """,
        unsafe_allow_html=True
    )
    
    fig_bubble = create_bubble_chart(filtered_df)
    st.plotly_chart(fig_bubble, use_container_width=True)

# Column 3
with col3:
    fig_heat = create_heatmap_chart(filtered_df)
    st.plotly_chart(fig_heat, use_container_width=True, )

    fig_region_heat = create_region_heatmap_chart(filtered_df)
    st.plotly_chart(fig_region_heat, use_container_width=True)
    

# Column 4
with col4:
    display_top_states(filtered_df)

#######################
# Footer
st.write('---')
st.write('This dataset consists of synthetic health insurance information.')