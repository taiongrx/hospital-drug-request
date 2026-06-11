import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import json 

# ==========================================
# 🔑 ตั้งค่า LINE Messaging API (LINE OA)
# ==========================================
# 1. นำ Channel Access Token (ยาวๆ) มาใส่ในเครื่องหมายคำพูดด้านล่าง
CHANNEL_ACCESS_TOKEN = "ubOQt7lYRoszvumGqPEkrIFAcA3RK9JqA4Qkq5SIcTvvv+wa4R4zUVfOqHRNDyLOaY6HYuSSkebXXcy5I8v2xeD18rAagMn1pA/Zq9nZQVzRVeu0gTWbTiYTU+InhTXLh2hldYxI8tCu88PxwhBHHQdB04t89/1O/w1cDnyilFU="

# 2. User ID (ตั้งค่าให้แล้ว)
TARGET_USER_ID = "C1780c21bdcd9af527f4fe49d96358968"

# ฟังก์ชันสำหรับส่งข้อความผ่าน LINE OA
def send_line_oa_message(message_text):
    if CHANNEL_ACCESS_TOKEN == "ใส่_Channel_Access_Token_ยาวๆ_ตรงนี้" or not CHANNEL_ACCESS_TOKEN:
        return False 
        
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": TARGET_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message_text
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        return response.status_code == 200
    except:
        return False

# ==========================================
# ส่วนของการตั้งค่าระบบและฐานข้อมูล
# ==========================================
st.set_page_config(
    page_title="ระบบจัดการยืมยา/เวชภัณฑ์", 
    page_icon="💊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "borrow_logs.csv"

STATUS_COLORS = {
    "รอพิจารณา": "🟠 รอพิจารณา",
    "รอยา": "🔵 รอยา",
    "รับยาแล้ว": "🟢 รับยาแล้ว",
    "ไม่อนุมัติ": "🔴 ไม่อนุมัติ"
}

# รายการหน่วยนับมาตรฐาน
UNIT_OPTIONS = ["เม็ด", "ขวด", "กล่อง", "ชิ้น", "แผง", "หลอด", "vial", "ampoule", "ซอง", "ม้วน", "อื่นๆ", "-"]

def load_data():
    # เพิ่มคอลัมน์ "หน่วย" เข้ามาในฐานข้อมูล
    expected_columns = [
        "รหัสคำขอ", "วันที่บันทึก", "ผู้ขอเบิก", "ตำแหน่ง", "ฝ่าย/กลุ่มงาน", 
        "โรงพยาบาลที่ขอยืม", "รายการที่ 1", "จำนวนที่ 1", "หน่วยที่ 1",
        "รายการที่ 2", "จำนวนที่ 2", "หน่วยที่ 2",
        "รายการที่ 3", "จำนวนที่ 3", "หน่วยที่ 3",
        "ต้องการใช้ภายในวันที่", "เวลา", "สถานะการอนุมัติ", "เหตุผล(กรณีไม่อนุมัติ)", "ผู้อนุมัติ"
    ]
    
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # ตรวจสอบและเติมคอลัมน์ที่ขาดหายไป (กรณีดึงข้อมูลเก่ามาใช้)
        for col in expected_columns:
            if col not in df.columns:
                if col == "รหัสคำขอ":
                    df[col] = [f"REQ-OLD-{i+1}" for i in range(len(df))]
                elif "หน่วย" in col:
                    df[col] = "เม็ด" # ค่าเริ่มต้นสำหรับข้อมูลเก่า
                else:
                    df[col] = "-"
        return df
    else:
        return pd.DataFrame(columns=expected_columns)

def save_new_request(data_dict):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def update_request(req_id, new_status, reject_reason, approver):
    df = load_data()
    df['สถานะการอนุมัติ'] = df['สถานะการอนุมัติ'].astype('object')
    df['เหตุผล(กรณีไม่อนุมัติ)'] = df['เหตุผล(กรณีไม่อนุมัติ)'].astype('object')
    df['ผู้อนุมัติ'] = df['ผู้อนุมัติ'].astype('object')
    
    idx = df.index[df['รหัสคำขอ'] == req_id].tolist()
    if idx:
        df.at[idx[0], 'สถานะการอนุมัติ'] = new_status
        df.at[idx[0], 'เหตุผล(กรณีไม่อนุมัติ)'] = reject_reason
        df.at[idx[0], 'ผู้อนุมัติ'] = approver
        df.to_csv(DB_FILE, index=False)
        return True
    return False

def edit_request_details(req_id, updated_data):
    df = load_data()
    for col in df.columns:
        df[col] = df[col].astype('object')
        
    idx = df.index[df['รหัสคำขอ'] == req_id].tolist()
    if idx:
        for key, val in updated_data.items():
            df.at[idx[0], key] = val
        df.to_csv(DB_FILE, index=False)
        return True
    return False

def delete_request(req_id):
    df = load_data()
    df = df[df['รหัสคำขอ'] != req_id]
    df.to_csv(DB_FILE, index=False)
    return True

def get_unit_index(unit_val):
    if pd.isna(unit_val) or unit_val not in UNIT_OPTIONS:
        return 0
    return UNIT_OPTIONS.index(unit_val)

# ==========================================
# ตกแต่ง Sidebar
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100)
    st.title("ระบบยืม-คืนยา")
    st.markdown("โรงพยาบาลสมเด็จพระยุพราชสายบุรี")
    st.divider()
    menu = st.radio("📌 เมนูการทำงาน", [
        "📝 ฟอร์มขอเบิก/ยืมยา", 
        "👨‍⚕️ จัดการคำขอและอนุมัติ", 
        "📊 Dashboard ติดตามสถานะ"
    ])

