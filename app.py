import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# ============================================
# ICD-11 CHAPTER RANGES
# ============================================
icd11_ranges = {
    "1. Certain infectious or parasitic diseases": ("1A00", "1H0Z"),
    "2. Neoplasms": ("2A00", "2F9Z"),
    "3. Diseases of the blood or blood-forming organs": ("3A00", "3C0Z"),
    "4. Diseases of the immune system": ("4A00", "4B4Z"),
    "5. Endocrine, nutritional and metabolic diseases": ("5A00", "5D46"),
    "6. Mental, behavioural and neurodevelopmental disorders": ("6A00", "6E8Z"),
    "7. Sleep-wake disorders": ("7A00", "7B2Z"),
    "8. Diseases of the nervous system": ("8A00", "8E7Z"),
    "9. Diseases of the visual system": ("9A00", "9E1Z"),
    "10. Diseases of the ear or mastoid process": ("AA00", "AC0Z"),
    "11. Diseases of the circulatory system": ("BA00", "BE2Z"),
    "12. Diseases of the respiratory system": ("CA00", "CB7Z"),
    "13. Diseases of the digestive system": ("DA00", "DE2Z"),
    "14. Diseases of the skin or subcutaneous tissue": ("EA00", "EM0Z"),
    "15. Diseases of musculoskeletal system": ("FA00", "FC0Z"),
    "16. Diseases of the genitourinary system": ("GA00", "GC8Z"),
    "17. Sexual health conditions": ("HA00", "HA8Z"),
    "18. Pregnancy/childbirth": ("JA00", "JB6Z"),
    "19. Perinatal conditions": ("KA00", "KD5Z"),
    "20. Developmental anomalies": ("LA00", "LD9Z"),
    "21. Symptoms/clinical findings NEC": ("MA00", "MH2Y"),
    "22. Injury/poisoning/external causes": ("NA00", "NF2Z")
}

# ============================================
# CATEGORY FUNCTION
# ============================================
def find_category(code):
    code = str(code).strip().upper()
    for category, (start, end) in icd11_ranges.items():
        if start <= code <= end:
            return category
        if code.startswith(start[:2]):
            return category
    return "Unknown"


# ============================================
# STREAMLIT UI
# ============================================
st.title("📘 ICD-11 Diagnosis Classifier Dashboard")

uploaded_files = st.file_uploader(
    "Upload Diagnosis Files (.csv, .xlsx, .txt)", 
    type=["csv", "xlsx", "txt"], 
    accept_multiple_files=True
)

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

# ============================================
# LOAD DATA
# ============================================
if uploaded_files:
    dfs = []
    for file in uploaded_files:
        name = file.name
        if name.endswith(".csv"):
            df = pd.read_csv(file)
        elif name.endswith(".xlsx"):
            df = pd.read_excel(file)
        elif name.endswith(".txt"):
            df = pd.read_csv(file, header=None, names=["Diagnosis"])
        else:
            st.error(f"Unsupported file type: {name}")
            st.stop()
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)

    # Detect column
    if "Diagnosis" in data.columns:
        col = "Diagnosis"
    elif "code" in data.columns:
        col = "code"
    else:
        st.error("No 'Diagnosis' or 'code' column found!")
        st.stop()

    data[col] = data[col].astype(str).str.strip().str.upper()
    data["ICD_Category"] = data[col].apply(find_category)
    st.session_state.data = data

    st.success(f"Loaded {data.shape[0]} diagnoses.")
    st.dataframe(data.head(10))

data = st.session_state.data


# ============================================
# TABS
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload",
    "📊 Summary",
    "🔎 Range Search",
    "🎯 Specific Code Search"
])


# ============================================
# TAB 1 — UPLOAD
# ============================================
with tab1:
    st.write("Upload diagnosis files to begin.")


# ============================================
# TAB 2 — SUMMARY
# ============================================
with tab2:
    if data.empty:
        st.warning("Upload data first!")
    else:
        st.subheader("📊 ICD-11 Chapter Counts")

        summary = data["ICD_Category"].value_counts().reset_index()
        summary.columns = ["ICD Chapter", "Count"]

        st.dataframe(summary)

        # Plot
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(summary["ICD Chapter"], summary["Count"])
        ax.set_xticklabels(summary["ICD Chapter"], rotation=90)
        ax.set_ylabel("Count")
        ax.set_title("Distribution of Diagnoses by ICD-11 Chapter")

        st.pyplot(fig)


# ============================================
# TAB 3 — RANGE SEARCH
# ============================================
with tab3:
    st.subheader("🔎 Range Search")

    if data.empty:
        st.warning("Upload data first!")
    else:
        start = st.text_input("Start Code (e.g., 2A00)")
        end = st.text_input("End Code (e.g., 2F9Z)")

        if st.button("Run Range Search"):
            col = "Diagnosis" if "Diagnosis" in data.columns else "code"
            filtered = data[(data[col] >= start.upper()) & (data[col] <= end.upper())]

            st.write(f"Found **{filtered.shape[0]}** diagnoses in range:")
            st.dataframe(filtered)


# ============================================
# TAB 4 — SPECIFIC CODE SEARCH
# ============================================
with tab4:
    st.subheader("🎯 Specific Code Search")

    if data.empty:
        st.warning("Upload data first!")
    else:
        sc = st.text_input("Specific Code (e.g., 2A20)")

        if st.button("Run Specific Code Search"):
            col = "Diagnosis" if "Diagnosis" in data.columns else "code"
            filtered_sc = data[data[col].str.startswith(sc.upper())].copy()
            filtered_sc["ICD_Category"] = filtered_sc[col].apply(find_category)

            st.write(f"Found **{filtered_sc.shape[0]}** diagnoses starting with '{sc}':")
            st.dataframe(filtered_sc)
