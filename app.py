"""
The Quick Win Generator - Enhanced Interactive Demo
AI-Powered Cloud Cost Savings with Dynamic Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_simulator import CloudDataSimulator
from savings_calculator import SavingsCalculator
from ai_assistant import AIAssistant

# Page configuration
st.set_page_config(
    page_title="Quick Win Generator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .scan-item {
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        background: #f0f2f6;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .scan-found {
        color: #ff4b4b;
        font-weight: 600;
    }
    .scan-ok {
        color: #00c853;
    }
    .finding-card {
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
        border-radius: 0 8px 8px 0;
    }
    .critical-finding {
        border-left-color: #ff4b4b;
        background: #fff5f5;
    }
    .warning-finding {
        border-left-color: #ffa726;
        background: #fff8e1;
    }
    .info-finding {
        border-left-color: #29b6f6;
        background: #e3f2fd;
    }
    .metric-highlight {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    .discovery-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    .team-badge {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .resource-badge {
        background: #f3e5f5;
        color: #7b1fa2;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(seed=42):
    """Load and cache simulated data"""
    simulator = CloudDataSimulator(seed=seed)
    return simulator.generate_complete_dataset()


@st.cache_data
def calculate_savings(_data):
    """Calculate and cache savings opportunities"""
    calculator = SavingsCalculator(_data)
    opportunities = calculator.calculate_all_opportunities()
    summary = calculator.get_summary_metrics()
    roi = calculator.calculate_roi()
    return calculator, opportunities, summary, roi


def run_dynamic_analysis(data, placeholder):
    """Run dynamic analysis with real-time updates showing discovered issues"""

    ec2_df = data['ec2_instances']
    storage_df = data['storage']
    cross_cloud_df = data['cross_cloud']
    ml_models_df = data['ml_models']

    findings = {
        'infrastructure': [],
        'storage': [],
        'cross_cloud': [],
        'ml_models': []
    }

    with placeholder.container():
        st.markdown("## 🔍 AI Infrastructure Analysis")
        st.markdown("*Real-time scanning and discovery of optimization opportunities...*")

        # ============================================
        # PHASE 1: Infrastructure Scan
        # ============================================
        st.markdown("### 📡 Phase 1: Infrastructure Discovery")

        infra_col1, infra_col2 = st.columns([2, 1])

        with infra_col1:
            infra_progress = st.progress(0)
            infra_status = st.empty()
            infra_findings = st.empty()

        with infra_col2:
            infra_metrics = st.empty()

        # Scan regions
        regions = ec2_df['region'].unique()
        discovered_instances = 0
        spot_candidates = 0
        idle_instances = 0

        region_findings = []

        for i, region in enumerate(regions):
            progress = (i + 1) / len(regions)
            infra_progress.progress(progress)

            region_instances = ec2_df[ec2_df['region'] == region]
            region_count = len(region_instances)
            region_spot = len(region_instances[region_instances['spot_compatible'] == True])
            region_idle = len(region_instances[region_instances['avg_cpu_usage'] < 0.3])

            discovered_instances += region_count
            spot_candidates += region_spot
            idle_instances += region_idle

            infra_status.markdown(f"""
            <div class="scan-item">
            🔍 Scanning <b>{region}</b>...
            Found <span class="scan-found">{region_count} instances</span> |
            <span class="scan-found">{region_spot} spot-compatible</span> |
            <span class="scan-found">{region_idle} idle</span>
            </div>
            """, unsafe_allow_html=True)

            if region_idle > 20:
                region_findings.append({
                    'region': region,
                    'instances': region_count,
                    'idle': region_idle,
                    'potential_savings': region_idle * 0.096 * 730  # Avg hourly cost * hours/month
                })

            with infra_metrics.container():
                st.metric("Instances Found", f"{discovered_instances:,}")
                st.metric("Spot Candidates", f"{spot_candidates:,}")
                st.metric("Idle Resources", f"{idle_instances:,}")

            time.sleep(0.30)

        # Show infrastructure findings
        with infra_findings.container():
            st.markdown("#### 🎯 Infrastructure Findings")

            # Group by environment
            env_analysis = ec2_df.groupby('environment').agg({
                'instance_id': 'count',
                'spot_compatible': 'sum',
                'avg_cpu_usage': 'mean'
            }).reset_index()
            env_analysis.columns = ['Environment', 'Instances', 'Spot Compatible', 'Avg CPU %']
            env_analysis['Avg CPU %'] = (env_analysis['Avg CPU %'] * 100).round(1)

            st.dataframe(env_analysis, use_container_width=True, hide_index=True)

            # Top idle regions
            if region_findings:
                st.markdown("**⚠️ High Idle Capacity Detected:**")
                for rf in sorted(region_findings, key=lambda x: x['idle'], reverse=True)[:3]:
                    st.markdown(f"""
                    <div class="finding-card warning-finding">
                    <b>{rf['region']}</b>: {rf['idle']} idle instances detected<br>
                    Potential Monthly Savings: <b>${rf['potential_savings']:,.0f}</b>
                    </div>
                    """, unsafe_allow_html=True)

        findings['infrastructure'] = {
            'total_instances': discovered_instances,
            'spot_candidates': spot_candidates,
            'idle_instances': idle_instances,
            'by_environment': env_analysis.to_dict('records'),
            'high_idle_regions': region_findings
        }

        st.success(f"✅ Infrastructure scan complete: {discovered_instances:,} instances across {len(regions)} regions")

        time.sleep(2.5)

        # ============================================
        # PHASE 2: Storage Analysis
        # ============================================
        st.markdown("### 💾 Phase 2: Storage Pattern Analysis")

        storage_col1, storage_col2 = st.columns([2, 1])

        with storage_col1:
            storage_progress = st.progress(0)
            storage_status = st.empty()
            storage_findings = st.empty()

        with storage_col2:
            storage_metrics = st.empty()

        # Analyze storage by data type
        data_types = storage_df['data_type'].unique()
        total_size = 0
        stale_data = 0
        optimization_candidates = []

        for i, dtype in enumerate(data_types):
            progress = (i + 1) / len(data_types)
            storage_progress.progress(progress)

            type_data = storage_df[storage_df['data_type'] == dtype]
            type_size = type_data['size_gb'].sum()
            type_stale = type_data[type_data['days_since_last_access'] > 90]['size_gb'].sum()
            type_cost = (type_data['size_gb'] * type_data['cost_per_gb_month']).sum()

            total_size += type_size
            stale_data += type_stale

            storage_status.markdown(f"""
            <div class="scan-item">
            📁 Analyzing <b>{dtype}</b> data...
            <span class="scan-found">{type_size/1024:.1f} TB</span> total |
            <span class="scan-found">{type_stale/1024:.1f} TB</span> stale (90+ days)
            </div>
            """, unsafe_allow_html=True)

            if type_stale > 1024:  # More than 1TB stale
                potential_savings = type_stale * (0.023 - 0.0125)  # Price difference
                optimization_candidates.append({
                    'data_type': dtype,
                    'total_tb': type_size / 1024,
                    'stale_tb': type_stale / 1024,
                    'monthly_savings': potential_savings,
                    'buckets': len(type_data[type_data['days_since_last_access'] > 90])
                })

            with storage_metrics.container():
                st.metric("Total Analyzed", f"{total_size/1024:.1f} TB")
                st.metric("Stale Data", f"{stale_data/1024:.1f} TB")
                st.metric("Optimization %", f"{(stale_data/total_size*100) if total_size > 0 else 0:.0f}%")

            time.sleep(0.30)

        # Show storage findings
        with storage_findings.container():
            st.markdown("#### 🎯 Storage Optimization Opportunities")

            if optimization_candidates:
                for oc in sorted(optimization_candidates, key=lambda x: x['monthly_savings'], reverse=True):
                    st.markdown(f"""
                    <div class="finding-card info-finding">
                    <span class="resource-badge">{oc['data_type'].upper()}</span><br>
                    {oc['stale_tb']:.1f} TB of {oc['total_tb']:.1f} TB not accessed in 90+ days<br>
                    <b>{oc['buckets']} buckets</b> can be moved to Infrequent Access tier<br>
                    Monthly Savings: <b>${oc['monthly_savings']:,.0f}</b>
                    </div>
                    """, unsafe_allow_html=True)

        findings['storage'] = {
            'total_tb': total_size / 1024,
            'stale_tb': stale_data / 1024,
            'optimization_candidates': optimization_candidates
        }

        st.success(f"✅ Storage analysis complete: {stale_data/1024:.1f} TB can be optimized")

        time.sleep(2.5)

        # ============================================
        # PHASE 3: Cross-Cloud Duplicate Detection
        # ============================================
        st.markdown("### ☁️ Phase 3: Cross-Cloud Duplicate Detection")

        cc_col1, cc_col2 = st.columns([2, 1])

        with cc_col1:
            cc_progress = st.progress(0)
            cc_status = st.empty()
            cc_findings = st.empty()

        with cc_col2:
            cc_metrics = st.empty()

        # Find duplicates by team
        duplicates = cross_cloud_df[cross_cloud_df['is_duplicate'] == True]
        teams = duplicates['team'].unique()

        total_duplicates = 0
        total_waste = 0
        team_findings = []
        resource_type_findings = []

        for i, team in enumerate(teams):
            progress = (i + 1) / len(teams)
            cc_progress.progress(progress)

            team_dupes = duplicates[duplicates['team'] == team]
            team_count = len(team_dupes)
            team_cost = team_dupes['monthly_cost'].sum()

            # Find which resources are duplicated
            team_resources = team_dupes.groupby('resource_type').agg({
                'resource_name': 'count',
                'monthly_cost': 'sum',
                'cloud_provider': lambda x: list(x.unique())
            }).reset_index()

            total_duplicates += team_count
            total_waste += team_cost / 2  # Half is waste (keeping one copy)

            cc_status.markdown(f"""
            <div class="scan-item">
            🔎 Checking <span class="team-badge">{team}</span>...
            <span class="scan-found">{team_count} duplicate resources</span> |
            Wasted: <span class="scan-found">${team_cost/2:,.0f}/month</span>
            </div>
            """, unsafe_allow_html=True)

            team_findings.append({
                'team': team,
                'duplicates': team_count,
                'monthly_waste': team_cost / 2,
                'clouds': team_dupes['cloud_provider'].unique().tolist(),
                'resource_types': team_resources.to_dict('records')
            })

            with cc_metrics.container():
                st.metric("Duplicates Found", f"{total_duplicates:,}")
                st.metric("Monthly Waste", f"${total_waste:,.0f}")
                st.metric("Clouds Affected", "3 (AWS, GCP, Azure)")

            time.sleep(0.50)

        # Analyze by resource type
        resource_summary = duplicates.groupby('resource_type').agg({
            'resource_name': 'nunique',
            'monthly_cost': 'sum'
        }).reset_index()
        resource_summary.columns = ['Resource Type', 'Unique Resources', 'Total Monthly Cost']
        resource_summary['Potential Savings'] = resource_summary['Total Monthly Cost'] / 2

        # Show cross-cloud findings
        with cc_findings.container():
            st.markdown("#### 🎯 Duplicate Resources by Team")

            for tf in sorted(team_findings, key=lambda x: x['monthly_waste'], reverse=True)[:4]:
                clouds_str = " + ".join(tf['clouds'])
                st.markdown(f"""
                <div class="finding-card critical-finding">
                <span class="team-badge">{tf['team']}</span>
                <span style="float:right;font-weight:600;color:#c62828">${tf['monthly_waste']:,.0f}/mo waste</span><br>
                <b>{tf['duplicates']} duplicates</b> across {clouds_str}<br>
                Resource Types: {', '.join([r['resource_type'] for r in tf['resource_types'][:3]])}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 📊 By Resource Type")
            st.dataframe(resource_summary.sort_values('Potential Savings', ascending=False),
                        use_container_width=True, hide_index=True)

        findings['cross_cloud'] = {
            'total_duplicates': total_duplicates,
            'monthly_waste': total_waste,
            'by_team': team_findings,
            'by_resource_type': resource_summary.to_dict('records')
        }

        st.success(f"✅ Cross-cloud scan complete: {total_duplicates} duplicates = ${total_waste:,.0f}/month waste")

        time.sleep(3.5)

        # ============================================
        # PHASE 4: ML Model Registry Audit
        # ============================================
        st.markdown("### 🤖 Phase 4: ML Model Registry Audit")

        ml_col1, ml_col2 = st.columns([2, 1])

        with ml_col1:
            ml_progress = st.progress(0)
            ml_status = st.empty()
            ml_findings = st.empty()

        with ml_col2:
            ml_metrics = st.empty()

        # Analyze models
        model_names = ml_models_df['model_name'].unique()
        total_versions = 0
        prunable_versions = 0
        total_storage = 0
        model_findings = []

        for i, model in enumerate(model_names):
            progress = (i + 1) / len(model_names)
            ml_progress.progress(progress)

            model_data = ml_models_df[ml_models_df['model_name'] == model]
            versions = len(model_data)
            active = len(model_data[model_data['is_active'] == True])
            prunable = len(model_data[(model_data['is_active'] == False) & (model_data['days_old'] > 90)])
            storage_gb = model_data['size_gb'].sum()
            prunable_storage = model_data[(model_data['is_active'] == False) & (model_data['days_old'] > 90)]['size_gb'].sum()
            framework = model_data['framework'].iloc[0]

            total_versions += versions
            prunable_versions += prunable
            total_storage += storage_gb

            ml_status.markdown(f"""
            <div class="scan-item">
            🔬 Auditing <b>{model}</b> ({framework})...
            <span class="scan-found">{versions} versions</span> |
            <span class="scan-ok">{active} active</span> |
            <span class="scan-found">{prunable} prunable</span>
            </div>
            """, unsafe_allow_html=True)

            if prunable > 50:
                model_findings.append({
                    'model': model,
                    'framework': framework,
                    'total_versions': versions,
                    'active_versions': active,
                    'prunable_versions': prunable,
                    'storage_gb': storage_gb,
                    'prunable_storage_gb': prunable_storage,
                    'monthly_savings': prunable_storage * 0.023 * 1.5
                })

            with ml_metrics.container():
                st.metric("Models Scanned", f"{i+1}/{len(model_names)}")
                st.metric("Total Versions", f"{total_versions:,}")
                st.metric("Prunable", f"{prunable_versions:,}")

            time.sleep(0.30)

        # Framework analysis
        framework_summary = ml_models_df.groupby('framework').agg({
            'version': 'count',
            'size_gb': 'sum',
            'is_active': 'sum'
        }).reset_index()
        framework_summary.columns = ['Framework', 'Total Versions', 'Storage (GB)', 'Active Versions']

        # Show ML findings
        with ml_findings.container():
            st.markdown("#### 🎯 Model Registry Cleanup Opportunities")

            for mf in sorted(model_findings, key=lambda x: x['prunable_versions'], reverse=True)[:4]:
                st.markdown(f"""
                <div class="finding-card warning-finding">
                <b>{mf['model']}</b> <span class="resource-badge">{mf['framework']}</span><br>
                {mf['prunable_versions']} of {mf['total_versions']} versions can be pruned ({mf['active_versions']} active)<br>
                Storage to reclaim: <b>{mf['prunable_storage_gb']:.1f} GB</b><br>
                Monthly Savings: <b>${mf['monthly_savings']:,.0f}</b>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("#### 📊 By Framework")
            st.dataframe(framework_summary, use_container_width=True, hide_index=True)

        findings['ml_models'] = {
            'total_versions': total_versions,
            'prunable_versions': prunable_versions,
            'total_storage_gb': total_storage,
            'model_findings': model_findings,
            'by_framework': framework_summary.to_dict('records')
        }

        st.success(f"✅ ML audit complete: {prunable_versions} versions ({total_storage:.0f} GB) can be pruned")

        time.sleep(6.5)

        # ============================================
        # PHASE 5: Final Summary
        # ============================================
        st.markdown("### 🎉 Analysis Complete!")

        # Calculate totals
        total_monthly_savings = (
            sum(r['potential_savings'] for r in findings['infrastructure'].get('high_idle_regions', [])) +
            sum(o['monthly_savings'] for o in findings['storage'].get('optimization_candidates', [])) +
            findings['cross_cloud']['monthly_waste'] +
            sum(m['monthly_savings'] for m in findings['ml_models'].get('model_findings', []))
        )

        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        with summary_col1:
            st.markdown("""
            <div style="text-align:center;padding:1rem;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;color:white;">
            <div style="font-size:0.9rem;">INFRASTRUCTURE</div>
            <div style="font-size:2rem;font-weight:700;">{:,}</div>
            <div style="font-size:0.8rem;">instances analyzed</div>
            </div>
            """.format(findings['infrastructure']['total_instances']), unsafe_allow_html=True)

        with summary_col2:
            st.markdown("""
            <div style="text-align:center;padding:1rem;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;color:white;">
            <div style="font-size:0.9rem;">STORAGE</div>
            <div style="font-size:2rem;font-weight:700;">{:.0f} TB</div>
            <div style="font-size:0.8rem;">optimizable</div>
            </div>
            """.format(findings['storage']['stale_tb']), unsafe_allow_html=True)

        with summary_col3:
            st.markdown("""
            <div style="text-align:center;padding:1rem;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;color:white;">
            <div style="font-size:0.9rem;">DUPLICATES</div>
            <div style="font-size:2rem;font-weight:700;">{:,}</div>
            <div style="font-size:0.8rem;">cross-cloud</div>
            </div>
            """.format(findings['cross_cloud']['total_duplicates']), unsafe_allow_html=True)

        with summary_col4:
            st.markdown("""
            <div style="text-align:center;padding:1rem;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;color:white;">
            <div style="font-size:0.9rem;">ML VERSIONS</div>
            <div style="font-size:2rem;font-weight:700;">{:,}</div>
            <div style="font-size:0.8rem;">prunable</div>
            </div>
            """.format(findings['ml_models']['prunable_versions']), unsafe_allow_html=True)

           # Pause before completing analysis
        time.sleep(10)

    return findings


def main():
    """Main application"""

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")

        demo_mode = st.selectbox(
            "Analysis Mode",
            ["Full Dynamic Scan", "Quick Analysis", "Deep Dive"],
            help="Choose the analysis depth"
        )

        st.markdown("---")

        st.markdown("### 🎲 Data Simulation")

        # Initialize seed in session state if not present
        if 'last_seed' not in st.session_state:
            st.session_state.last_seed = 42

        seed = st.number_input("Random Seed", value=st.session_state.last_seed, min_value=1, max_value=9999,
                              help="Change seed value to generate different infrastructure data")

        # Check if seed changed and reset analysis state
        if st.session_state.last_seed != seed:
            st.session_state.last_seed = seed
            st.session_state.analysis_run = False
            st.session_state.show_results = False
            st.session_state.analysis_complete = False
            st.session_state.findings = None
            # Clear chat history on seed change
            st.session_state.chat_messages = []
            if 'ai_assistant' in st.session_state:
                st.session_state.ai_assistant.clear_history()

        if st.button("🔄 Generate New Scenario", help="Generate random seed and create new infrastructure"):
            import random
            st.cache_data.clear()
            # Generate new random seed
            st.session_state.last_seed = random.randint(1, 9999)
            # Reset all session state to clear old analysis results
            st.session_state.analysis_run = False
            st.session_state.show_results = False
            st.session_state.analysis_complete = False
            st.session_state.findings = None
            # Clear chat history
            st.session_state.chat_messages = []
            if 'ai_assistant' in st.session_state:
                st.session_state.ai_assistant.clear_history()
            st.rerun()


    # Main content
    st.markdown('<h1 class="main-header">💰 The Quick Win Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;font-size:1.2rem;color:#6c757d;margin-bottom:2rem;">AI-Powered Cloud Cost Optimization</p>', unsafe_allow_html=True)

    # Load data
    data = load_data(seed)

    # Check if analysis is complete to show results
    analysis_complete = st.session_state.get('analysis_complete', False)

    if not analysis_complete:
        # Opening hook - BEFORE analysis (no specific amount yet)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Discover Your Hidden")
            st.markdown('<div style="text-align: center; font-size: 4rem; font-weight: 700; color: #667eea; margin: 1rem 0;">Cloud Savings</div>', unsafe_allow_html=True)
            st.markdown('<div style="text-align: center; font-size: 1.5rem; margin-bottom: 2rem; color: #6c757d;">Let AI analyze your infrastructure and find quick wins</div>', unsafe_allow_html=True)

            if st.button("🚀 Start Infrastructure Analysis", type="primary", use_container_width=True):
                st.session_state.analysis_run = True
                st.session_state.show_results = True
                st.rerun()

    # Analysis Section
    if st.session_state.get('show_results', False):
        st.markdown("---")

        # Run the dynamic analysis
        analysis_placeholder = st.empty()

        if not st.session_state.get('analysis_complete', False):
            findings = run_dynamic_analysis(data, analysis_placeholder)
            st.session_state.findings = findings
            st.session_state.analysis_complete = True
            time.sleep(1)
            st.rerun()

        # Calculate savings first to get the total
        calculator, opportunities, summary, roi = calculate_savings(data)
        total_monthly = sum(opp.monthly_savings for opp in opportunities)

        # Show discovered savings as the hero number - AFTER analysis
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🎉 Analysis Complete! We found")
            st.markdown(f'<div style="text-align: center; font-size: 5rem; font-weight: 700; color: #00c853; margin: 1rem 0;">${total_monthly/1_000_000:.1f}M</div>', unsafe_allow_html=True)
            st.markdown('<div style="text-align: center; font-size: 2rem; margin-bottom: 1rem;">in monthly savings</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; font-size: 1.2rem; color: #6c757d; margin-bottom: 2rem;">(${total_monthly*12/1_000_000:.1f}M annually)</div>', unsafe_allow_html=True)

        # Quick summary cards
        sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
        findings = st.session_state.get('findings', {})

        with sum_col1:
            instances = findings.get('infrastructure', {}).get('total_instances', 0)
            st.metric("Instances Scanned", f"{instances:,}")
        with sum_col2:
            storage_tb = findings.get('storage', {}).get('total_tb', 0)
            st.metric("Storage Analyzed", f"{storage_tb:.0f} TB")
        with sum_col3:
            duplicates = findings.get('cross_cloud', {}).get('total_duplicates', 0)
            st.metric("Duplicates Found", f"{duplicates:,}")
        with sum_col4:
            prunable = findings.get('ml_models', {}).get('prunable_versions', 0)
            st.metric("ML Versions Prunable", f"{prunable:,}")

        st.markdown("---")

        # AI Chat - Make it prominent right after results
        st.markdown("## 🤖 Ask AI About Your Results")

        # Initialize AI assistant in session state
        if 'ai_assistant' not in st.session_state:
            st.session_state.ai_assistant = AIAssistant()

        # Initialize chat messages in session state
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []

        # Update AI context with current analysis
        if findings:
            st.session_state.ai_assistant.set_analysis_context(findings, opportunities, summary)

        # Show API status
      #  if st.session_state.ai_assistant.is_available():
       #     st.success("🟢 Claude API connected - Live AI responses enabled")
       # else:
       #     st.info("🔵 Using intelligent fallback responses (set ANTHROPIC_API_KEY for live AI)")

        # Chat interface in a nice container
        chat_col1, chat_col2 = st.columns([3, 2])

        with chat_col1:
            # Display chat messages
            chat_container = st.container(height=300)
            with chat_container:
                if not st.session_state.chat_messages:
                    st.markdown("*Ask me anything about the analysis results, recommendations, risks, or implementation details...*")
                for msg in st.session_state.chat_messages:
                    if msg["role"] == "user":
                        st.markdown(f"""
                        <div style="background:#e3f2fd;padding:0.75rem;border-radius:10px;margin:0.5rem 0;">
                        <strong>You:</strong> {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background:#f5f5f5;padding:0.75rem;border-radius:10px;margin:0.5rem 0;border-left:4px solid #667eea;">
                        {msg["content"]}
                        </div>
                        """, unsafe_allow_html=True)

            # Chat input
            input_col1, input_col2 = st.columns([5, 1])
            with input_col1:
                user_question = st.text_input(
                    "Ask a question",
                    placeholder="e.g., What's the risk of spot instance migration?",
                    key="chat_input",
                    label_visibility="collapsed"
                )
            with input_col2:
                send_clicked = st.button("Send", type="primary", use_container_width=True)

            if send_clicked and user_question:
                st.session_state.chat_messages.append({"role": "user", "content": user_question})
                with st.spinner("Thinking..."):
                    response = st.session_state.ai_assistant.ask(user_question)
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

        with chat_col2:
            st.markdown("**Quick Questions:**")
            if st.button("💡 Tell me about spot instances", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": "Tell me about spot instance migration"})
                response = st.session_state.ai_assistant.ask("Tell me about spot instance migration")
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("📊 How is ROI calculated?", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": "How is the ROI calculated?"})
                response = st.session_state.ai_assistant.ask("How is the ROI calculated?")
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("⚠️ What are the risks?", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": "What are the risks of these recommendations?"})
                response = st.session_state.ai_assistant.ask("What are the risks of these recommendations?")
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("📅 What's the timeline?", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": "What's the implementation timeline?"})
                response = st.session_state.ai_assistant.ask("What's the implementation timeline?")
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            if st.button("👥 Which teams are affected?", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": "Which teams have the most duplicates?"})
                response = st.session_state.ai_assistant.ask("Which teams have the most duplicates?")
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
                st.rerun()

            st.markdown("---")
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.session_state.ai_assistant.clear_history()
                st.rerun()

        st.markdown("---")

        # Quick Win Dashboard
        st.markdown("## 🎯 Prioritized Quick Wins")
        st.markdown("*Based on analysis findings, ranked by impact and feasibility*")

        # Display opportunities with enhanced details
        for idx, opp in enumerate(opportunities):
            with st.expander(f"**#{idx + 1} {opp.name}** - ${opp.monthly_savings/1_000_000:.2f}M/month", expanded=(idx < 2)):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**{opp.description}**")

                    # Risk and timeline
                    risk_color = {'None': '🟢', 'Low': '🟡', 'Medium': '🟠', 'High': '🔴'}
                    st.markdown(f"{risk_color.get(opp.risk_level, '⚪')} **Risk:** {opp.risk_level} | ⏱️ **Timeline:** {opp.implementation_time}")

                    # Confidence bar
                    st.markdown(f"**Confidence:** {opp.confidence * 100:.0f}%")
                    st.progress(opp.confidence)

                with col2:
                    st.metric("Monthly Savings", f"${opp.monthly_savings/1_000_000:.2f}M")
                    st.metric("Annual Impact", f"${opp.annual_savings/1_000_000:.1f}M")

                with col3:
                    st.metric("Resources", f"{opp.affected_resources:,}")

                    # Add context based on opportunity type
                    if 'Spot' in opp.name:
                        st.caption(f"Across {data['ec2_instances']['region'].nunique()} regions")
                    elif 'Storage' in opp.name:
                        st.caption(f"{data['storage']['data_type'].nunique()} data types")
                    elif 'Cross-Cloud' in opp.name:
                        st.caption(f"{data['cross_cloud']['team'].nunique()} teams affected")
                    elif 'Model' in opp.name:
                        st.caption(f"{data['ml_models']['framework'].nunique()} frameworks")

                # Detailed breakdown
                st.markdown("##### 📊 Detailed Breakdown")

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:
                    if 'by_environment' in opp.details:
                        st.markdown("**By Environment:**")
                        for env, count in opp.details['by_environment'].items():
                            st.markdown(f"- {env}: {count} resources")

                    if 'by_data_type' in opp.details:
                        st.markdown("**By Data Type:**")
                        for dtype, size in list(opp.details['by_data_type'].items())[:5]:
                            st.markdown(f"- {dtype}: {size/1024:.1f} TB")

                    if 'by_cloud' in opp.details:
                        st.markdown("**By Cloud Provider:**")
                        for cloud, cost in opp.details['by_cloud'].items():
                            st.markdown(f"- {cloud.upper()}: ${cost:,.0f}/mo")

                    if 'by_framework' in opp.details:
                        st.markdown("**By Framework:**")
                        for fw, cost in list(opp.details['by_framework'].items())[:5]:
                            st.markdown(f"- {fw}: ${cost:,.0f}/mo")

                with detail_col2:
                    if 'by_region' in opp.details:
                        st.markdown("**Top Regions:**")
                        sorted_regions = sorted(opp.details['by_region'].items(), key=lambda x: x[1], reverse=True)[:5]
                        for region, cost in sorted_regions:
                            st.markdown(f"- {region}: ${cost:,.0f}/mo")

                    if 'by_resource_type' in opp.details:
                        st.markdown("**By Resource Type:**")
                        for rtype, cost in list(opp.details['by_resource_type'].items())[:5]:
                            st.markdown(f"- {rtype}: ${cost:,.0f}/mo")

                    if 'by_team' in opp.details:
                        st.markdown("**By Team:**")
                        for team, cost in list(opp.details['by_team'].items())[:5]:
                            st.markdown(f"- {team}: ${cost:,.0f}/mo")

        st.markdown("---")

        # Execute button
        selected_top_3 = opportunities[:3]
        top_3_savings = sum(opp.monthly_savings for opp in selected_top_3)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align:center;padding:1.5rem;background:#f8f9fa;border-radius:10px;margin-bottom:1rem;">
            <div style="font-size:1.2rem;color:#6c757d;">Top 3 Quick Wins Total</div>
            <div style="font-size:3rem;font-weight:700;color:#667eea;">${top_3_savings/1_000_000:.1f}M<span style="font-size:1rem;color:#6c757d;">/month</span></div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("⚡ EXECUTE TOP 3 QUICK WINS ⚡", type="primary", use_container_width=True):
                st.balloons()
                st.success(f"✅ Implementation queued! Week 1 savings: **${top_3_savings/1_000_000:.1f}M/month** (${top_3_savings*12/1_000_000:.1f}M annualized)")

        st.markdown("---")

        # ROI Calculator
        st.markdown("## 💎 ROI Calculator")

        calc_col1, calc_col2 = st.columns(2)

        with calc_col1:
            investment = st.slider(
                "Initial Investment ($M)",
                min_value=1.0,
                max_value=10.0,
                value=5.4,
                step=0.1
            )

        with calc_col2:
            include_all = st.checkbox("Include all 4 recommendations", value=False)
            if include_all:
                total_monthly = sum(opp.monthly_savings for opp in opportunities)
            else:
                total_monthly = top_3_savings

        # Calculate ROI
        annual_savings = total_monthly * 12 / 1_000_000
        payback_months = investment / (total_monthly / 1_000_000)
        payback_days = payback_months * 30

        # NPV calculation
        discount_rate = 0.10
        npv = -investment
        for year in range(1, 4):
            npv += annual_savings / ((1 + discount_rate) ** year)

        roi_pct = ((annual_savings - investment) / investment) * 100

        # Display ROI metrics
        roi_col1, roi_col2, roi_col3, roi_col4 = st.columns(4)

        with roi_col1:
            st.metric("Payback Period", f"{payback_days:.0f} days")
        with roi_col2:
            st.metric("Annual Savings", f"${annual_savings:.1f}M")
        with roi_col3:
            st.metric("First Year ROI", f"{roi_pct:.0f}%")
        with roi_col4:
            st.metric("3-Year NPV", f"${npv:.1f}M")

        # Cumulative savings chart
        months = list(range(0, 13))
        cumulative_savings = [-investment] + [
            (total_monthly / 1_000_000 * m) - investment
            for m in range(1, 13)
        ]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months,
            y=cumulative_savings,
            mode='lines+markers',
            name='Cumulative Savings',
            fill='tozeroy',
            line=dict(color='#667eea', width=3)
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break Even")
        fig.update_layout(
            title="Cumulative Savings Over Time",
            xaxis_title="Month",
            yaxis_title="Cumulative Savings ($M)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        # Data explorer
        with st.expander("🔍 Explore Raw Data"):
            tab1, tab2, tab3, tab4 = st.tabs(["EC2", "Storage", "Cross-Cloud", "ML Models"])

            with tab1:
                st.dataframe(data['ec2_instances'].head(100), use_container_width=True)
            with tab2:
                st.dataframe(data['storage'].head(100), use_container_width=True)
            with tab3:
                st.dataframe(data['cross_cloud'].head(100), use_container_width=True)
            with tab4:
                st.dataframe(data['ml_models'].head(100), use_container_width=True)

    # Footer
    #st.markdown("---")
    #st.markdown("""
    #<div style='text-align: center; color: #6c757d; padding: 2rem;'>
     #   <p><strong>The Quick Win Generator</strong> - AI-Powered Cloud Cost Optimization</p>
      #  <p>All analysis performed in real-time on simulated data | Python + Streamlit + Plotly</p>
    #</div>
   # """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