# ==========================================
# เมนูที่ 1: สำหรับผู้ขอเบิก
# ==========================================
if menu == "📝 ฟอร์มขอเบิก/ยืมยา":
    st.header("📝 บันทึกข้อความขอเบิกยา/เวชภัณฑ์ไม่ใช่ยา")
    st.caption("กรอกข้อมูลให้ครบถ้วนเพื่อความรวดเร็วในการพิจารณาอนุมัติ")
    
    with st.form("borrow_form", clear_on_submit=True):
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
            
            # ปรับ Layout ให้มีช่องเลือกหน่วย (แบ่งความกว้างเป็น 2:1:1)
            c_item1, c_qty1, c_unit1 = st.columns([2, 1, 1])
            item1 = c_item1.text_input("รายการที่ 1 *")
            qty1 = c_qty1.number_input("จำนวน (1)", min_value=0, step=1)
            unit1 = c_unit1.selectbox("หน่วย (1)", UNIT_OPTIONS, key="u1")
            
            c_item2, c_qty2, c_unit2 = st.columns([2, 1, 1])
            item2 = c_item2.text_input("รายการที่ 2")
            qty2 = c_qty2.number_input("จำนวน (2)", min_value=0, step=1)
            unit2 = c_unit2.selectbox("หน่วย (2)", UNIT_OPTIONS, key="u2", index=UNIT_OPTIONS.index("-"))
            
            c_item3, c_qty3, c_unit3 = st.columns([2, 1, 1])
            item3 = c_item3.text_input("รายการที่ 3")
            qty3 = c_qty3.number_input("จำนวน (3)", min_value=0, step=1)
            unit3 = c_unit3.selectbox("หน่วย (3)", UNIT_OPTIONS, key="u3", index=UNIT_OPTIONS.index("-"))

        with st.container(border=True):
            st.markdown("#### ⏰ ส่วนที่ 3: กำหนดเวลาที่ต้องใช้")
            col_date, col_time = st.columns(2)
            with col_date:
                needed_date = st.date_input("ต้องการใช้ภายในวันที่")
            with col_time:
                needed_time = st.time_input("เวลา")
            
        col_blank, col_btn = st.columns([4, 1])
        with col_btn:
            submitted = st.form_submit_button("ส่งคำขอ 📤", use_container_width=True)
        
        if submitted:
            if not req_name or not target_hospital or not item1 or not department:
                st.error("⚠️ กรุณากรอกข้อมูลที่มีเครื่องหมาย * ให้ครบถ้วน")
            else:
                req_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                formatted_date = needed_date.strftime("%Y-%m-%d")
                
                # บันทึกข้อมูลรวม "หน่วย"
                new_record = {
                    "รหัสคำขอ": req_id,
                    "วันที่บันทึก": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "ผู้ขอเบิก": req_name,
                    "ตำแหน่ง": position,
                    "ฝ่าย/กลุ่มงาน": department,
                    "โรงพยาบาลที่ขอยืม": target_hospital,
                    "รายการที่ 1": item1, "จำนวนที่ 1": qty1, "หน่วยที่ 1": unit1,
                    "รายการที่ 2": item2, "จำนวนที่ 2": qty2, "หน่วยที่ 2": unit2 if item2 else "-",
                    "รายการที่ 3": item3, "จำนวนที่ 3": qty3, "หน่วยที่ 3": unit3 if item3 else "-",
                    "ต้องการใช้ภายในวันที่": formatted_date,
                    "เวลา": needed_time.strftime("%H:%M"),
                    "สถานะการอนุมัติ": "รอพิจารณา",
                    "เหตุผล(กรณีไม่อนุมัติ)": "-",
                    "ผู้อนุมัติ": "-"
                }
                save_new_request(new_record)
                
                msg = f"🚨 มีคำขอยืมยาใหม่!\n\nรหัส: {req_id}\nผู้ขอ: {req_name} ({department})\nขอยืมจาก: {target_hospital}\nรายการหลัก: {item1} (จำนวน {qty1} {unit1})\nต้องการใช้ภายใน: {formatted_date}"
                send_line_oa_message(msg)
                
                st.success(f"✅ ส่งคำขอสำเร็จ! รหัสอ้างอิง: **{req_id}**")

