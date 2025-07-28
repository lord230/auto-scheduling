import streamlit as st
import pandas as pd
import random
import math

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

def generate_timetable(periods_per_day, period_length, teachers):
    timetable = {day: ["Free"] * periods_per_day for day in WEEKDAYS}
    all_slots = [(day, p) for day in WEEKDAYS for p in range(periods_per_day)]
    random.shuffle(all_slots)

    for teacher in teachers:
        blocks_needed = math.ceil(teacher['minutes_per_class'] / period_length)
        total_slots_needed = teacher['classes_per_week']

        allocations = 0
        attempts = 0

        while allocations < total_slots_needed and attempts < 1000:
            attempts += 1
            day = random.choice(WEEKDAYS)
            start = random.randint(0, periods_per_day - blocks_needed)

            if all(timetable[day][start + i] == "Free" for i in range(blocks_needed)):
                label = f"{teacher['subject']} ({teacher['name']})"
                for i in range(blocks_needed):
                    timetable[day][start + i] = label
                allocations += 1

    return timetable

def timetable_to_df(timetable, periods_per_day):
    df = pd.DataFrame(columns=[f"Period {i+1}" for i in range(periods_per_day)])
    for day in WEEKDAYS:
        df.loc[day] = timetable[day]
    df.index.name = "Day"
    return df

# ================= STREAMLIT APP =================
st.set_page_config(page_title="Timetable Generator", layout="centered")

st.title("Class Timetable Generator")
school_name = st.text_input("Enter School Name:")

colA, colB = st.columns(2)
with colA:
    periods_per_day = st.number_input("Number of periods per day", min_value=1, max_value=12, value=6, step=1)
with colB:
    period_length = st.number_input("Length of each period (minutes)", min_value=15, max_value=120, value=45, step=5)

st.markdown("---")
st.subheader("Add Teachers")

teachers = []
teacher_count = st.number_input("Number of teachers", min_value=1, max_value=20, value=3)

with st.form("teacher_form"):
    for i in range(teacher_count):
        st.markdown(f"**Teacher {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Name {i+1}", key=f"name{i}")
            subject = st.text_input(f"Subject {i+1}", key=f"subject{i}")
        with col2:
            classes_per_week = st.number_input(f"Classes/Week {i+1}", min_value=1, max_value=periods_per_day * 5, key=f"cpw{i}")
            minutes_per_class = st.number_input(
                f"Class Duration (minutes) {i+1}", min_value=10, max_value=300, step=5, value=45, key=f"dur{i}"
            )
        teachers.append({
            "name": name,
            "subject": subject,
            "classes_per_week": int(classes_per_week),
            "minutes_per_class": int(minutes_per_class)
        })

    submitted = st.form_submit_button("Generate Timetable")

if submitted:
    if school_name.strip() == "":
        st.warning("Please enter the school name.")
    elif any(t['name'] == "" or t['subject'] == "" for t in teachers):
        st.warning("Please fill all teacher names and subjects.")
    else:
        timetable = generate_timetable(periods_per_day, period_length, teachers)
        df = timetable_to_df(timetable, periods_per_day)

        st.success(f"Timetable for **{school_name}** generated!")
        st.markdown(f"###  {school_name} Weekly Timetable")
        st.dataframe(df, use_container_width=True)

        # CSV Download
        csv = df.to_csv().encode('utf-8')
        st.download_button("Download CSV", csv, file_name=f"{school_name}_timetable.csv", mime='text/csv')
