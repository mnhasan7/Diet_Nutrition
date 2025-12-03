# Streamlit GUI for Diet Optimizer
import streamlit as st
import cvxpy as cp
import numpy as np
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="Diet Optimizer",
    page_icon="🥗",
    layout="wide"
)

# Title and description
st.title("🥗 Diet Optimizer")
st.markdown("**Optimize your daily diet to minimize cost while meeting nutritional requirements**")

# Load dataset
@st.cache_data
def load_data():
    DATA_DIR = "Datasets"
    FILENAME = "food_data_with_prices.csv"
    DATA_PATH = os.path.join(DATA_DIR, FILENAME)
    
    if DATA_PATH.endswith(".csv"):
        try:
            df = pd.read_csv(DATA_PATH)
        except FileNotFoundError:
            DATA_PATH = os.path.join(DATA_DIR, "food_data_with_prices.xlsx")
            df = pd.read_excel(DATA_PATH)
    else:
        df = pd.read_excel(DATA_PATH)
    
    # Basic cleaning
    df = df.dropna(subset=["Market Price (USD per gram)", "Caloric Value", "Protein"])
    df = df[df["Market Price (USD per gram)"] > 0].reset_index(drop=True)
    
    return df

# Helper function
def get_nutrient_per_g(df, column_name, conversion_factor=100.0):
    """Extract nutrient data and convert to per-gram basis."""
    if column_name not in df.columns:
        return np.zeros(len(df))
    return df[column_name].fillna(0).to_numpy() / conversion_factor

# Optimization function
def optimize_diet(df, params):
    """Run diet optimization with given parameters."""
    n = len(df)
    food_names = df["food"].astype(str).tolist()
    
    # Build nutrient arrays
    c = get_nutrient_per_g(df, "Market Price (USD per gram)", conversion_factor=1.0)
    cal_per_g = get_nutrient_per_g(df, "Caloric Value")
    prot_per_g = get_nutrient_per_g(df, "Protein")
    carb_per_g = get_nutrient_per_g(df, "Carbohydrates")
    fat_per_g = get_nutrient_per_g(df, "Fat")
    sat_per_g = get_nutrient_per_g(df, "Saturated Fats")
    fib_per_g = get_nutrient_per_g(df, "Dietary Fiber")
    sugar_per_g = get_nutrient_per_g(df, "Sugars")
    Na_per_g = get_nutrient_per_g(df, "Sodium")
    chol_per_g = get_nutrient_per_g(df, "Cholesterol")
    
    # Minerals
    Calcium_per_g = get_nutrient_per_g(df, "Calcium")
    Iron_per_g = get_nutrient_per_g(df, "Iron")
    Magnesium_per_g = get_nutrient_per_g(df, "Magnesium")
    Phosphorus_per_g = get_nutrient_per_g(df, "Phosphorus")
    Potassium_per_g = get_nutrient_per_g(df, "Potassium")
    
    # Decision variable
    x = cp.Variable(n, nonneg=True)
    
    # Constraints
    constraints = [x <= params['max_per_food']]
    
    # Macronutrient constraints
    constraints += [
        cal_per_g @ x >= params['cal_min'],
        cal_per_g @ x <= params['cal_max'],
        prot_per_g @ x >= params['prot_min'],
        carb_per_g @ x >= params['carb_min'],
        carb_per_g @ x <= params['carb_max'],
        fat_per_g @ x >= params['fat_min'],
        fat_per_g @ x <= params['fat_max'],
        fib_per_g @ x >= params['fib_min'],
        sugar_per_g @ x <= params['sug_max'],
        Na_per_g @ x <= params['na_max'],
        chol_per_g @ x <= params['chol_max'],
        sat_per_g @ x <= params['sat_max']
    ]
    
    # Mineral constraints
    constraints += [
        Calcium_per_g @ x >= params['ca_min'],
        Iron_per_g @ x >= params['iron_min'],
        Magnesium_per_g @ x >= params['mag_min'],
        Phosphorus_per_g @ x >= params['phos_min'],
        Potassium_per_g @ x >= params['k_min']
    ]
    
    # Objective: minimize cost
    objective = cp.Minimize(c @ x)
    prob = cp.Problem(objective, constraints)
    
    try:
        prob.solve()
        
        if prob.status in ["optimal", "optimal_inaccurate"]:
            # Extract results
            selected_foods = []
            for i in range(n):
                if x.value[i] is not None and x.value[i] > 1e-3:
                    selected_foods.append({
                        'Food': food_names[i],
                        'Amount (g)': round(x.value[i], 1),
                        'Cost ($)': round(x.value[i] * c[i], 2)
                    })
            
            results_df = pd.DataFrame(selected_foods)
            
            # Calculate nutritional totals
            totals = {
                'Calories': float(cal_per_g @ x.value),
                'Protein': float(prot_per_g @ x.value),
                'Carbs': float(carb_per_g @ x.value),
                'Fat': float(fat_per_g @ x.value),
                'Fiber': float(fib_per_g @ x.value),
                'Sugar': float(sugar_per_g @ x.value),
                'Sodium': float(Na_per_g @ x.value),
                'Cholesterol': float(chol_per_g @ x.value),
                'Saturated Fat': float(sat_per_g @ x.value)
            }
            
            return prob.status, prob.value, results_df, totals
        else:
            return prob.status, None, None, None
    except Exception as e:
        return f"Error: {str(e)}", None, None, None

