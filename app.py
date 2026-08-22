import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

users = pd.read_csv(BASE_DIR /"users.csv")
courses = pd.read_csv(BASE_DIR /"courses.csv")
transactions = pd.read_csv(BASE_DIR /"transactions.csv")
teachers = pd.read_csv(BASE_DIR /"teachers.csv")

# users = pd.read_csv(BASE_DIR / "data" / "users.csv")
# courses = pd.read_csv(BASE_DIR / "data" / "courses.csv")
# transactions = pd.read_csv(BASE_DIR / "data" / "transactions.csv")
# teachers = pd.read_csv(BASE_DIR / "data" / "teachers.csv")

st.title("📈EduPro Learner Analytics")

#Merge all the dataset-------------------------------
merge=pd.merge(users,transactions,on="UserID",how="inner")
complete_merge=pd.merge(merge,courses,on="CourseID",how="inner")

#Grouping by ages------------------------------------
bins = [0, 17, 25, 35, 45, float("inf")]

labels = [
    "<18",
    "18–25",
    "26–35",
    "36–45",
    "45+"
]

complete_merge["AgeGroup"] = pd.cut(
    complete_merge["Age"],
    bins=bins,
    labels=labels,
    right=True
)

#Sidebar Filters---------------------------------
st.sidebar.title("Filters")
#AgeGroup
selected_age = st.sidebar.multiselect(
    "Age Group",
    options=complete_merge["AgeGroup"].dropna().unique()
)
#Course Level
selected_level = st.sidebar.multiselect(
    "Course Level",
    options=complete_merge["CourseLevel"].dropna().unique()
)#Course Category
selected_category = st.sidebar.multiselect(
    "Course Category",
    options=complete_merge["CourseCategory"].dropna().unique()
)#Gender
selected_gender = st.sidebar.multiselect(
    "Gender",
    options=complete_merge["Gender"].dropna().unique()
)

#applying filters 
filtered_df = complete_merge.copy()

if selected_age:
    filtered_df = filtered_df[
        filtered_df["AgeGroup"].isin(selected_age)
    ]

if selected_gender:
    filtered_df = filtered_df[
        filtered_df["Gender"].isin(selected_gender)
    ]

if selected_category:
    filtered_df = filtered_df[
        filtered_df["CourseCategory"].isin(selected_category)
    ]

if selected_level:
    filtered_df = filtered_df[
        filtered_df["CourseLevel"].isin(selected_level)
    ]
#KPI's-----------------------------------
col1,col2,col3,col4=st.columns([1.5,1.7,1.5,2,])

col1.metric("📝Total Learners",f"{filtered_df["UserID"].nunique()}")

col2.metric("🎯Total Enrollments",f"{filtered_df["TransactionID"].nunique()}")

col3.metric("🛠Total Courses",f"{filtered_df["CourseID"].nunique()}")

col4.metric("🎓Average Courses Per Learner",f"{round(filtered_df.groupby("UserID")["CourseID"].nunique().mean(),2)}")

#Learner Demographics-------------------------------------------
st.subheader("---------------Learner Demographics---------------")
col1, col2 = st.columns([1, 1])

with col1:
    age_distribution = (
        filtered_df.groupby("AgeGroup", observed=True)["UserID"]
        .nunique()
        .reindex(labels)
        .reset_index(name="Learners")
    )

    fig_age = px.bar(
        age_distribution,
        x="AgeGroup",
        y="Learners",
        title="Age Distribution of Learners",
        text="Learners"
    )

    fig_age.update_layout(
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(
        fig_age,
        use_container_width=True
    )

with col2:
    gen_distribution = (
        filtered_df.groupby("Gender")["UserID"]
        .nunique()
        .reset_index(name="Learners")
    )

    fig_gender = px.pie(
        gen_distribution,
        names="Gender",
        values="Learners",
        title="Gender Distribution of Learners",
        hole=0.35
    )

    fig_gender.update_layout(
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(
        fig_gender,
        use_container_width=True
    )

#Enrollment Behaviour--------------------------------------------
st.subheader("-----------Enrollment Behaviour-----------")
col1, col2 = st.columns([1, 1])
with col1:
    age_distribution_enrol = (
        filtered_df.groupby(
        "AgeGroup",observed=True)["TransactionID"]
        .nunique()
        .reindex(labels)
        .reset_index(name="Enrollments")
    )

    # st.markdown("Age Distribution in Enrollments")

    fig_age = px.bar(
        age_distribution_enrol,
        x="AgeGroup",
        y="Enrollments",
        title="Age Distribution in Enrollments",
        text="Enrollments"
    )

    fig_age.update_traces(
        textposition="outside"
    )

    fig_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Number of Enrollments"
    )

    st.plotly_chart(
        fig_age,
        use_container_width=True
    )

with col2:

    category_popularity = (
        filtered_df.groupby("CourseCategory")["TransactionID"]
        .nunique()
        .sort_values(ascending=True)
        .reset_index(name="Enrollments")
    )

    # st.markdown("Course Category Popularity")

    fig_category = px.bar(
        category_popularity,
        x="Enrollments",
        y="CourseCategory",
        orientation="h",
        title="Course Category Popularity",
        labels={
            "Enrollments": "Number of Enrollments",
            "CourseCategory": "Course Category"
        },
        text="Enrollments"
    )

    fig_category.update_traces(
        textposition="outside"
    )

    fig_category.update_layout(
        yaxis_title="Course Category",
        xaxis_title="Number of Enrollments"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )
#Preference analysis----------------------------------
age_category = (
    filtered_df.groupby(
        ["AgeGroup", "CourseCategory"],
        observed=True
    )["TransactionID"]
    .nunique()
    .reset_index(name="Enrollments")
)

fig = px.density_heatmap(
    age_category,
    x="AgeGroup",
    y="CourseCategory",
    z="Enrollments",
    title="Age Group vs Course Category",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

#----------------------------------------------
level_distribution = (
    filtered_df.groupby("CourseLevel")["TransactionID"]
    .nunique()
    .reset_index(name="Enrollments")
)

fig = px.bar(
    level_distribution,
    x="CourseLevel",
    y="Enrollments",
    title="Course Level Preference",
    text="Enrollments"
)

st.plotly_chart(fig, use_container_width=True)