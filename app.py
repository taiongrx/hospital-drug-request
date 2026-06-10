import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. ตั้งค่าหน้าเพจและธีม
st.set_page_config(
    page_title="ระบบจัดการยืมยา/เวชภัณฑ์", 
    page_icon="💊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# จำลองฐานข้อมูลด้วยไฟล์ CSV
DB_FILE = "borrow_logs.csv"

# กำหนดสีของสถานะเพื่อให้อ่านง่าย
STATUS_COLORS = {
    "รอพิจารณา": "🟠 รอพิจารณา",
    "รอยา": "🔵 รอยา",
    "รับยาแล้ว": "🟢 รับยาแล้ว",
    "ไม่อนุมัติ": "🔴 ไม่อนุมัติ"
}

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        columns = [
            "รหัสคำขอ", "วันที่บันทึก", "ผู้ขอเบิก", "ตำแหน่ง", "ฝ่าย/กลุ่มงาน", 
            "โรงพยาบาลที่ขอยืม", "รายการที่ 1", "จำนวนที่ 1",
            "รายการที่ 2", "จำนวนที่ 2", "รายการที่ 3", "จำนวนที่ 3",
            "ต้องการใช้ภายในวันที่", "เวลา", "สถานะการอนุมัติ", "เหตุผล(กรณีไม่อนุมัติ)", "ผู้อนุมัติ"
        ]
        return pd.DataFrame(columns=columns)

def save_new_request(data_dict):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def update_request(req_id, new_status, reject_reason, approver):
    df = load_data()
    idx = df.index[df['รหัสคำขอ'] == req_id].tolist()
    if idx:
        df.at[idx[0], 'สถานะการอนุมัติ'] = new_status
        df.at[idx[0], 'เหตุผล(กรณีไม่อนุมัติ)'] = reject_reason
        df.at[idx[0], 'ผู้อนุมัติ'] = approver
        df.to_csv(DB_FILE, index=False)
        return True
    return False

# ตกแต่ง Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100) # โลโก้จำลอง
    st.title("ระบบยืม-คืนยา")
    st.markdown("โรงพยาบาลสมเด็จพระยุพราชสายบุรี")
    st.divider()
    menu = st.radio("📌 เมนูการทำงาน", [
        "📝 ฟอร์มขอเบิก/ยืมยา", 
        "👨‍⚕️ พิจารณาอนุมัติ", 
        "📊 Dashboard ติดตามสถานะ"
    ])

# ==========================================
# เมนูที่ 1: สำหรับผู้ขอเบิก
# ==========================================
if menu == "📝 ฟอร์มขอเบิก/ยืมยา":
    st.header("📝 บันทึกข้อความขอเบิกยา/เวชภัณฑ์ไม่ใช่ยา")
    st.caption("กรอกข้อมูลให้ครบถ้วนเพื่อความรวดเร็วในการพิจารณาอนุมัติ")
    
    with st.form("borrow_form", clear_on_submit=True):
        # ใช้ container แบ่งโซนให้ดูง่ายขึ้น
        with st.container(border=True):
            st.markdown("#### 👤 ส่วนที่ 1: ข้อมูลผู้ขอ")
            col1, col2, col3 = st.columns(3)
            with col1:
                req_name = st.text_input("ชื่อ-นามสกุล ผู้ขอเบิก *")
            with col2:
                position = st.text_input("ตำแหน่ง")
            with col3:
                department = st.text_input("ฝ่าย/กลุ่มงาน *")
                
            target_hospital = st.text_input("🏥 ขอสนับสนุนจากโรงพยาบาล (ระบุชื่อ) *", placeholder="เช่น รพ.ปัตตานี, รพ.ไม้แก่น")

        with st.container(border=True):
            st.markdown("#### 💊 ส่วนที่ 2: รายการยา/เวชภัณฑ์ที่ต้องการ")
            
            c_item1, c_qty1 = st.columns([3, 1])
            item1 = c_item1.text_input("รายการที่ 1 *")
            qty1 = c_qty1.number_input("จำนวน (1)", min_value=0, step=1)
            
            c_item2, c_qty2 = st.columns([3, 1])
            item2 = c_item2.text_input("รายการที่ 2")
            qty2 = c_qty2.number_input("จำนวน (2)", min_value=0, step=1)
            
            c_item3, c_qty3 = st.columns([3, 1])
            item3 = c_item3.text_input("รายการที่ 3")
            qty3 = c_qty3.number_input("จำนวน (3)", min_value=0, step=1)

        with st.container(border=True):
            st.markdown("#### ⏰ ส่วนที่ 3: กำหนดเวลาที่ต้องใช้")
            col_date, col_time = st.columns(2)
            with col_date:
                needed_date = st.date_input("ต้องการใช้ภายในวันที่")
            with col_time:
                needed_time = st.time_input("เวลา")
            
        st.info("💡 รหัสคำขอจะถูกสร้างอัตโนมัติหลังจากกดบันทึกข้อมูล")
        
        # จัดตำแหน่งปุ่มให้อยู่ตรงกลางหรือขวา
        col_blank, col_btn = st.columns([4, 1])
        with col_btn:
            submitted = st.form_submit_button("ส่งคำขอ 📤", use_container_width=True)
        
        if submitted:
            if not req_name or not target_hospital or not item1 or not department:
                st.error("⚠️ กรุณากรอกข้อมูลที่มีเครื่องหมาย * ให้ครบถ้วน")
            else:
                req_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M')}"
                new_record = {
                    "รหัสคำขอ": req_id,
                    "วันที่บันทึก": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "ผู้ขอเบิก": req_name,
                    "ตำแหน่ง": position,
                    "ฝ่าย/กลุ่มงาน": department,
                    "โรงพยาบาลที่ขอยืม": target_hospital,
                    "รายการที่ 1": item1, "จำนวนที่ 1": qty1,
                    "รายการที่ 2": item2, "จำนวนที่ 2": qty2,
                    "รายการที่ 3": item3, "จำนวนที่ 3": qty3,
                    "ต้องการใช้ภายในวันที่": needed_date.strftime("%Y-%m-%d"),
                    "เวลา": needed_time.strftime("%H:%M"),
                    "สถานะการอนุมัติ": "รอพิจารณา",
                    "เหตุผล(กรณีไม่อนุมัติ)": "-",
                    "ผู้อนุมัติ": "-"
                }
                save_new_request(new_record)
                st.success(f"✅ ส่งคำขอสำเร็จ! รหัสอ้างอิง: **{req_id}**")

# ==========================================
# เมนูที่ 2: สำหรับเภสัชกร
# ==========================================
elif menu == "👨‍⚕️ พิจารณาอนุมัติ":
    st.header("👨‍⚕️ หน้าต่างพิจารณาอนุมัติคำขอยืมยา")
    
    df = load_data()
    if df.empty:
        st.info("ไม่มีข้อมูลคำขอในระบบ")
    else:
        active_requests = df[df["สถานะการอนุมัติ"].isin(["รอพิจารณา", "รอยา"])]
        
        if active_requests.empty:
            st.success("🎉 ปัจจุบันไม่มีรายการค้างพิจารณา ยอดเยี่ยมมากครับ!")
        else:
            st.subheader("📋 รายการที่ต้องดำเนินการ")
            
            # ปรับแต่งตารางให้อ่านง่ายขึ้น
            display_df = active_requests[["รหัสคำขอ", "ผู้ขอเบิก", "ฝ่าย/กลุ่มงาน", "โรงพยาบาลที่ขอยืม", "สถานะการอนุมัติ"]]
            display_df["สถานะ"] = display_df["สถานะการอนุมัติ"].map(STATUS_COLORS)
            st.dataframe(display_df.drop(columns=["สถานะการอนุมัติ"]), hide_index=True, use_container_width=True)
            
            st.divider()
            st.subheader("🔄 อัปเดตสถานะคำขอ")
            
            with st.container(border=True):
                req_list = active_requests["รหัสคำขอ"].tolist()
                selected_req = st.selectbox("🔍 เลือกรหัสคำขอที่ต้องการจัดการ", ["-- กรุณาเลือก --"] + req_list)
                
                if selected_req != "-- กรุณาเลือก --":
                    selected_data = active_requests[active_requests["รหัสคำขอ"] == selected_req].iloc[0]
                    
                    # แสดงสรุปข้อมูลแบบ Card
                    st.info(f"**ผู้ขอ:** {selected_data['ผู้ขอเบิก']} ({selected_data['ฝ่าย/กลุ่มงาน']}) \n\n"
                            f"**ยืมจาก:** {selected_data['โรงพยาบาลที่ขอยืม']} \n\n"
                            f"**รายการหลัก:** {selected_data['รายการที่ 1']} (จำนวน {selected_data['จำนวนที่ 1']})")
                    
                    with st.form("approval_form"):
                        col_stat, col_name = st.columns(2)
                        with col_stat:
                            new_status = st.selectbox(
                                "อัปเดตสถานะเป็น", 
                                ["รอพิจารณา", "รอยา", "รับยาแล้ว", "ไม่อนุมัติ"],
                                index=["รอพิจารณา", "รอยา", "รับยาแล้ว", "ไม่อนุมัติ"].index(selected_data["สถานะการอนุมัติ"])
                            )
                        with col_name:
                            approver_name = st.text_input("ชื่อเภสัชกรผู้ดำเนินการ *")
                            
                        reject_reason = st.text_input("หมายเหตุ (จำเป็นหากเลือก 'ไม่อนุมัติ')", value="-")
                        
                        update_btn = st.form_submit_button("💾 บันทึกการอัปเดต", use_container_width=True)
                        
                        if update_btn:
                            if not approver_name:
                                st.error("⚠️ กรุณาระบุชื่อเภสัชกรผู้ดำเนินการ")
                            elif new_status == "ไม่อนุมัติ" and (reject_reason == "-" or not reject_reason):
                                st.error("⚠️ กรุณาระบุเหตุผลกรณีไม่อนุมัติ")
                            else:
                                if update_request(selected_req, new_status, reject_reason, approver_name):
                                    st.success(f"✅ อัปเดตสถานะเป็น '{new_status}' เรียบร้อยแล้ว")
                                    st.rerun() # รีเฟรชหน้าจออัตโนมัติ

# ==========================================
# เมนูที่ 3: Dashboard ติดตามสถานะ
# ==========================================
elif menu == "📊 Dashboard ติดตามสถานะ":
    st.header("📊 Dashboard ภาพรวมการยืม-คืนยา")
    
    df = load_data()
    
    if df.empty:
        st.info("ยังไม่มีข้อมูลในระบบ")
    else:
        # ใช้ container แยกส่วนสรุปตัวเลข
        with st.container(border=True):
            total = len(df)
            pending = len(df[df["สถานะการอนุมัติ"] == "รอพิจารณา"])
            waiting = len(df[df["สถานะการอนุมัติ"] == "รอยา"])
            received = len(df[df["สถานะการอนุมัติ"] == "รับยาแล้ว"])
            rejected = len(df[df["สถานะการอนุมัติ"] == "ไม่อนุมัติ"])
            
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("📋 ทั้งหมด", total)
            c2.metric("🟠 รอพิจารณา", pending)
            c3.metric("🔵 รอยา", waiting)
            c4.metric("🟢 รับยาแล้ว", received)
            c5.metric("🔴 ไม่อนุมัติ", rejected)
        
        col_chart, col_table = st.columns([1, 1])
        
        with col_chart:
            st.write("📈 **สัดส่วนสถานะคำขอ**")
            status_counts = df["สถานะการอนุมัติ"].value_counts()
            st.bar_chart(status_counts)
            
        with col_table:
            st.write("🏥 **โรงพยาบาลที่ขอยืมบ่อยที่สุด**")
            hosp_counts = df["โรงพยาบาลที่ขอยืม"].value_counts().reset_index()
            hosp_counts.columns = ["ชื่อโรงพยาบาล", "จำนวนครั้ง"]
            st.dataframe(hosp_counts, hide_index=True, use_container_width=True)
            
        st.divider()
        st.write("