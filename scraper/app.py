# app.py (frontend)
import streamlit as st
import pandas as pd
import altair as alt
from backend import fetch_emails, get_ebay_avg_price

# Set page config for a sexy UI
st.set_page_config(
    page_title="Ziggi Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for insane UX - enhanced with neon Pokémon theme, background, better animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* Global styles */
.stApp {
background-image: url('https://wallpapers.com/images/hd/neon-city-aesthetic-96p1k833z3pjdgkn.jpg');
background-size: cover;
background-position: center;
color: #e0e0e0;
font-family: 'Press Start 2P', cursive;
}
header { visibility: hidden; } /* Hide Streamlit header */
.stSidebar {
background-color: rgba(15, 52, 96, 0.8);
border-right: 2px solid #e94560;
backdrop-filter: blur(5px);
}
.stButton > button {
background: linear-gradient(45deg, #e94560, #ff2e63);
color: white;
border: none;
border-radius: 30px;
padding: 12px 24px;
font-weight: bold;
transition: all 0.4s ease;
box-shadow: 0 0 10px #ff2e63;
}
.stButton > button:hover {
transform: scale(1.1) rotate(5deg);
box-shadow: 0 0 20px #ff2e63, 0 0 30px #e94560;
}
.stMetric {
background: rgba(22, 33, 62, 0.7);
border-radius: 15px;
padding: 15px;
box-shadow: 0 4px 8px rgba(0,0,0,0.3), inset 0 0 10px rgba(255,46,99,0.2);
backdrop-filter: blur(3px);
}
.stMetric label {
color: #ffd700 !important;
font-size: 16px !important;
}
.stMetric [data-testid="stMetricValue"] {
color: #ffffff !important;
font-size: 28px !important;
font-weight: bold !important;
text-shadow: 0 0 5px #ffd700;
}
.stMetric [data-testid="stMetricDelta"] {
font-size: 18px !important;
color: #4ade80 !important;
}
/* Enhanced color-coded metrics with Pokémon flair */
[data-testid="metric-container"]:nth-child(1) { border-left: 5px solid #4ade80; animation: electric 1s infinite; } /* Confirmed */
[data-testid="metric-container"]:nth-child(2) { border-left: 5px solid #ef4444; } /* Canceled */
[data-testid="metric-container"]:nth-child(3) { border-left: 5px solid #f59e0b; } /* Shipped */
[data-testid="metric-container"]:nth-child(4) { border-left: 5px solid #3b82f6; } /* Delivered */
[data-testid="metric-container"]:nth-child(5) { border-left: 5px solid #a855f7; } /* Stick % */
[data-testid="metric-container"]:nth-child(6) { border-left: 5px solid #22c55e; } /* Total Orders */
[data-testid="metric-container"]:nth-child(7) { border-left: 5px solid #eab308; } /* Total Spent */
/* Table styles */
.stDataFrame {
background: rgba(22, 33, 62, 0.7);
border-radius: 15px;
overflow: hidden;
box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}
thead tr th {
background: linear-gradient(#0f3460, #1a1a2e);
color: #ffd700;
text-align: center;
font-family: 'Press Start 2P';
}
tbody tr:nth-child(even) {
background-color: rgba(26, 26, 46, 0.8);
}
/* Item cards with hover pop */
.stColumn > div > div > div > div {
background: rgba(22, 33, 62, 0.8);
border-radius: 15px;
padding: 20px;
box-shadow: 0 4px 8px rgba(0,0,0,0.3);
transition: all 0.4s ease;
backdrop-filter: blur(5px);
}
.stColumn > div > div > div > div:hover {
transform: translateY(-10px) scale(1.05);
box-shadow: 0 8px 16px rgba(233,69,96,0.5), 0 0 20px #ff2e63;
}
/* Chart */
.stAltairChart {
background: rgba(22, 33, 62, 0.7);
border-radius: 15px;
padding: 15px;
box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}
/* Sidebar caption */
.stSidebar .stCaption {
color: #ffd700;
}
/* Electric glow animation like Pikachu's thunder */
@keyframes electric {
0% { box-shadow: 0 0 5px #ffd700, 0 0 10px #ffff00; }
50% { box-shadow: 0 0 20px #ffd700, 0 0 30px #ffff00, 0 0 40px #ffcc00; }
100% { box-shadow: 0 0 5px #ffd700, 0 0 10px #ffff00; }
}
h1, h2, h3 {
color: #ffffff !important;
text-shadow: 0 0 10px #ff2e63, 0 0 20px #e94560;
font-family: 'Press Start 2P';
}
/* Fade-in for elements */
div[data-testid="stElementContainer"] {
animation: fadeIn 1s ease-in;
}
@keyframes fadeIn {
from { opacity: 0; transform: translateY(20px); }
to { opacity: 1; transform: translateY(0); }
}
/* Pokémon spin */
.poke-spin {
animation: spin 3s linear infinite;
}
@keyframes spin {
0% { transform: rotate(0deg); }
100% { transform: rotate(360deg); }
}
/* Floating Pokémon */
@keyframes float {
0% { transform: translateY(0px); }
50% { transform: translateY(-20px); }
100% { transform: translateY(0px); }
}
.float-poke {
animation: float 3s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

# Product images (update with actual URLs for your items)
PRODUCT_IMAGES = {
'Mega Diancie Ex Battle Deck': 'https://www.pokemon.com/static-assets/content-assets/cms2/img/trading-card-game/series/incrementals/2025/mega-battle-deck-mega-gengar-ex-mega-diancie-ex/mega-battle-deck-mega-gengar-ex-mega-diancie-ex-169-en.png',
'Mega Greninja Ex Battle Deck': 'https://m.media-amazon.com/images/I/81DvxvLRMfL.jpg'
}

# Enhanced Pokémon GIFs
POKEBALL_GIF = "https://sweezy-cursors.com/wp-content/uploads/cursor/auto-draft/pokemon-spinning-pokeball-animated-custom-cursor.gif"
PIKACHU_GIF = "https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUybXEzdmlqN21sbDR3YzA2MHhvN3N1ZTlhbDF5NWozaXBxeGZrYXRpcyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/e5q0CVGJab5fmW8mme/giphy.gif"
BATTLE_GIF = "https://media4.giphy.com/media/vkBoW05WXhCGn4Kdkz/giphy.gif"

# Main App
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    st.image(POKEBALL_GIF, width=120, caption="Catch 'Em All!")
with col2:
    st.title('Ziggi Bot')
with col3:
    st.image(PIKACHU_GIF, width=120, caption="Pika Power!")
st.markdown("### Ultimate Pokémon TCG Drop Tracker - Powered Up! ⚡")

st.sidebar.info('Epic hunts with neon vibes! Customize for max power.')
st.sidebar.image(PIKACHU_GIF, width=200, caption="Pika-Party!")

email_addr = st.sidebar.text_input('Gmail Address', value='yourgmail@gmail.com')
password = st.sidebar.text_input('App Password', type='password', value='your_app_password')
days_back = st.sidebar.slider('Days Back to Search', 1, 90, 30, help="Scan deeper into your email history!")
if st.sidebar.button('Refresh Data 🔥'):
    with st.spinner('Charging up... Thunderbolt incoming!'):
        st.image(PIKACHU_GIF, width=200)
        st.cache_data.clear()
        st.snow() # Pokémon weather effect
        st.balloons() # Celebration

df = fetch_emails(email_addr, password, days_back=days_back)

if df.empty:
    st.warning('No orders detected. Power up your creds or extend range. Tune regex for elite parsing!')
else:
    selected_site = st.selectbox('Select Retailer', ['All'] + sorted(df['Site'].unique()), help="Focus your Pokédex!")
    filtered_df = df if selected_site == 'All' else df[df['Site'] == selected_site]

    if not filtered_df.empty:
        # Enhanced Tabs with icons
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Stats Arena", "🛒 Item Dex", "📋 Order Log", "💰 Profit Calc"])

        with tab1:
            st.header(f"{selected_site} Drop Battle Stats" if selected_site != 'All' else 'Global Gym Overview')
            total_orders = len(filtered_df)
            status_counts = filtered_df['Status'].value_counts()
            confirmed = status_counts.get('Confirmed', 0)
            canceled = status_counts.get('Canceled', 0)
            shipped = status_counts.get('Shipped', 0)
            delivered = status_counts.get('Delivered', 0)
            stick_pct = ((total_orders - canceled) / total_orders * 100) if total_orders else 0
            total_spent = filtered_df['Amount'].sum()

            cols = st.columns(7)
            cols[0].metric('Confirmed ✅', confirmed, delta=f"{confirmed / total_orders * 100:.1f}%" if total_orders else "0%")
            cols[1].metric('Canceled ❌', canceled, delta=f"-{canceled / total_orders * 100:.1f}%" if total_orders else "0%", delta_color="inverse")
            cols[2].metric('Shipped 🚀', shipped)
            cols[3].metric('Delivered 📦', delivered)
            cols[4].metric('Stick % 💪', f"{stick_pct:.1f}%")
            cols[5].metric('Total Orders 📑', total_orders)
            cols[6].metric('Total Spent 💸', f"${total_spent:.2f}")

            # Pie chart for status
            pie_data = pd.DataFrame({
                'Status': ['Confirmed', 'Canceled', 'Shipped', 'Delivered'],
                'Count': [confirmed, canceled, shipped, delivered]
            })
            pie_chart = alt.Chart(pie_data).mark_arc().encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Status", type="nominal", scale=alt.Scale(range=['#4ade80', '#ef4444', '#f59e0b', '#3b82f6'])),
                tooltip=['Status', 'Count']
            ).properties(title="Status Distribution")
            st.altair_chart(pie_chart, use_container_width=True)

        with tab2:
            st.subheader('Item Pokédex')
            unique_items = filtered_df['Item'].unique()
            item_cols = st.columns(min(len(unique_items), 4)) # More responsive
            for idx, item in enumerate(unique_items):
                with item_cols[idx % 4]:
                    image_url = PRODUCT_IMAGES.get(item, 'https://via.placeholder.com/150')
                    st.image(image_url, use_column_width=True)
                    st.image(BATTLE_GIF, width=150, caption="Epic Battle!")
                    item_df = filtered_df[filtered_df['Item'] == item]
                    item_status = item_df['Status'].value_counts()
                    item_confirmed = item_status.get('Confirmed', 0)
                    item_canceled = item_status.get('Canceled', 0)
                    item_shipped = item_status.get('Shipped', 0)
                    item_delivered = item_status.get('Delivered', 0)
                    item_total_orders = len(item_df)
                    item_stick_pct = ((item_total_orders - item_canceled) / item_total_orders * 100) if item_total_orders else 0
                    item_spent = item_df['Amount'].sum()
                    item_qty = item_df['Quantity'].sum()
                    st.metric('Confirmed ✅', item_confirmed)
                    st.metric('Canceled ❌', item_canceled)
                    st.metric('Shipped 🚀', item_shipped)
                    st.metric('Delivered 📦', item_delivered)
                    st.metric('Stick Rate 💪', f"{item_stick_pct:.1f}%")
                    st.metric('Total Orders 📑', item_total_orders)
                    st.metric('Spent 💸', f"${item_spent:.2f}")
                    st.metric('Active Quantity 🛍️', item_qty)
                    avg_price = get_ebay_avg_price(item)
                    profit_per_unit = avg_price - (item_spent / item_qty if item_qty else 0)
                    st.metric('eBay Avg Sold 📈', f"${avg_price:.2f}", delta=f"{profit_per_unit:.2f} profit/unit" if item_qty else "N/A", delta_color="normal" if profit_per_unit > 0 else "inverse")

        with tab3:
            st.subheader(f'Order Battle Log ({total_orders})')
            search_query = st.text_input("Search Orders", help="Search by Item, Order ID, etc.")
            display_df = filtered_df[['Site', 'Item', 'Order ID', 'Date', 'Delivery Date', 'Status', 'Amount', 'Quantity']].rename(columns={
                'Site': 'Retailer',
                'Date': 'Order Date',
                'Amount': 'Total'
            }).sort_values('Order Date', ascending=False)
            if search_query:
                display_df = display_df[display_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
            # Color-code status
            def color_status(val):
                color = {
                    'Confirmed': '#4ade80',
                    'Canceled': '#ef4444',
                    'Shipped': '#f59e0b',
                    'Delivered': '#3b82f6',
                    'Unknown': '#6b7280'
                }.get(val, '#ffffff')
                return f'background-color: {color}; color: black;'
            styled_df = display_df.style.applymap(color_status, subset=['Status'])
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Order Date': st.column_config.DatetimeColumn(format="MMM DD, YYYY"),
                    'Total': st.column_config.NumberColumn(format="$%.2f")
                }
            )
            # Export button
            csv = display_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Orders CSV 📥", csv, "orders.csv", "text/csv")

        with tab4:
            st.subheader('Profit Projection Gym')
            total_profit = 0
            profit_data = []
            for item in filtered_df['Item'].unique():
                item_df = filtered_df[filtered_df['Item'] == item]
                item_qty = item_df['Quantity'].sum()
                item_spent = item_df['Amount'].sum()
                avg_price = get_ebay_avg_price(item)
                item_profit = (avg_price * item_qty) - item_spent
                total_profit += item_profit
                profit_data.append({'Item': item, 'Profit': item_profit})
                st.metric(f"{item} Profit", f"${item_profit:.2f}", delta_color="normal" if item_profit > 0 else "inverse")
            st.metric("Total Projected Profit", f"${total_profit:.2f}", delta_color="normal" if total_profit > 0 else "inverse")

            # Bar chart for profits
            profit_df = pd.DataFrame(profit_data)
            bar_chart = alt.Chart(profit_df).mark_bar().encode(
                x='Item',
                y='Profit',
                color=alt.condition(
                    alt.datum.Profit > 0,
                    alt.value('#4ade80'), # Positive green
                    alt.value('#ef4444') # Negative red
                ),
                tooltip=['Item', 'Profit']
            ).properties(title="Item Profits")
            st.altair_chart(bar_chart, use_container_width=True)

        # Advanced Analytics Expander
        with st.expander("📈 Elite Analytics"):
            st.subheader('Spent Over Time')
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
            line_data = filtered_df.groupby(filtered_df['Date'].dt.date)['Amount'].sum().reset_index()
            line_chart = alt.Chart(line_data).mark_line(point=True, color='#ff2e63').encode(
                x='Date:T',
                y='Amount:Q',
                tooltip=['Date', 'Amount']
            ).properties(title="Daily Spend Trend")
            st.altair_chart(line_chart, use_container_width=True)