# ==========================================
# เมนูที่ 2: จัดการคำขอและอนุมัติ
# ==========================================
elif menu == "👨‍⚕️ จัดการคำขอและอนุมัติ":
    st.header("👨‍⚕️ หน้าต่างจัดการและพิจารณาอนุมัติคำขอ")
    
    df = load_data()
    if df.empty:
        st.info("ไม่มีข้อมูลคำขอในระบบ")
    else:
        st.subheader("📋 รายการคำขอทั้งหมดในระบบ")
        display_all = df.copy()
        display_all["สถานะ"] = display_all["สถานะการอนุมัติ"].map(STATUS_COLORS)
        st.dataframe(display_all[["รหัสคำขอ", "ผู้ขอเบิก", "ฝ่าย/กลุ่มงาน", "โรงพยาบาลที่ขอยืม", "สถานะ"]], hide_index=True, use_container_width=True)
        
        st.divider()
        st.subheader("🛠️ เครื่องมือจัดการคำขอ")
        
        all_req_list = df["รหัสคำขอ"].tolist()
        
        def format_req_choice(req_id):
            if req_id == "-- กรุณาเลือกรหัสคำขอ --":
                return "👇 คลิกเพื่อค้นหา หรือเลือกคำขอที่ต้องการ..."
            
            row = df[df["รหัสคำขอ"] == req_id].iloc[0]
            status = row["สถานะการอนุมัติ"]
            icon = "🟢" if status == "รับยาแล้ว" else "🔵" if status == "รอยา" else "🔴" if status == "ไม่อนุมัติ" else "🟠"
            
            return f"{icon} {req_id} | ผู้ขอ: {row['ผู้ขอเบิก']} | ยาหลัก: {row['รายการที่ 1']}"

        selected_req = st.selectbox(
            "🔍 พิมพ์ค้นหา หรือเลือกรายการที่ต้องการดำเนินการ", 
            ["-- กรุณาเลือกรหัสคำขอ --"] + all_req_list,
            format_func=format_req_choice
        )
        
        if selected_req != "-- กรุณาเลือกรหัสคำขอ --":
            selected_data = df[df["รหัสคำขอ"] == selected_req].iloc[0]
            
            tab_approve, tab_edit, tab_delete = st.tabs([
                "📥 1. อัปเดตสถานะอนุมัติ", 
                "✏️ 2. แก้ไขรายละเอียดคำขอ", 
                "❌ 3. ลบคำขอออกจากระบบ"
            ])
            
            # --- TAB 1: พิจารณาอนุมัติ ---
            with tab_approve:
                st.markdown("#### เปลี่ยนแปลงสถานะการดำเนินงาน")
                with st.form("approval_form"):
                    col_stat, col_name = st.columns(2)
                    with col_stat:
                        new_status = st.selectbox(
                            "อัปเดตสถานะเป็น", 
                            ["รอพิจารณา", "รอยา", "รับยาแล้ว", "ไม่อนุมัติ"],
                            index=["รอพิจารณา", "รอยา", "รับยาแล้ว", "ไม่อนุมัติ"].index(selected_data["สถานะการอนุมัติ"])
                        )
                    with col_name:
                        approver_name = st.text_input("ชื่อเภสัชกรผู้ดำเนินการ *", value=selected_data["ผู้อนุมัติ"] if selected_data["ผู้อนุมัติ"] != "-" else "")
                        
                    reject_reason = st.text_input("หมายเหตุ / เหตุผลกรณีไม่อนุมัติ", value=selected_data["เหตุผล(กรณีไม่อนุมัติ)"])
                    
                    update_btn = st.form_submit_button("💾 บันทึกการอัปเดตสถานะ", use_container_width=True)
                    if update_btn:
                        if not approver_name:
                            st.error("⚠️ กรุณาระบุชื่อเภสัชกรผู้ดำเนินการ")
                        elif new_status == "ไม่อนุมัติ" and (reject_reason == "-" or not reject_reason):
                            st.error("⚠️ กรุณาระบุเหตุผลกรณีไม่อนุมัติ")
                        else:
                            if update_request(selected_req, new_status, reject_reason, approver_name):
                                
                                status_icon = "🟢" if new_status == "รับยาแล้ว" else "🔵" if new_status == "รอยา" else "🔴" if new_status == "ไม่อนุมัติ" else "🟠"
                                note_msg = f"\nหมายเหตุ: {reject_reason}" if reject_reason != "-" else ""
                                
                                # แสดงรายการยา จำนวน พร้อมหน่วย
                                med_list = f"{selected_data['รายการที่ 1']} (จำนวน {selected_data['จำนวนที่ 1']} {selected_data['หน่วยที่ 1']})"
                                if pd.notna(selected_data['รายการที่ 2']) and str(selected_data['รายการที่ 2']).strip() not in ["", "-", "None"]:
                                    med_list += f"\n- {selected_data['รายการที่ 2']} (จำนวน {selected_data['จำนวนที่ 2']} {selected_data['หน่วยที่ 2']})"
                                if pd.notna(selected_data['รายการที่ 3']) and str(selected_data['รายการที่ 3']).strip() not in ["", "-", "None"]:
                                    med_list += f"\n- {selected_data['รายการที่ 3']} (จำนวน {selected_data['จำนวนที่ 3']} {selected_data['หน่วยที่ 3']})"
                                
                                msg = f"🔄 อัปเดตสถานะคำขอ\n\nรหัส: {selected_req}\nผู้ขอ: {selected_data['ผู้ขอเบิก']}\n\n💊 รายการยาที่ขอยืม:\n- {med_list}\n\nสถานะใหม่: {status_icon} {new_status}\nผู้ดำเนินการ: {approver_name}{note_msg}"
                                send_line_oa_message(msg)
                                
                                st.success("✅ อัปเดตสถานะเรียบร้อยแล้ว")
                                st.rerun()

            # --- TAB 2: แก้ไขข้อมูลต้นฉบับ ---
            with tab_edit:
                st.markdown("#### แก้ไขเนื้อหาคำขอเบิก/ยืมยา")
                with st.form("edit_details_form"):
                    col_e1, col_e2, col_e3 = st.columns(3)
                    with col_e1:
                        e_name = st.text_input("ชื่อผู้ขอเบิก", value=selected_data["ผู้ขอเบิก"])
                    with col_e2:
                        e_pos = st.text_input("ตำแหน่ง", value=selected_data["ตำแหน่ง"])
                    with col_e3:
                        e_dept = st.text_input("ฝ่าย/กลุ่มงาน", value=selected_data["ฝ่าย/กลุ่มงาน"])
                        
                    e_hosp = st.text_input("ขอสนับสนุนจากโรงพยาบาล", value=selected_data["โรงพยาบาลที่ขอยืม"])
                    
                    st.markdown("##### รายการยาที่ต้องการแก้ไข")
                    
                    col_i1, col_q1, col_u1 = st.columns([2, 1, 1])
                    e_item1 = col_i1.text_input("รายการที่ 1", value=selected_data["รายการที่ 1"])
                    e_qty1 = col_q1.number_input("จำนวน (1)", value=int(selected_data["จำนวนที่ 1"]), min_value=0, step=1)
                    e_unit1 = col_u1.selectbox("หน่วย (1)", UNIT_OPTIONS, index=get_unit_index(selected_data.get("หน่วยที่ 1", "เม็ด")), key="eu1")
                    
                    col_i2, col_q2, col_u2 = st.columns([2, 1, 1])
                    e_item2 = col_i2.text_input("รายการที่ 2", value=str(selected_data["รายการที่ 2"]) if pd.notna(selected_data["รายการที่ 2"]) else "")
                    e_qty2 = col_q2.number_input("จำนวน (2)", value=int(selected_data["จำนวนที่ 2"]) if pd.notna(selected_data["จำนวนที่ 2"]) and str(selected_data["จำนวนที่ 2"]) != "-" else 0, min_value=0, step=1)
                    e_unit2 = col_u2.selectbox("หน่วย (2)", UNIT_OPTIONS, index=get_unit_index(selected_data.get("หน่วยที่ 2", "-")), key="eu2")
                    
                    col_i3, col_q3, col_u3 = st.columns([2, 1, 1])
                    e_item3 = col_i3.text_input("รายการที่ 3", value=str(selected_data["รายการที่ 3"]) if pd.notna(selected_data["รายการที่ 3"]) else "")
                    e_qty3 = col_q3.number_input("จำนวน (3)", value=int(selected_data["จำนวนที่ 3"]) if pd.notna(selected_data["จำนวนที่ 3"]) and str(selected_data["จำนวนที่ 3"]) != "-" else 0, min_value=0, step=1)
                    e_unit3 = col_u3.selectbox("หน่วย (3)", UNIT_OPTIONS, index=get_unit_index(selected_data.get("หน่วยที่ 3", "-")), key="eu3")
                    
                    try:
                        default_date = datetime.strptime(selected_data["ต้องการใช้ภายในวันที่"], "%Y-%m-%d").date()
                    except:
                        default_date = datetime.now().date()
                        
                    e_date = st.date_input("แก้ไขวันที่ต้องการใช้", value=default_date)
                    
                    save_edit_btn = st.form_submit_button("✏️ บันทึกการแก้ไขข้อมูลคำขอ", use_container_width=True)
                    if save_edit_btn:
                        updated_fields = {
                            "ผู้ขอเบิก": e_name,
                            "ตำแหน่ง": e_pos,
                            "ฝ่าย/กลุ่มงาน": e_dept,
                            "โรงพยาบาลที่ขอยืม": e_hosp,
                            "รายการที่ 1": e_item1, "จำนวนที่ 1": e_qty1, "หน่วยที่ 1": e_unit1,
                            "รายการที่ 2": e_item2, "จำนวนที่ 2": e_qty2, "หน่วยที่ 2": e_unit2,
                            "รายการที่ 3": e_item3, "จำนวนที่ 3": e_qty3, "หน่วยที่ 3": e_unit3,
                            "ต้องการใช้ภายในวันที่": e_date.strftime("%Y-%m-%d")
                        }
                        if edit_request_details(selected_req, updated_fields):
                            st.success("🎉 แก้ไขรายละเอียดข้อมูลสำเร็จ!")
                            st.rerun()

            # --- TAB 3: ลบข้อมูลออกจากระบบ ---
            with tab_delete:
                st.markdown("#### ⚠️ เขตอันตราย: ลบรายการข้อมูล")
                st.warning(f"คุณกำลังจะทำการลบคำขอรหัส {selected_req} ของคุณ {selected_data['ผู้ขอเบิก']} ออกจากระบบอย่างถาวร ข้อมูลนี้จะไม่สามารถกู้คืนได้")
                
                confirm_delete = st.checkbox("ฉันยืนยันว่าต้องการลบข้อมูลคำขอนี้จริง")
                
                delete_btn = st.button("🗑️ ลบคำขอนี้ทันที", type="primary", disabled=not confirm_delete, use_container_width=True)
                if delete_btn and confirm_delete:
                    if delete_request(selected_req):
                        st.success("🗑️ ลบข้อมูลออกจากระบบเรียบร้อยแล้ว")
                        st.rerun()

# ==========================================
# เมนูที่ 3: Dashboard ติดตามสถานะ
# ==========================================
elif menu == "📊 Dashboard ติดตามสถานะ":
    st.header("📊 Dashboard ภาพรวมการยืม-คืนยา")
    
    df = load_data()
    if df.empty:
        st.info("ยังไม่มีข้อมูลในระบบ")
    else:
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
        st.write("🗂️ **ฐานข้อมูลคำขอทั้งหมด**")
        
        display_all = df.copy()
        display_all["สถานะการอนุมัติ"] = display_all["สถานะการอนุมัติ"].map(STATUS_COLORS)
        
        # จัดตารางใหม่ให้ดูง่ายและซ่อนข้อมูลคอลัมน์ลึกๆ 
        display_cols = ["รหัสคำขอ", "วันที่บันทึก", "ผู้ขอเบิก", "โรงพยาบาลที่ขอยืม", "รายการที่ 1", "จำนวนที่ 1", "หน่วยที่ 1", "สถานะการอนุมัติ"]
        st.dataframe(display_all[display_cols].sort_values("วันที่บันทึก", ascending=False), hide_index=True, use_container_width=True)