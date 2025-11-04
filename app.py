import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from news_scraper import scrape_all
import time, os
from functools import lru_cache

# Set page config first
st.set_page_config(
    page_title="Live News Aggregator (Advanced)",
    layout="wide",
    page_icon="📰",
    initial_sidebar_state="expanded"
)

# Cache the CSS to avoid reprocessing
@st.cache_data
def get_base_css():
    return '''
    :root {
        --text-color: #333333;
        --card-bg: #ffffff;
        --source-bg: #e9ecef;
        --category-bg: #6c757d;
        --category-text: #ffffff;
        --link-color: #0b3d91;
        --card-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    [data-testid="stAppViewContainer"] {
        color: var(--text-color);
    }
    
    .news-card { 
        padding: 14px; 
        margin: 10px; 
        border-radius: 10px; 
        box-shadow: var(--card-shadow);
        background: var(--card-bg);
        color: var(--text-color);
    }
    
    .source-badge { 
        font-size: 12px; 
        padding: 4px 8px; 
        border-radius: 6px; 
        background: var(--source-bg); 
        color: #333;
        display: inline-block; 
    }
    
    .category-badge { 
        font-size: 12px; 
        padding: 4px 8px; 
        border-radius: 6px; 
        background: var(--category-bg);
        color: var(--category-text);
        display: inline-block; 
        margin-left: 8px; 
    }
    
    a { color: var(--link-color); }
    
    .marquee { 
        white-space: nowrap; 
        overflow: hidden; 
        box-sizing: border-box; 
        color: var(--text-color);
    }
    
    .marquee p { 
        display: inline-block; 
        padding-left: 100%; 
        animation: marquee 18s linear infinite; 
        color: var(--text-color);
    }
    
    @keyframes marquee { 
        0% { transform: translate(0, 0); } 
        100% { transform: translate(-100%, 0); } 
    }
    
    /* Dark mode overrides */
    [data-theme="dark"] {
        --text-color: #e0e0e0;
        --card-bg: #1e1e1e;
        --source-bg: #2d2d2d;
        --category-bg: #3a3a3a;
        --link-color: #64b5f6;
        --card-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    [data-theme="dark"] .stMarkdown, 
    [data-theme="dark"] .stMarkdown p, 
    [data-theme="dark"] .stMarkdown h1, 
    [data-theme="dark"] .stMarkdown h2, 
    [data-theme="dark"] .stMarkdown h3,
    [data-theme="dark"] .stMarkdown li {
        color: var(--text-color) !important;
    }
    
    [data-theme="dark"] .stButton>button {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444;
    }
    
    [data-theme="dark"] .stButton>button:hover {
        background-color: #3a3a3a;
    }
    
    [data-theme="dark"] .stTextInput>div>div>input,
    [data-theme="dark"] .stSelectbox>div>div>div>div>div>div>div {
        background-color: #2d2d2d;
        color: #ffffff;
        border-color: #444;
    }
    
    [data-theme="dark"] .stNumberInput>div>div>input {
        background-color: #2d2d2d;
        color: #ffffff;
        border-color: #444;
    }
    
    [data-theme="dark"] .stMarkdown a {
        color: #64b5f6 !important;
    }
    
    [data-theme="dark"] .stMarkdown a:hover {
        color: #90caf9 !important;
    }
    '''

def local_css(css):
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Cache the news data with a timeout
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_news_data(selected_sources):
    try:
        return scrape_all(selected=selected_sources)
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

# Cache wordcloud generation
@st.cache_data(ttl=300)
def generate_wordcloud(text):
    if not text:
        return None
    wc = WordCloud(width=600, height=300, background_color='white').generate(text)
    fig, ax = plt.subplots(figsize=(6,3))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    return fig

# Initialize session state for alerts and favorites
if 'alert_keywords' not in st.session_state:
    st.session_state['alert_keywords'] = []
if 'favorites' not in st.session_state:
    st.session_state['favorites'] = []

# Load CSS
local_css(get_base_css())

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Controls")
    all_sources = ["BBC","CNN","Times of India","NDTV","The Hindu","Al Jazeera"]
    selected_sources = st.multiselect("Select Sources", all_sources, default=all_sources)
    selected_category = st.selectbox("Category", ["All","World","Politics","Business","Sports","India","Tech","Health","General"])
    query = st.text_input("Search headlines...")
    refresh_interval = st.number_input("Auto-refresh (seconds)", min_value=30, max_value=1800, value=180)
    dark_mode = st.checkbox("Dark mode", value=False)
    
    # Alert keywords
    save_keyword = st.text_input("Alert keyword (add and press Enter)")
    if save_keyword and save_keyword not in st.session_state['alert_keywords']:
        st.session_state['alert_keywords'].append(save_keyword)
        st.rerun()
    
    if st.session_state['alert_keywords']:
        st.markdown("**Alert keywords:**")
        for kw in st.session_state['alert_keywords']:
            st.write(f"- {kw}")

