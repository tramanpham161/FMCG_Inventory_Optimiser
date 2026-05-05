import streamlit as st
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(page_title="FMCG Inventory Optimiser", page_icon="📦", layout="wide")

# --- CUSTOM CSS FOR MINIMALIST NAVY THEME (Consistency with Project 1) ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    h1 { color: #001F3F; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { background-color: #001F3F; color: white; border-radius: 5px; width: 100%; }
    .stMetric { border: 1px solid #f0f2f6; padding: 15px; border-radius: 10px; background-color: #fcfcfc; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISE SESSION STATE FOR MASTER PLAN ---
if 'inventory_plan' not in st.session_state:
    st.session_state.inventory_plan = []

# --- HEADER ---
st.title("FMCG Inventory Optimiser")

# --- SIDEBAR: PRODUCT CONFIGURATION ---
with st.sidebar:
    st.header("Product Settings")
    item_name = st.text_input("Item Name", value="Fresh Beef", help="Enter the name of the SKU or product category.")
    
    st.divider()
    
    daily_sales = st.number_input("Average Daily Sales (Units)", value=50, min_value=1, help="The average number of units sold per day.")
    unit_cost = st.number_input("Unit Cost (£)", value=5.50, min_value=0.01, help="The cost price paid to the supplier per unit.")
    
    st.divider()
    
    shelf_life = st.number_input("Shelf Life (Days)", value=10, min_value=1, help="Maximum days the product remains sellable.")
    lead_time = st.number_input("Supplier Lead Time (Days)", value=3, min_value=1, help="Time from placing an order to stock arrival.")
    current_stock = st.number_input("Current Stock Level", value=120, min_value=0, help="Units currently available in the warehouse.")

# --- INVENTORY LOGIC CALCULATIONS ---
# 1. Reorder Point (ROP) = (Sales * Lead Time) + 10% Buffer
rop = int((daily_sales * lead_time) * 1.1)

# 2. Days of Cover = Current Stock / Daily Sales
days_of_cover = round(current_stock / daily_sales, 1)

# 3. Waste Risk % = (Days of Cover / Shelf Life) * 100
waste_risk_pct = round((days_of_cover / shelf_life) * 100, 1)

# 4. Total Planned Spend = ROP * Unit Cost
total_spend = round(rop * unit_cost, 2)

# --- MAIN PAGE: LIVE METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Reorder Point (ROP)", f"{rop} Units", 
              help="Calculation: (Daily Sales × Lead Time) + 10% Safety Buffer. This is the stock level that triggers a new order.")

with col2:
    st.metric("Days of Cover", f"{days_of_cover} Days", 
              help="Calculation: Current Stock ÷ Daily Sales. Indicates how long until stockouts occur.")

with col3:
    st.metric("Waste Risk %", f"{waste_risk_pct}%", 
              help="Calculation: (Days of Cover ÷ Shelf Life) × 100. Flags if stock will expire before sale.")

with col4:
    st.metric("Total Planned Spend", f"£{total_spend}", 
              help="Calculation: Reorder Point × Unit Cost. This is the capital required for the next replenishment order.")

# --- ALERTS & LOGIC WARNINGS ---
st.write("### Operational Alerts")
if days_of_cover < 2:
    st.error(f"🔴 **STOCKOUT IMMINENT:** Only {days_of_cover} days of stock remaining. Place an order immediately.")
elif days_of_cover <= lead_time:
    st.warning(f"🟡 **ORDER REQUIRED:** Current stock will not last the {lead_time}-day lead time.")
else:
    st.success("🟢 **STOCK SECURE:** Current levels exceed the lead time requirement.")

if waste_risk_pct > 80:
    st.error(f"⚠️ **HIGH SPOILAGE RISK:** Days of cover is {waste_risk_pct}% of the total shelf life. Reduce order quantities.")

# --- MASTER BUYING PLAN (SESSION STATE) ---
st.divider()
if st.button("Add Item to Master Order List"):
    new_item = {
        "Item Name": item_name,
        "Reorder Point (Units)": rop,
        "Unit Cost (£)": unit_cost,
        "Total Spend (£)": total_spend,
        "Days of Cover": days_of_cover,
        "Waste Risk %": waste_risk_pct
    }
    st.session_state.inventory_plan.append(new_item)
    st.toast('Item added to Buying Plan!')

if st.session_state.inventory_plan:
    st.write("### Master Buying Plan")
    df = pd.DataFrame(st.session_state.inventory_plan)
    st.dataframe(df, use_container_width=True)
    
    # Calculate Total Plan Value
    total_plan_value = df["Total Spend (£)"].sum()
    st.write(f"**Total Consolidated Spend:** £{round(total_plan_value, 2)}")
    
    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Buying Plan as CSV",
        data=csv,
        file_name='fmcg_buying_plan.csv',
        mime='text/csv',
    )

# --- FOOTER ---
st.markdown("<br><hr><center>FMCG Inventory Optimiser | Operational Decision Support Tool</center>", unsafe_allow_html=True)
