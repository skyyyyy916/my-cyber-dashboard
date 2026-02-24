import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")

st.title("🛡️ Cybersecurity Monitoring Dashboard")
st.markdown("วิเคราะห์ข้อมูลการจราจรทางเครือข่ายและประเภทการโจมตี")
st.markdown("---")

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df = df.dropna(how='all')
    df = df.dropna(subset=['attack_type'])
    return df

# 2. ส่วนการจัดการไฟล์ (เช็คตรงนี้ดีๆ ครับ)
uploaded_file = st.file_uploader("อัปโหลดไฟล์ .CSV ของคุณ", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)
else:
    # ถ้ายังไม่มีการอัปโหลด ให้ลองดึงไฟล์จากระบบมาโชว์ก่อน
    try:
        df = load_data("cybersecurity1.csv") # ชื่อไฟล์ต้องตรงกับใน GitHub
        st.success("📊 แสดงข้อมูลตัวอย่างจากไฟล์ในระบบอัตโนมัติ")
    except:
        st.info("👋 ยินดีต้อนรับ! กรุณาอัปโหลดไฟล์ CSV เพื่อเริ่มต้นใช้งาน")
        st.stop() 

# --- 3. ส่วนสร้าง Filter และกราฟ (ต้องอยู่นอก if/else ข้างบน) ---
# บรรทัดเหล่านี้ต้องเริ่มที่ชิดซ้ายสุด (ไม่เยื้องเข้า) เพื่อให้แสดงผลตลอดเวลาที่มี data
st.sidebar.header("🎯 Filters")

all_attacks = sorted(df['attack_type'].unique().tolist())
selected_attack = st.sidebar.multiselect("เลือกประเภทการโจมตี", all_attacks, default=all_attacks)

all_protocols = df['protocol'].unique().tolist()
selected_proto = st.sidebar.multiselect("เลือก Protocol", all_protocols, default=all_protocols)

# กรองข้อมูล
mask = (df['attack_type'].isin(selected_attack)) & (df['protocol'].isin(selected_proto))
filtered_df = df[mask]

# --- 4. ส่วนแสดงผล KPI และ กราฟ ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Events", f"{len(filtered_df):,}")
with col2:
    malicious_count = len(filtered_df[filtered_df['label'] == 1]) if 'label' in filtered_df.columns else 0
    st.metric("Malicious Events", f"{malicious_count:,}", delta_color="inverse")
with col3:
    st.metric("Unique Src IPs", f"{filtered_df['src_ip'].nunique():,}")
with col4:
    avg_sent = filtered_df['bytes_sent'].mean() if 'bytes_sent' in filtered_df.columns else 0
    st.metric("Avg Bytes Sent", f"{avg_sent:,.0f}")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    st.subheader("📊 Attack Type Proportions")
    fig_pie = px.pie(filtered_df, names='attack_type', hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_traces(textinfo='percent+label', textposition='outside')
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("🔝 Top 10 Targeted Ports")
    port_data = filtered_df['dst_port'].value_counts().head(10).reset_index()
    port_data.columns = ['Port', 'Count']
    fig_bar = px.bar(port_data, x='Count', y=port_data['Port'].astype(str), 
                     orientation='h', text='Count',
                     color='Count', color_continuous_scale='Reds')
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("### 📋 Detailed Logs")
with st.expander("คลิกเพื่อดูข้อมูลทั้งหมด"):
    st.dataframe(filtered_df, use_container_width=True)
