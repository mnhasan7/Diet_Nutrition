# Streamlit GUI for Diet Optimizer
import streamlit as st
import cvxpy as cp
import numpy as np
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="Diet Optimizer",
    layout="wide"
)

# Title and description
st.title("Diet Optimizer")
st.markdown("**Optimize your daily diet to minimize cost while meeting nutritional requirements**")
vid_col, _ = st.columns([5.5, 6.5])
with vid_col:
    st.markdown("Watch a quick overview of the project:")
    st.video("https://youtu.be/rkeTNgGIy38")

# Dataset helpers
def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning shared by bundled and uploaded datasets."""
    df = df.dropna(subset=["Market Price (USD per gram)", "Caloric Value", "Protein"])
    df = df[df["Market Price (USD per gram)"] > 0].reset_index(drop=True)
    if "Category" in df.columns:
        df["Category"] = df["Category"].fillna("Unspecified")
    return df


def validate_dataset(df: pd.DataFrame):
    """Check for required columns and return missing ones."""
    required_cols = [
        "food",
        "Market Price (USD per gram)",
        "Caloric Value",
        "Protein",
        "Carbohydrates",
        "Fat",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    return missing


@st.cache_data
def load_data():
    """Load the bundled dataset from disk."""
    data_dir = "Datasets"
    filename = "food_data_with_prices_with_category.csv"
    data_path = os.path.join(data_dir, filename)
    
    if data_path.endswith(".csv"):
        try:
            df = pd.read_csv(data_path)
        except FileNotFoundError:
            data_path = os.path.join(data_dir, "food_data_with_prices.xlsx")
            df = pd.read_excel(data_path)
    else:
        df = pd.read_excel(data_path)
    
    return clean_dataset(df)

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
    category_labels = df["Category"].astype(str).tolist() if "Category" in df.columns else None
    
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

    # Vitamins (per 100 g -> per g)
    vitamin_cols = [col for col in df.columns if col.startswith("Vitamin ")]
    vitamins_per_g = {col: get_nutrient_per_g(df, col) for col in vitamin_cols}
    
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
    
    # Category diversity constraint (optional)
    if category_labels and params.get('min_categories', 0) > 0:
        unique_cats = sorted(pd.Series(category_labels).unique())
        min_cats_required = min(params['min_categories'], len(unique_cats))
        y = cp.Variable(len(unique_cats), boolean=True)
        max_per_food = params['max_per_food']
        diversity_min_grams = 1.0  # require at least 1g to count a category
        for idx, cat in enumerate(unique_cats):
            mask = np.array([1.0 if label == cat else 0.0 for label in category_labels])
            constraints.append(mask @ x <= max_per_food * y[idx])
            constraints.append(mask @ x >= diversity_min_grams * y[idx])
        constraints.append(cp.sum(y) >= min_cats_required)

    # Objective: minimize cost
    objective = cp.Minimize(c @ x)
    prob = cp.Problem(objective, constraints)
    
    try:
        solved = False
        for solver in [cp.GLPK_MI, cp.ECOS_BB]:
            try:
                prob.solve(solver=solver)
                solved = True
                break
            except Exception:
                continue
        if not solved:
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

            # Vitamin totals (dataset units)
            vitamin_totals = {vit: float(arr @ x.value) for vit, arr in vitamins_per_g.items()}
            
            return prob.status, prob.value, results_df, totals, vitamin_totals
        else:
            return prob.status, None, None, None, None
    except Exception as e:
        return f"Error: {str(e)}", None, None, None, None

# Load data (built-in or uploaded)
st.sidebar.header("Dataset")
data_source = st.sidebar.radio(
    "Choose data source",
    ["Use bundled dataset", "Upload CSV"],
    index=0
)

uploaded_file = st.sidebar.file_uploader(
    "Upload a .csv with required columns",
    type=["csv"],
    help="Required: food, Market Price (USD per gram), Caloric Value, Protein, Carbohydrates, Fat. Optional: other nutrients."
)

try:
    if data_source == "Upload CSV":
        if uploaded_file is None:
            st.sidebar.info("Upload a CSV to use it, or switch back to the bundled dataset.")
            df = load_data()
            st.sidebar.success(f"Loaded {len(df)} foods from bundled dataset")
        else:
            user_df = pd.read_csv(uploaded_file)
            missing_cols = validate_dataset(user_df)
            if missing_cols:
                st.sidebar.error(f"Missing required columns: {', '.join(missing_cols)}")
                st.stop()
            df = clean_dataset(user_df)
            st.sidebar.success(f"Loaded {len(df)} foods from uploaded file")
    else:
        df = load_data()
        st.sidebar.success(f"Loaded {len(df)} foods from bundled dataset")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Sidebar - User Profile Selection
st.sidebar.header("Select Profile or Customize")

profile = st.sidebar.selectbox(
    "Choose a preset profile:",
    ["Custom", "Young Adult Male", "Adult Female", "Senior - Hypertension"]
)

# Profile presets
profiles = {
    "Young Adult Male": {
        'cal_min': 2600, 'cal_max': 2900, 'prot_min': 130,
        'carb_min': 260, 'carb_max': 380, 'fat_min': 70, 'fat_max': 100,
        'fib_min': 25, 'na_max': 2300, 'sug_max': 50, 'chol_max': 300, 'sat_max': 30,
        'min_categories': 0
    },
    "Adult Female": {
        'cal_min': 1800, 'cal_max': 2100, 'prot_min': 80,
        'carb_min': 180, 'carb_max': 260, 'fat_min': 50, 'fat_max': 80,
        'fib_min': 25, 'na_max': 2000, 'sug_max': 35, 'chol_max': 250, 'sat_max': 22,
        'min_categories': 0
    },
    "Senior - Hypertension": {
        'cal_min': 1700, 'cal_max': 2000, 'prot_min': 90,
        'carb_min': 160, 'carb_max': 240, 'fat_min': 50, 'fat_max': 75,
        'fib_min': 25, 'na_max': 1500, 'sug_max': 35, 'chol_max': 200, 'sat_max': 20,
        'min_categories': 0
    }
}

# Initialize parameters
if profile != "Custom":
    params = profiles[profile].copy()
else:
    params = profiles["Young Adult Male"].copy()  # Default values

# Sidebar - Custom Parameters
st.sidebar.header("Nutritional Constraints")

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
with st.sidebar.expander("Mineral Requirements"):
    params['ca_min'] = st.number_input("Min Calcium (mg)", value=800, step=50)
    params['iron_min'] = st.number_input("Min Iron (mg)", value=8, step=1)
    params['mag_min'] = st.number_input("Min Magnesium (mg)", value=200, step=50)
    params['phos_min'] = st.number_input("Min Phosphorus (mg)", value=700, step=50)
    params['k_min'] = st.number_input("Min Potassium (mg)", value=2500, step=100)

# Category controls
if "Category" in df.columns:
    st.sidebar.subheader("Food Categories")
    categories_available = sorted(df["Category"].astype(str).unique())
    selected_categories = st.sidebar.multiselect(
        "Include categories",
        categories_available,
        default=categories_available
    )
    if not selected_categories:
        st.sidebar.warning("No categories selected; using all categories.")
        selected_categories = categories_available
    max_cats = len(selected_categories)
    default_min_cats = min(3, max_cats)
    params['min_categories'] = st.sidebar.slider(
        "Minimum different categories",
        min_value=0,
        max_value=max_cats,
        value=default_min_cats,
        help="Guarantee variety by requiring the solution to include foods from at least this many categories."
    )
else:
    selected_categories = None
    params['min_categories'] = 0

# Apply category filter
if selected_categories:
    df_active = df[df["Category"].astype(str).isin(selected_categories)].reset_index(drop=True)
else:
    df_active = df

# Stop early if filter removes everything
if df_active.empty:
    st.error("No foods left after applying category filters. Please select more categories.")
    st.stop()

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
if st.sidebar.button("Optimize Diet", type="primary", use_container_width=True):
    with st.spinner("Optimizing your diet..."):
        status, cost, results_df, totals, vitamin_totals = optimize_diet(df_active, params)
        
        if status in ["optimal", "optimal_inaccurate"]:
            st.success(f"Optimization successful!")
            
            # Display results in columns
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Cost", f"${cost:.2f}")
            col2.metric("Different Foods", len(results_df))
            col3.metric("Total Weight", f"{results_df['Amount (g)'].sum():.0f}g")
            
            # Food selection table
            st.subheader("Shopping List")
            st.dataframe(
                results_df.style.format({'Amount (g)': '{:.1f}', 'Cost ($)': '${:.2f}'}),
                use_container_width=True,
                hide_index=True
            )
            
            # Download button
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="Download Shopping List (CSV)",
                data=csv,
                file_name="diet_shopping_list.csv",
                mime="text/csv"
            )
            
            # Nutritional summary
            st.subheader("Nutritional Summary")
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
            
            # Vitamin totals table
            if vitamin_totals:
                st.subheader("Vitamin Totals (dataset units)")
                vt_df = pd.DataFrame({
                    'Vitamin': list(vitamin_totals.keys()),
                    'Total': [vitamin_totals[k] for k in vitamin_totals.keys()]
                })
                st.dataframe(vt_df.sort_values('Vitamin'), use_container_width=True, hide_index=True)

            # Macronutrient pie chart
            st.subheader("Macronutrient Distribution")
            macro_data = pd.DataFrame({
                'Nutrient': ['Protein', 'Carbs', 'Fat'],
                'Grams': [totals['Protein'], totals['Carbs'], totals['Fat']]
            })
            st.bar_chart(macro_data.set_index('Nutrient'))
            
        else:
            st.error(f"Optimization failed: {status}")
            st.info("Try relaxing some constraints or adjusting your requirements.")
else:
    # Show instructions
    st.info("Adjust your nutritional requirements in the sidebar and click **Optimize Diet**")
    
    st.subheader("How to Use")
    st.markdown("""
    1. **Select a profile** or create a custom one
    2. **Adjust constraints** to match your dietary needs
    3. **Set variety level** with the max grams per food slider
    4. **Click Optimize** to find the optimal diet plan
    5. **Download** your shopping list as CSV
    """)
    
    st.subheader("Available Foods Preview")
    st.dataframe(
        df_active[['food', 'Caloric Value', 'Protein', 'Carbohydrates', 'Fat', 'Market Price (USD per gram)']].head(10),
        use_container_width=True,
        hide_index=True
    )
