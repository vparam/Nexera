# ⚡ Quick Start - 60 Seconds to Running Demo

## The Absolute Fastest Way

```bash
./run.sh
```

**That's it!** The demo opens in your browser automatically.

---

## What Just Happened?

The script automatically:
1. ✅ Checked your Python installation
2. ✅ Created a virtual environment
3. ✅ Installed all dependencies
4. ✅ Started the Streamlit server
5. ✅ Opened your browser

---

## Manual Method (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the demo
streamlit run app.py

# 3. Open browser (automatic)
# http://localhost:8501
```

---

## What You'll See

1. **"What could you do with $5M?"** - Opening hook
2. **Click "Start Infrastructure Analysis"** - Begin scan
3. **Watch 4 phases scan in real-time**:
   - Phase 1: Infrastructure Discovery (12 regions)
   - Phase 2: Storage Pattern Analysis (5 data types)
   - Phase 3: Cross-Cloud Duplicate Detection (4 teams)
   - Phase 4: ML Model Registry Audit (10 models)
4. **Review prioritized Quick Wins** - Detailed breakdowns
5. **Use ROI Calculator** - Interactive sliders
6. **Click "Execute Top 3"** - See celebration!

---

## Try These Features

### 🔄 Generate New Data
Click "Generate New Scenario" in sidebar → Creates new random scenario

### 📊 Adjust ROI
Move sliders to model different investments

### 📥 Export Data
Download buttons for CSV exports

---

## Troubleshooting (30 seconds)

### Demo won't start?
```bash
pip install --upgrade streamlit pandas plotly numpy
```

### Port already in use?
```bash
streamlit run app.py --server.port 8502
```

### Python not found?
```bash
python3 --version  # Should be 3.8+
```

---

## One More Time

```bash
pip install -r requirements.txt && streamlit run app.py
```

**Enjoy exploring $80M in cloud savings!** 💰
