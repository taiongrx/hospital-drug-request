import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="ระบบจัดการยืมยา/เวชภัณฑ์", layout="wide")

# จำลองฐานข้อมูลด้วยไฟล์ CSV
DB_FILE = "borrow_logs.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # สร้างโครงสร้างข้อมูลอ้างอิงจากแบบฟอร์ม
        columns = [
            "วันที่บันทึก", "ผู้ขอเบิก", "ตำแหน่ง", "ฝ่าย/กลุ่มงาน", 
            "โรงพยาบาลที่ขอยืม", "รายการที่ 1", "จำนวนที่ 1",
            "รายการที่ 2", "จำนวนที่ 2", "รายการที่ 3", "จำนวนที่ 3",
            "ต้องการใช้ภายในวันที่", "เวลา", "สถานะการอนุมัติ", "เหตุผล(กรณีไม่อนุมัติ)", "ผู้อนุมัติ"
        ]
        return pd.DataFrame(columns=columns)

def save_data(data_dict):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# เมนูนำทาง
menu = st.sidebar.selectbox("เลือกเมนูการทำงาน", ["📝 ฟอร์มขอเบิก/ยืมยา", "📊 Dashboard ติดตามสถานะ"])

if menu == "📝 ฟอร์มขอเบิก/ยืมยา":
    st.header("บันทึกข้อความขอเบิกยา/เวชภัณฑ์ไม่ใช่ยา")
    st.subheader("โรงพยาบาลสมเด็จพระยุพราชสายบุรี")
    
    with st.form("borrow_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            req_name = st.text_input("ชื่อผู้ขอเบิก")
        with col2:
            position = st.text_input("ตำแหน่ง")
        with col3:
            department = st.text_input("ฝ่าย/กลุ่มงาน")
            
        target_hospital = st.text_input("ขอสนับสนุนจากโรงพยาบาล")
        
        st.markdown("---")
        st.write("**รายการยา/เวชภัณฑ์ที่ต้องการ**")
        
        col_item1, col_qty1 = st.columns([3, 1])
        item1 = col_item1.text_input("รายการที่ 1")
        qty1 = col_qty1.number_input("จำนวน (1)", min_value=0, step=1)
        
        col_item2, col_qty2 = st.columns([3, 1])
        item2 = col_item2.text_input("รายการที่ 2")
        qty2 = col_qty2.number_input("จำนวน (2)", min_value=0, step=1)
        
        col_item3, col_qty3 = st.columns([3, 1])
        item3 = col_item3.text_input("รายการที่ 3")
        qty3 = col_qty3.number_input("จำนวน (3)", min_value=0, step=1)
        
        st.markdown("---")
        col_date, col_time = st.columns(2)
        with col_date:
            needed_date = st.date_input("ต้องการใช้ภายในวันที่")
        with col_time:
            needed_time = st.time_input("เวลา")
            
        st.markdown("---")
        st.write("**ส่วนของการอนุมัติ**")
        approval_status = st.radio("ความเห็นของผู้มีอำนาจ", ["รอพิจารณา", "อนุมัติ", "ไม่อนุมัติ"])
        reject_reason = st.text_input("หมายเหตุ/เหตุผล (กรณีไม่อนุมัติ)")
        approver = st.text_input("ชื่อผู้อนุมัติ")
        
        submitted = st.form_submit_button("บันทึกข้อมูล")
        
        if submitted:
            if not req_name or not target_hospital or not item1:
                st.error("กรุณากรอกข้อมูลที่จำเป็น (ชื่อผู้ขอ, โรงพยาบาลปลายทาง, อย่างน้อย 1 รายการ)")
            else:
                new_record = {
                    "วันที่บันทึก": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ผู้ขอเบิก": req_name,
                    "ตำแหน่ง": position,
                    "ฝ่าย/กลุ่มงาน": department,
                    "โรงพยาบาลที่ขอยืม": target_hospital,
                    "รายการที่ 1": item1, "จำนวนที่ 1": qty1,
                    "รายการที่ 2": item2, "จำนวนที่ 2": qty2,
                    "รายการที่ 3": item3, "จำนวนที่ 3": qty3,
                    "ต้องการใช้ภายในวันที่": needed_date.strftime("%Y-%m-%d"),
                    "เวลา": needed_time.strftime("%H:%M"),
                    "สถานะการอนุมัติ": approval_status,
                    "เหตุผล(กรณีไม่อนุมัติ)": reject_reason,
                    "ผู้อนุมัติ": approver
                }
                save_data(new_record)
                st.success("บันทึกข้อมูลสำเร็จ!")

elif menu == "📊 Dashboard ติดตามสถานะ":
    st.header("Dashboard ติดตามการขอยืมยา/เวชภัณฑ์")
    
    df = load_data()
    
    if df.empty:
        st.info("ยังไม่มีข้อมูลในระบบ")
    else:
        # สรุปภาพรวม (Metrics)
        total_requests = len(df)
        pending = len(df[df["สถานะการอนุมัติ"] == "รอพิจารณา"])
        approved = len(df[df["สถานะการอนุมัติ"] == "อนุมัติ"])
        rejected = len(df[df["สถานะการอนุมัติ"] == "ไม่อนุมัติ"])
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("คำขอทั้งหมด", total_requests)
        col2.metric("รอพิจารณา ⏳", pending)
        col3.metric("อนุมัติแล้ว ✅", approved)
        col4.metric("ไม่อนุมัติ ❌", rejected)
        
        st.markdown("---")
        
        # กราฟและตาราง
        col_chart, col_table = st.columns([1, 1])
        
        with col_chart:
            st.write("**สัดส่วนสถานะการอนุมัติ**")
            status_counts = df["สถานะการอนุมัติ"].value_counts()
            st.bar_chart(status_counts)
            
        with col_table:
            st.write("**โรงพยาบาลที่ขอยืมบ่อยที่สุด**")
            hosp_counts = df["โรงพยาบาลที่ขอยืม"].value_counts()
            st.dataframe(hosp_counts, use_container_width=True)
            
        st.markdown("---")
        st.write("**รายละเอียดคำขอล่าสุด**")
        # แสดงข้อมูลล่าสุด 10 รายการ
        st.dataframe(df.tail(10).sort_values("วันที่บันทึก", ascending=False), use_container_width=True)