# Load data
try:
    df = load_data()
    st.sidebar.success(f"✅ Loaded {len(df)} foods from dataset")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar - User Profile Selection
st.sidebar.header("📊 Select Profile or Customize")

profile = st.sidebar.selectbox(
    "Choose a preset profile:",
    ["Custom", "Young Adult Male", "Adult Female", "Senior - Hypertension"]
)

# Profile presets
profiles = {
    "Young Adult Male": {
        'cal_min': 2600, 'cal_max': 2900, 'prot_min': 130,
        'carb_min': 260, 'carb_max': 380, 'fat_min': 70, 'fat_max': 100,
        'fib_min': 25, 'na_max': 2300, 'sug_max': 50, 'chol_max': 300, 'sat_max': 30
    },
    "Adult Female": {
        'cal_min': 1800, 'cal_max': 2100, 'prot_min': 80,
        'carb_min': 180, 'carb_max': 260, 'fat_min': 50, 'fat_max': 80,
        'fib_min': 25, 'na_max': 2000, 'sug_max': 35, 'chol_max': 250, 'sat_max': 22
    },
    "Senior - Hypertension": {
        'cal_min': 1700, 'cal_max': 2000, 'prot_min': 90,
        'carb_min': 160, 'carb_max': 240, 'fat_min': 50, 'fat_max': 75,
        'fib_min': 25, 'na_max': 1500, 'sug_max': 35, 'chol_max': 200, 'sat_max': 20
    }
}

# Initialize parameters
if profile != "Custom":
    params = profiles[profile].copy()
else:
    params = profiles["Young Adult Male"].copy()  # Default values

# Sidebar - Custom Parameters
st.sidebar.header("⚙️ Nutritional Constraints")

# Calories
col1, col2 = st.sidebar.columns(2)
params['cal_min'] = col1.number_input("Min Calories", value=params['cal_min'], step=100)
params['cal_max'] = col2.number_input("Max Calories", value=params['cal_max'], step=100)

# Protein
params['prot_min'] = st.sidebar.number_input("Min Protein (g)", value=params['prot_min'], step=10)

# Carbs
col1, col2 = st.sidebar.columns(2)
params['carb_min'] = col1.number_input("Min Carbs (g)", value=params['carb_min'], step=10)
params['carb_max'] = col2.number_input("Max Carbs (g)", value=params['carb_max'], step=10)

# Fat
col1, col2 = st.sidebar.columns(2)
params['fat_min'] = col1.number_input("Min Fat (g)", value=params['fat_min'], step=5)
params['fat_max'] = col2.number_input("Max Fat (g)", value=params['fat_max'], step=5)

# Fiber
params['fib_min'] = st.sidebar.number_input("Min Fiber (g)", value=params['fib_min'], step=5)

