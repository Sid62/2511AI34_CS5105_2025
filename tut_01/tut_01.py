import streamlit as st
import pandas as pd
import math
import zipfile
import io
from datetime import datetime

st.set_page_config(page_title="Student Grouping", page_icon="👥")

# split by branch 
def split_by_branch(df):
    branches = sorted(df["Branch"].unique())
    branch_data = {}
    branch_files = {}
    for branch in branches:
        students = df[df["Branch"] == branch].copy().sort_values("Roll").reset_index(drop=True)
        branch_data[branch] = students
        csv_buffer = io.StringIO()
        students.to_csv(csv_buffer, index=False)
        branch_files[f"{branch}.csv"] = csv_buffer.getvalue()
    return branch_data, branch_files, branches

# make branchwise group
def make_branchwise_groups(branch_data, branches, n_groups):
    groups = [pd.DataFrame(columns=['Roll', 'Name', 'Email', 'Branch']) for _ in range(n_groups)]
    branch_index = {b: 0 for b in branches}
    total_students = sum(len(branch_data[b]) for b in branches)
    target_size = math.ceil(total_students / n_groups)

    for g in range(n_groups):
        while len(groups[g]) < target_size:
            added = False
            for b in branches:
                if branch_index[b] < len(branch_data[b]):
                    row = branch_data[b].iloc[branch_index[b]]
                    groups[g] = pd.concat([groups[g], row.to_frame().T], ignore_index=True)
                    branch_index[b] += 1
                    added = True
                    if len(groups[g]) >= target_size:
                        break
            if not added:  # agar aur student bacha hi nahi
                break
    return groups


# Uniform mix groups
def make_uniform_groups(branch_data, branches, n_groups):
    total_students = sum(len(branch_data[b]) for b in branches)
    group_size = math.ceil(total_students / n_groups)
    branch_counts = {b: len(branch_data[b]) for b in branches}
    sorted_branches = sorted(branches, key=lambda x: branch_counts[x], reverse=True)

    groups = [pd.DataFrame(columns=['Roll', 'Name', 'Email', 'Branch']) for _ in range(n_groups)]
    g = 0
    for b in sorted_branches:
        students = branch_data[b].copy()
        idx = 0
        while idx < len(students):
            available = group_size - len(groups[g])
            take = min(available, len(students) - idx)
            for i in range(take):
                row = students.iloc[idx + i]
                groups[g] = pd.concat([groups[g], row.to_frame().T], ignore_index=True)
            idx += take
            if len(groups[g]) >= group_size:
                g = (g + 1) % n_groups
    return groups


def groups_to_files(groups):
    files = {}
    stats = []
    for i, g in enumerate(groups, 1):
        if not g.empty:
            sorted_g = g.sort_values(['Branch', 'Roll']).reset_index(drop=True)
            csv_buffer = io.StringIO()
            sorted_g.to_csv(csv_buffer, index=False)
            files[f"G{i}.csv"] = csv_buffer.getvalue()

            # count for stats
            counts = sorted_g["Branch"].value_counts().to_dict()
            counts["Total"] = len(sorted_g)
            counts["Group"] = f"G{i}"
            stats.append(counts)
    return files, stats

# Combined_Stats
def make_stats(branchwise_stats, uniform_stats, branches):
    bw = pd.DataFrame(branchwise_stats).fillna(0).astype({col:int for col in branches+["Total"]})
    um = pd.DataFrame(uniform_stats).fillna(0).astype({col:int for col in branches+["Total"]})
    output = []
    output.append(",".join(["Group"]+branches+["Total"]))
    for _, row in bw.iterrows():
        output.append(",".join(map(str,[row["Group"]]+[row[b] for b in branches]+[row["Total"]])))
    output.append("")  # ek blank line
    output.append(",".join(["Group"]+branches+["Total"]))
    for _, row in um.iterrows():
        output.append(",".join(map(str,[row["Group"]]+[row[b] for b in branches]+[row["Total"]])))
    return "\n".join(output)


def make_zip(branch_files, branchwise_files, uniform_files, stats):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fn,c in branch_files.items():
            z.writestr(f"Branch_Full_List/{fn}", c)
        for fn,c in branchwise_files.items():
            z.writestr(f"Branchwise_Mix/{fn}", c)
        for fn,c in uniform_files.items():
            z.writestr(f"Uniform_Mix/{fn}", c)
        z.writestr("Combined_Stats.csv", stats)
    buf.seek(0)
    return buf

# Streamlit App (UI)
st.title("Auto Student Grouper")

file = st.file_uploader("Upload CSV file(Roll, Name, Email)", type=["csv"])
n = st.number_input("Number of Groups", min_value=1, max_value=50, value=5, step=1)

if file and st.button("Proceed"):
    df = pd.read_csv(file)

    if not all(col in df.columns for col in ["Roll","Name","Email"]):
        st.error("CSV must have Roll, Name, Email columns")
        st.stop()

    df["Branch"] = df["Roll"].astype(str).str[4:6]

    branch_data, branch_files, branches = split_by_branch(df)

    bw_groups = make_branchwise_groups(branch_data, branches, n)
    bw_files, bw_stats = groups_to_files(bw_groups)

    uni_groups = make_uniform_groups(branch_data, branches, n)
    uni_files, uni_stats = groups_to_files(uni_groups)

    combined_stats = make_stats(bw_stats, uni_stats, branches)

    zipbuf = make_zip(branch_files, bw_files, uni_files, combined_stats)

    st.download_button(
        "Download All Groups (ZIP)",
        data=zipbuf,
        file_name=f"Student_Groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
        mime="application/zip"
    )
