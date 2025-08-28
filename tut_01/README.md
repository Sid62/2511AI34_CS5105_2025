# 🎓 Auto Student Grouper

This project is a **Streamlit web app** that automatically creates balanced student groups from a CSV file.  
It supports both **branchwise grouping** and **uniform mixing** of students, and generates a downloadable ZIP file with all group CSVs and summary stats.

---

## 🚀 Features
- Upload a CSV file containing student details (`Roll`, `Name`, `Email`).
- Automatically extracts **Branch** info from the `Roll` number.
- Two grouping modes:
  - **Branchwise Mix** → keeps branch balance in groups.
  - **Uniform Mix** → evenly distributes students.
- Generates:
  - Branch-wise student lists
  - Groups in both modes
  - Combined statistics (CSV)
- Download everything in **one ZIP file**.

---

## 📂 Input Format
Your CSV file must have these columns:

| Roll      | Name         | Email              |
|-----------|--------------|--------------------|
| 123456789 | John Doe     | john@example.com   |
| 123456790 | Jane Smith   | jane@example.com   |

👉 Branch is automatically derived from digits **[4:6]** of the Roll number.

---

## ⚙️ Installation & Run

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/auto-student-grouper.git
   cd auto-student-grouper
