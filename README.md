Project files are located in `bruin/nourishmama_pipeline` and `bruin/nourishmama_gcp`.

**[Live app](https://nourishmama-u.streamlit.app/)**
# 🌱 NourishMama

**Nutrition insights for first-time mums and baby-friendly foods under 1 year**

NourishMama is an end-to-end data pipeline built with **Bruin** that delivers actionable nutrition insights for **nursing mothers** and **babies under 1 year**.

It enables users to explore:
- Nutrient-rich foods by category
- Age-appropriate foods for babies (6–11 months)
- Top foods for key nutrients like Iron, Calcium, Protein, and more

---

## 🚀 Problem Statement

First-time mothers often struggle with:
- Knowing which foods support recovery and breastfeeding
- Identifying safe, nutrient-rich foods for babies at different ages

Existing resources are scattered and not data-driven.

👉 **NourishMama solves this by providing a data-driven dashboard that connects maternal nutrition and baby feeding recommendations in one place.**

---

## 🧠 What This Project Does

This project builds a complete data pipeline that:

1. Ingests nutrition data
2. Transforms it into structured, analysis-ready datasets
3. Produces analytical tables for insights
4. Powers an interactive dashboard

---

## ⚙️ Tech Stack

- **Data Platform**: Bruin
- **Cloud**: GCP
- **Infrastructure as Code**: Terraform
- **Data Lake**: Google Cloud Storage (GCS)
- **Data Warehouse**: BigQuery
- **Data Warehouse**: DuckDB
- **Transformations**: SQL + Python (Bruin assets)
- **Orchestration**: Bruin pipeline DAG
- **Dashboard**: Streamlit

---

## ☁️ Cloud Architecture

NourishMama includes a cloud pipeline built on GCP.

- **Terraform** provisions the cloud infrastructure: a **GCS bucket** for raw data storage and **BigQuery datasets** for analytics layers
- **Bruin** orchestrates ingestion and transformations across the pipeline
- **Streamlit** reads analytics-ready tables from **BigQuery** to power the dashboard

### Cloud flow

USDA FoodData Central / curated nutrition data  
→ GCS raw zone  
→ BigQuery raw tables  
→ BigQuery staging / marts / reports  
→ Streamlit dashboard

---

## 📦 Data Model

### Key Features

- `target_group`: baby | mother | both
- `is_baby_friendly`: TRUE/FALSE
- `min_age_months`, `max_age_months`
- `texture_stage` (e.g., mashed, soft, flaked)

---

## 📊 Dashboard Features

### 1️⃣ Nutrient Distribution by Category
- Shows how nutrients (e.g., Calcium, Iron) are distributed across food groups
- Helps identify **which categories are richest in nutrients**

### 2️⃣ Top Foods by Nutrient
- Ranks foods based on nutrient content
- Highlights **best food choices for mothers or babies**

---

## 🎛️ Interactive Filters

- 👶 Baby age (6–11 months)
- 👩 Audience:
  - Baby under 1
  - Mother
  - Both

---

## 📸 Dashboard Preview
![Dashboard](image_2.png)
![Dashboard](image_1.png)

---

## ▶️ How to Run the Project

### 1. Clone the repository

```bash
git clone https://github.com/kachiann/nourishmama.git
cd nourishmama
```
### 2. Create a virtual environment
```bash 
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
```

### 3. Install Python dependencies
```bash
  pip install -r bruin/nourishmama_pipeline/requirements.txt
```

### 4. Install Bruin CLI
```bash
curl -LsSf https://getbruin.com/install/cli | sh
```
```bash
export PATH="$HOME/.local/bin:$PATH"
bruin --version
```

### 5. Create Bruin connection
```bash
  bruin connections add \
  --environment default \
  --name duckdb_local \
  --type duckdb \
  --credentials '{"path":"./nourishmama.duckdb"}'
```
### 5. Run the pipeline
```bash
cd bruin
bruin run nourishmama_pipeline
```

### 3. Launch the dashboard
```bash
streamlit run nourishmama_pipeline/app1.py
```

## Cloud Quickstart: Run Cloud Pipeline (BigQuery + GCS)
Make sure you are authenticated:
```bash
gcloud auth application-default login
```

```bash
cd nourishmama/bruin
bruin run nourishmama_gcp
streamlit run nourishmama_gcp/app.py
```
