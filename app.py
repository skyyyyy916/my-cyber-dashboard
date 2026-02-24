import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")

# ส่วนหัวของ Dashboard
st.title("🛡️ Cybersecurity Monitoring Dashboard")
st.markdown("---")

# ฟังก์ชันโหลดข้อมูล
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# ส่วนอัปโหลดไฟล์
uploaded_file = st.file_uploader("อัปโหลดไฟล์ .CSV ของคุณ", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)

    # --- Sidebar Filter ---
    st.sidebar.header("🎯 Filters")
    all_attacks = df['attack_type'].unique().tolist()
    selected_attack = st.sidebar.multiselect("เลือกประเภทการโจมตี", all_attacks, default=all_attacks)
    
    # กรองข้อมูล
    filtered_df = df[df['attack_type'].isin(selected_attack)]

    # --- Row 1: Key Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events", f"{len(filtered_df):,}")
    with col2:
        malicious_count = len(filtered_df[filtered_df['label'] == 1])
        st.metric("Malicious Events", f"{malicious_count:,}", delta_color="inverse")
    with col3:
        st.metric("Unique Src IPs", filtered_df['src_ip'].nunique())
    with col4:
        st.metric("Avg Bytes Sent", f"{filtered_df['bytes_sent'].mean():,.0f}")

    st.markdown("### 📈 Visual Analysis")

    # --- Row 2: Charts ---
    c1, c2 = st.columns([1, 1])

    with c1:
        # Donut Chart - แสดงสัดส่วนการโจมตี
        st.subheader("Attack Type Proportions")
        fig_pie = px.pie(filtered_df, names='attack_type', hole=0.5,
                         color_discrete_sequence=px.colors.qualitative.Safe)
        fig_pie.update_traces(textinfo='percent+label', textposition='outside')
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        # Horizontal Bar Chart - Top Target Ports
        st.subheader("Top 10 Targeted Ports")
        port_data = filtered_df['dst_port'].value_counts().head(10).reset_index()
        port_data.columns = ['Port', 'Count']
        fig_bar = px.bar(port_data, x='Count', y=port_data['Port'].astype(str), 
                         orientation='h', text='Count',
                         color='Count', color_continuous_scale='Reds')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- Row 3: Full Data Details ---
    st.markdown("### 📋 Detailed Logs")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("กรุณาอัปโหลดไฟล์ CSV เพื่อเริ่มต้นใช้งาน")
    