# 💰 The Quick Win Generator

## AI-Powered Cloud Cost Savings Demo

An interactive Python Streamlit application that simulates cloud infrastructure analysis and calculates real savings opportunities with dynamic, real-time visualization.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo
streamlit run app.py
```

Or use the automated script:

```bash
./run.sh
```

Demo opens at `http://localhost:8501`

---

## 🎯 What This Demo Does

This is a **working demo** with real calculations:

1. **Simulates** realistic cloud infrastructure (2,847 EC2 instances, 156 TB storage)
2. **Scans** each category in real-time with live progress
3. **Discovers** optimization opportunities by team, resource type, and region
4. **Calculates** actual savings using real pricing formulas
5. **Visualizes** results with interactive charts

---

## 🔍 Dynamic Analysis Phases

### Phase 1: Infrastructure Discovery
- Scans 12 AWS regions one by one
- Identifies spot-compatible instances
- Detects idle capacity by region
- Groups by environment (production, staging, dev, test)

### Phase 2: Storage Pattern Analysis
- Analyzes by data type (logs, backups, media, data-lake, ml-models)
- Identifies stale data (90+ days not accessed)
- Shows optimization candidates per category

### Phase 3: Cross-Cloud Duplicate Detection
- Scans by team (data-science, backend, frontend, ml-ops)
- Shows duplicates found per team with waste calculation
- Identifies resource type breakdowns

### Phase 4: ML Model Registry Audit
- Audits each model with version counts
- Shows active vs prunable versions
- Calculates storage reclaim per framework

---

## 📊 Quick Win Recommendations

| Opportunity | Monthly Savings | Risk | Timeline |
|-------------|----------------|------|----------|
| Spot Instance Migration | ~$3.2M | Low | 2 hours |
| Storage Lifecycle | ~$1.1M | None | 1 day |
| Cross-Cloud Dedup | ~$890K | Low | 1 week |
| Model Registry | ~$1.5M | Medium | 2 weeks |

*Actual values calculated in real-time from simulated data*

---

## 💎 ROI Calculator

Interactive sliders to model:
- **Investment**: $1M - $10M
- **Payback Period**: Calculated in days
- **3-Year NPV**: Using 10% discount rate
- **First Year ROI**: Percentage return

---

## 📁 Project Structure

```
.
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── run.sh                # Quick start script
├── README.md             # This file
├── QUICKSTART.md         # 60-second setup guide
└── src/
    ├── data_simulator.py    # Infrastructure data generator
    ├── savings_calculator.py # Cost analysis engine
    └── ai_assistant.py      # Optional Claude AI integration
```

---

## 🛠️ Requirements

- Python 3.8+
- Streamlit
- Pandas
- NumPy
- Plotly

Install all with:
```bash
pip install -r requirements.txt
```

---

## ✨ Features

### Real-Time Analysis
- Live progress bars during scanning
- Metrics updating as discoveries are made
- Findings appearing in real-time

### Detailed Breakdowns
- By Team (data-science, backend, ml-ops, etc.)
- By Resource Type (load_balancer, database, cache)
- By Region (us-east-1, us-west-2, eu-west-1, etc.)
- By Environment (production, staging, development)
- By Cloud Provider (AWS, GCP, Azure)

### Interactive Visualizations
- Cumulative savings timeline
- Usage heatmaps by hour/day
- ROI break-even charts
- Resource distribution plots

### Data Export
- Download raw data as CSV
- Generate executive summaries
- Export analysis results

---

## 🎨 Customization

### Change Data Seed
In the sidebar, change the "Random Seed" to generate different scenarios.

### Modify Calculations
Edit `src/savings_calculator.py`:
```python
spot_discount = 0.68  # Adjust discount percentage
discount_rate = 0.10  # Change NPV discount rate
```

### Adjust Simulation
Edit `src/data_simulator.py`:
```python
def generate_ec2_instances(self, count: int = 2847):  # Change instance count
```

---

## 🧮 Calculation Formulas

**Spot Savings:**
```
Savings = Current Cost × Spot Discount (68%)
```

**Storage Lifecycle:**
```
Savings = Data GB × (Standard Rate - IA Rate)
       = Data GB × ($0.023 - $0.0125)
```

**NPV (3-Year):**
```
NPV = -Investment + Σ(Annual Savings / (1 + 0.10)^year)
```

**Payback Period:**
```
Days = (Investment / Monthly Savings) × 30
```

---

## 🤖 Optional AI Integration

Set your Anthropic API key for live AI Q&A:

```bash
export ANTHROPIC_API_KEY="your-key"
streamlit run app.py
```

Without API key, the demo uses intelligent fallback responses.

---

## 📱 Demo Flow

1. **Open** - See "$5M this month?" hook
2. **Click** - "Start Infrastructure Analysis"
3. **Watch** - 4 phases scan in real-time
4. **Review** - Prioritized Quick Wins
5. **Calculate** - Adjust ROI sliders
6. **Execute** - Click "Execute Top 3"
7. **Export** - Download results

---

## 🐛 Troubleshooting

### Demo won't start
```bash
pip install --upgrade streamlit pandas plotly numpy
```

### Port in use
```bash
streamlit run app.py --server.port 8502
```

### Charts not showing
```bash
pip install --upgrade plotly
```

---

## 📄 License

MIT License - Use freely for demos and education

---

## 🎉 Run It Now!

```bash
pip install -r requirements.txt && streamlit run app.py
```

**Click "Start Infrastructure Analysis" and watch the magic!** 🚀