# Limits
st.sidebar.subheader("Maximum Limits")
params['sug_max'] = st.sidebar.number_input("Max Sugar (g)", value=params['sug_max'], step=5)
params['na_max'] = st.sidebar.number_input("Max Sodium (mg)", value=params['na_max'], step=100)
params['chol_max'] = st.sidebar.number_input("Max Cholesterol (mg)", value=params['chol_max'], step=50)
params['sat_max'] = st.sidebar.number_input("Max Saturated Fat (g)", value=params['sat_max'], step=5)

# Minerals
with st.sidebar.expander("🧪 Mineral Requirements"):
    params['ca_min'] = st.number_input("Min Calcium (mg)", value=800, step=50)
    params['iron_min'] = st.number_input("Min Iron (mg)", value=8, step=1)
    params['mag_min'] = st.number_input("Min Magnesium (mg)", value=200, step=50)
    params['phos_min'] = st.number_input("Min Phosphorus (mg)", value=700, step=50)
    params['k_min'] = st.number_input("Min Potassium (mg)", value=2500, step=100)

# Variety constraint
params['max_per_food'] = st.sidebar.slider(
    "Max grams per food (variety)", 
    min_value=100, 
    max_value=500, 
    value=300, 
    step=50,
    help="Lower values encourage more food variety"
)

# Optimize button
if st.sidebar.button("🚀 Optimize Diet", type="primary", use_container_width=True):
    with st.spinner("Optimizing your diet..."):
        status, cost, results_df, totals = optimize_diet(df, params)
        
        if status in ["optimal", "optimal_inaccurate"]:
            st.success(f"✅ Optimization successful!")
            
            # Display results in columns
            col1, col2, col3 = st.columns(3)
            col1.metric("💰 Total Cost", f"${cost:.2f}")
            col2.metric("🍽️ Different Foods", len(results_df))
            col3.metric("📦 Total Weight", f"{results_df['Amount (g)'].sum():.0f}g")
            
            # Food selection table
            st.subheader("🛒 Shopping List")
            st.dataframe(
                results_df.style.format({'Amount (g)': '{:.1f}', 'Cost ($)': '${:.2f}'}),
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Shopping List (CSV)",
                data=csv,
                file_name="diet_shopping_list.csv",
                mime="text/csv"
            )
            
            # Nutritional summary
            st.subheader("📊 Nutritional Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Calories", f"{totals['Calories']:.0f} kcal")
                st.metric("Protein", f"{totals['Protein']:.1f} g")
                st.metric("Carbs", f"{totals['Carbs']:.1f} g")
            
            with col2:
                st.metric("Fat", f"{totals['Fat']:.1f} g")
                st.metric("Fiber", f"{totals['Fiber']:.1f} g")
                st.metric("Sugar", f"{totals['Sugar']:.1f} g")
            
            with col3:
                st.metric("Sodium", f"{totals['Sodium']:.0f} mg")
                st.metric("Cholesterol", f"{totals['Cholesterol']:.0f} mg")
                st.metric("Saturated Fat", f"{totals['Saturated Fat']:.1f} g")
            
            # Macronutrient pie chart
            st.subheader("🥧 Macronutrient Distribution")
            macro_data = pd.DataFrame({
                'Nutrient': ['Protein', 'Carbs', 'Fat'],
                'Grams': [totals['Protein'], totals['Carbs'], totals['Fat']]
            })
            st.bar_chart(macro_data.set_index('Nutrient'))
            
        else:
            st.error(f"❌ Optimization failed: {status}")
            st.info("Try relaxing some constraints or adjusting your requirements.")
else:
    # Show instructions
    st.info("👈 Adjust your nutritional requirements in the sidebar and click **Optimize Diet**")
    
    st.subheader("📖 How to Use")
    st.markdown("""
    1. **Select a profile** or create a custom one
    2. **Adjust constraints** to match your dietary needs
    3. **Set variety level** with the max grams per food slider
    4. **Click Optimize** to find the optimal diet plan
    5. **Download** your shopping list as CSV
    """)
    
    st.subheader("📋 Available Foods Preview")
    st.dataframe(
        df[['food', 'Caloric Value', 'Protein', 'Carbohydrates', 'Fat', 'Market Price (USD per gram)']].head(10),
        use_container_width=True,
        hide_index=True
    )
