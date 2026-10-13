import streamlit as st
import pandas as pd
import plotly.express as px

from database import init_db, add_harvest, get_harvests, delete_harvest
from utils import calculate_revenue, calculate_profit

st.set_page_config(
    page_title="Garden Manager of Purichaya garden",
    page_icon="🌱",
    layout="wide",
)

init_db()

st.title("Garden Manager of Purichaya garden")
st.caption("ระบบจัดการผลผลิตในสวนภูริชญา")

page = st.sidebar.radio(
    "เมนูหลัก",
    ["ภาพรวม", "บันทึกผลผลิต", "ประวัติผลผลิต"],
)

records = get_harvests()
df = pd.DataFrame(records)

if page == "ภาพรวม":
    st.header("ภาพรวมผลผลิต")

    if df.empty:
        st.info("ยังไม่มีข้อมูลผลผลิต กรุณาไปที่เมนู 'บันทึกผลผลิต' เพื่อเพิ่มข้อมูล")
    else:
        total_items = len(df)
        total_quantity = float(df["quantity"].sum())
        total_revenue = float(df["revenue"].sum())
        total_cost = float(df["cost"].sum())
        total_profit = total_revenue - total_cost

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("จำนวนรายการ", f"{total_items:,}")
        c2.metric("ผลผลิตรวม", f"{total_quantity:,.2f}")
        c3.metric("รายรับรวม", f"{total_revenue:,.2f} บาท")
        c4.metric("กำไรเบื้องต้น", f"{total_profit:,.2f} บาท")

        st.subheader("รายรับแยกตามชนิดพืช")
        chart_data = df.groupby("crop", as_index=False)["revenue"].sum()
        fig = px.bar(
            chart_data,
            x="crop",
            y="revenue",
            labels={"crop": "ชนิดพืช", "revenue": "รายรับ (บาท)"},
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("รายการล่าสุด")
        st.dataframe(
            df.sort_values("harvest_date", ascending=False).head(10),
            use_container_width=True,
            hide_index=True,
        )

elif page == "บันทึกผลผลิต":
    st.header("บันทึกผลผลิต")
    st.write("กรอกข้อมูลตามรายการจริงของสวน")

    with st.form("harvest_form", clear_on_submit=True):
        crop = st.text_input("ชื่อพืช / ผลผลิต")
        harvest_date = st.date_input("วันที่เก็บเกี่ยว")
        quantity = st.number_input("ปริมาณผลผลิต", min_value=0.0, value=0.0, step=0.5)
        unit = st.selectbox("หน่วย", ["กิโลกรัม", "กรัม", "ผล", "มัด", "ถุง", "ลัง", "อื่น ๆ"])
        price_per_unit = st.number_input("ราคาขายต่อหน่วย (บาท)", min_value=0.0, value=0.0, step=1.0)
        cost = st.number_input("ต้นทุนของรายการนี้ (บาท)", min_value=0.0, value=0.0, step=1.0)
        note = st.text_area("หมายเหตุ (ถ้ามี)")

        submitted = st.form_submit_button("บันทึกข้อมูล", type="primary")

        if submitted:
            if not crop.strip():
                st.error("กรุณากรอกชื่อพืชหรือผลผลิต")
            elif quantity <= 0:
                st.error("ปริมาณผลผลิตต้องมากกว่า 0")
            else:
                revenue = calculate_revenue(quantity, price_per_unit)
                add_harvest(
                    crop=crop.strip(),
                    harvest_date=harvest_date.isoformat(),
                    quantity=quantity,
                    unit=unit,
                    price_per_unit=price_per_unit,
                    cost=cost,
                    revenue=revenue,
                    note=note.strip(),
                )
                st.success(f"บันทึกข้อมูล '{crop.strip()}' เรียบร้อยแล้ว")
                st.rerun()

elif page == "ประวัติผลผลิต":
    st.header("ประวัติผลผลิต")
    if df.empty:
        st.info("ยังไม่มีข้อมูลให้แสดง")
    else:
        search = st.text_input("ค้นหาตามชื่อพืช")
        filtered = df[df["crop"].str.contains(search, case=False, na=False)] if search else df

        display_df = filtered.rename(
            columns={
                "id": "รหัส",
                "crop": "ผลผลิต",
                "harvest_date": "วันที่เก็บเกี่ยว",
                "quantity": "ปริมาณ",
                "unit": "หน่วย",
                "price_per_unit": "ราคาต่อหน่วย (บาท)",
                "cost": "ต้นทุน (บาท)",
                "revenue": "รายรับ (บาท)",
                "note": "หมายเหตุ",
            }
        )
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.subheader("ลบรายการ")
        options = {
            f"รหัส {row.id} — {row.crop} ({row.harvest_date})": int(row.id)
            for row in filtered.itertuples()
        }
        if options:
            selected_label = st.selectbox("เลือกรายการที่ต้องการลบ", list(options.keys()))
            confirm = st.checkbox("ยืนยันว่าต้องการลบรายการนี้")
            if st.button("ลบรายการ", disabled=not confirm):
                delete_harvest(options[selected_label])
                st.success("ลบรายการแล้ว")
                st.rerun()