# Main content
st.title("📰 Live News Aggregator — Advanced")
st.markdown("An attractive, responsive news aggregator with cards, logos, wordcloud, charts & alerts.")

# Apply theme
if dark_mode:
    st.markdown('''
        <style>
            [data-testid="stAppViewContainer"] {
                background-color: #121212;
                color: #e0e0e0;
            }
            [data-theme="light"] {
                color-scheme: dark;
            }
        </style>
    ''', unsafe_allow_html=True)

# Get and filter data
data = get_news_data(selected_sources)
df = pd.DataFrame(data)

if selected_category != "All":
    df = df[df['Category'] == selected_category]
if query:
    df = df[df['Title'].str.contains(query, case=False, na=False)]

# Show alerts
if st.session_state['alert_keywords'] and not df.empty:
    for kw in st.session_state['alert_keywords']:
        matched = df[df['Title'].str.contains(kw, case=False, na=False)]
        if not matched.empty:
            st.sidebar.success(f'Keyword matched: "{kw}" ({len(matched)} items)')

# Marquee
if not df.empty:
    st.markdown('<div class="marquee"><p>' + '  ||  '.join(df['Title'].head(10).tolist()) + '</p></div>', unsafe_allow_html=True)

# Main columns
left, right = st.columns([3,1])

with left:
    st.header("Headlines")
    for i, row in df.iterrows():
        src = row.get('Source','Unknown')
        logo_key = src.lower().replace(' ','')
        logo_path = os.path.join('assets', f"{logo_key}.svg")
        logo_html = ''
        if os.path.exists(logo_path):
            with open(logo_path, 'r', encoding='utf-8') as f:
                svg = f.read()
                logo_html = f'<div style="display:inline-block; vertical-align: middle; margin-right:10px;">{svg}</div>'
        
        st.markdown(f'''
            <div class="news-card" style="background: {'#0f1720' if dark_mode else '#f9fafb'}">
                <div style="display:flex; align-items:center;">
                    {logo_html}
                    <div style="flex:1">
                        <a href="{row['Link']}" target="_blank" style="text-decoration:none; color: {'#9ad1ff' if dark_mode else '#0b3d91'};"><h4>{row['Title']}</h4></a>
                        <div style="margin-top:6px;">
                            <span class="source-badge">{src}</span>
                            <span class="category-badge">{row['Category']}</span>
                            <span style="margin-left:10px;">🕒 {row['Scraped_At']}</span>
                        </div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

with right:
    st.header("Insights")
    
    # WordCloud
    if not df.empty:
        text = " ".join(df['Title'].tolist())
        wc_fig = generate_wordcloud(text)
        if wc_fig:
            st.pyplot(wc_fig)
    
    # Source distribution
    if not df.empty:
        counts = df['Source'].value_counts().reset_index()
        counts.columns = ['Source','Count']
        fig2 = px.bar(counts, x='Source', y='Count', title='Headlines per Source', 
                     labels={'Count':'Headlines'})
        st.plotly_chart(fig2, use_container_width=True)
    
    # Favorites
    st.markdown("### ⭐ Favorites")
    for fav in st.session_state['favorites']:
        st.markdown(f"- [{fav['title']}]({fav['link']}) ({fav['source']})")
    
    # Actions
    st.markdown("### Actions")
    if st.button("Save top 3 to Favorites"):
        top3 = df.head(3).to_dict('records')
        for item in top3:
            fav = {'title': item['Title'], 'link': item['Link'], 'source': item['Source']}
            if fav not in st.session_state['favorites']:  # Prevent duplicates
                st.session_state['favorites'].append(fav)
        st.success("Saved top 3 to favorites!")
    
    if st.button("Clear Favorites"):
        st.session_state['favorites'] = []
        st.success("Favorites cleared")

# Download button
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download filtered headlines (CSV)", csv, "news_headlines.csv", "text/csv")

# Auto-refresh
if st.button('⏱️ Refresh Now') or 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = time.time()
    st.rerun()

# Show time until next refresh
if 'last_refresh' in st.session_state:
    time_since_refresh = time.time() - st.session_state['last_refresh']
    time_until_refresh = max(0, refresh_interval - time_since_refresh)
    st.markdown(f"<small>Next refresh in: {int(time_until_refresh)} seconds</small>", unsafe_allow_html=True)

# Auto-refresh logic
if time_since_refresh > refresh_interval:
    st.session_state['last_refresh'] = time.time()
    st.rerun()
else:
    time.sleep(1)  # Reduce CPU usage by sleeping between checks
    st.rerun()
