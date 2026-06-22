import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

st.set_page_config(
    page_title="AutomateIQ — AI Process Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal, reliable CSS — only targets elements Streamlit exposes stably
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, div, p, span, h1, h2, h3, h4, button, input, label, select, textarea {
    font-family: 'Inter', sans-serif !important;
}
.main .block-container { padding-top: 1.8rem; padding-bottom: 2rem; max-width: 1300px; }

/* Cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-top: 4px solid #4f46e5;
    border-radius: 12px;
    padding: 1.4rem 1.5rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    margin-bottom: 0.5rem;
}
.kpi-label { font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
.kpi-value { font-size: 2.2rem; font-weight: 800; color: #1e293b; line-height: 1; margin-bottom: 6px; }
.kpi-sub   { font-size: 0.78rem; color: #94a3b8; }
.kpi-sub.green { color: #16a34a; font-weight: 600; }

.idea-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.idea-title { font-size: 0.9rem; font-weight: 600; color: #1e293b; margin-bottom: 5px; }
.idea-cat   { font-size: 0.76rem; color: #94a3b8; margin-bottom: 6px; }

.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    margin-right: 4px;
}
.badge-green  { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.badge-yellow { background: #fefce8; color: #a16207; border: 1px solid #fde68a; }
.badge-red    { background: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
.badge-indigo { background: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe; }
.badge-sky    { background: #f0f9ff; color: #0369a1; border: 1px solid #bae6fd; }

.section-hdr {
    font-size: 1rem;
    font-weight: 700;
    color: #1e293b;
    margin: 1.2rem 0 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f1f5f9;
}

.phase-box {
    background: #f5f3ff;
    border-left: 4px solid #4f46e5;
    border-radius: 0 10px 10px 0;
    padding: 0.9rem 1.1rem;
    margin: 1rem 0 0.6rem;
}
.phase-box h4 { font-size: 0.9rem; font-weight: 700; color: #3730a3; margin: 0 0 3px; }
.phase-box p  { font-size: 0.78rem; color: #6b7280; margin: 0; }

.tip-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
}

.page-title { font-size: 1.85rem; font-weight: 800; color: #1e293b; letter-spacing: -0.4px; margin-bottom: 4px; }
.page-sub   { font-size: 0.9rem; color: #64748b; margin-bottom: 1.5rem; }

hr.divider { border: none; border-top: 1px solid #f1f5f9; margin: 1.4rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Plotly theme ─────────────────────────────────────────────────────────────
def styled_fig(fig, height=360):
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Inter", color="#374151", size=12),
        title_font=dict(family="Inter", color="#1e293b", size=14),
        height=height,
        margin=dict(l=6, r=6, t=44, b=6),
        legend=dict(font=dict(color="#374151", size=10),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#e2e8f0", borderwidth=1),
    )
    fig.update_xaxes(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0",
                     linecolor="#e2e8f0", tickfont=dict(color="#374151"))
    fig.update_yaxes(gridcolor="#f1f5f9", zerolinecolor="#e2e8f0",
                     linecolor="#e2e8f0", tickfont=dict(color="#374151"))
    return fig


# ── Data ─────────────────────────────────────────────────────────────────────
AUTOMATION_IDEAS = {
    "Sales & Marketing": [
        {"idea": "Lead scoring & qualification",                    "effort": "Low",    "impact": "High",   "roi": 85, "time_saved": 12},
        {"idea": "Personalized email campaign generation",          "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 8},
        {"idea": "Competitor analysis & monitoring",                "effort": "Medium", "impact": "High",   "roi": 70, "time_saved": 6},
        {"idea": "Social media content scheduling",                 "effort": "Low",    "impact": "Medium", "roi": 60, "time_saved": 5},
        {"idea": "CRM data enrichment & deduplication",            "effort": "Low",    "impact": "High",   "roi": 82, "time_saved": 10},
        {"idea": "Sales call transcription & coaching",             "effort": "Low",    "impact": "High",   "roi": 75, "time_saved": 7},
        {"idea": "Proposal & quote generation",                     "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 9},
        {"idea": "Ad copy A/B testing automation",                  "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 5},
        {"idea": "Customer sentiment & intent analysis",            "effort": "Low",    "impact": "High",   "roi": 72, "time_saved": 6},
        {"idea": "Win/loss analysis automation",                    "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 7},
        {"idea": "Pipeline forecasting & risk flagging",            "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 8},
        {"idea": "Outbound prospecting sequence automation",        "effort": "Low",    "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "Sales territory optimization",                    "effort": "Medium", "impact": "Medium", "roi": 62, "time_saved": 5},
        {"idea": "Contract renewal alert & upsell triggers",        "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 6},
        {"idea": "Marketing attribution modelling",                 "effort": "High",   "impact": "High",   "roi": 76, "time_saved": 8},
        {"idea": "SEO content gap analysis & briefs",               "effort": "Low",    "impact": "Medium", "roi": 63, "time_saved": 5},
        {"idea": "Event / webinar follow-up automation",            "effort": "Low",    "impact": "Medium", "roi": 58, "time_saved": 4},
        {"idea": "Chatbot for website lead qualification",          "effort": "Medium", "impact": "High",   "roi": 83, "time_saved": 12},
        {"idea": "Dynamic pricing recommendations",                 "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 10},
        {"idea": "Customer lifetime value prediction",              "effort": "High",   "impact": "High",   "roi": 85, "time_saved": 8},
    ],
    "Customer Onboarding": [
        {"idea": "Automated welcome & drip email sequences",        "effort": "Low",    "impact": "High",   "roi": 80, "time_saved": 8},
        {"idea": "KYC / identity document verification",            "effort": "Medium", "impact": "High",   "roi": 90, "time_saved": 15},
        {"idea": "Personalized onboarding journey builder",         "effort": "Medium", "impact": "High",   "roi": 75, "time_saved": 10},
        {"idea": "Account setup guided chatbot",                    "effort": "Medium", "impact": "High",   "roi": 70, "time_saved": 12},
        {"idea": "Onboarding progress tracking & nudges",           "effort": "Low",    "impact": "Medium", "roi": 60, "time_saved": 5},
        {"idea": "Eligibility & compliance pre-checks",             "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 20},
        {"idea": "Customer health score initialisation",            "effort": "Medium", "impact": "High",   "roi": 72, "time_saved": 7},
        {"idea": "Product tutorial & training recommendation",      "effort": "Medium", "impact": "Medium", "roi": 58, "time_saved": 5},
        {"idea": "Onboarding bottleneck detection & alerting",      "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Customer segmentation at signup",                 "effort": "Low",    "impact": "Medium", "roi": 62, "time_saved": 4},
        {"idea": "Automated provisioning & access setup",           "effort": "Medium", "impact": "High",   "roi": 84, "time_saved": 12},
        {"idea": "Stakeholder intro email generation",              "effort": "Low",    "impact": "Medium", "roi": 55, "time_saved": 3},
        {"idea": "Onboarding satisfaction survey & analysis",       "effort": "Low",    "impact": "Medium", "roi": 60, "time_saved": 4},
        {"idea": "Risk-based onboarding flag & escalation",         "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "Digital contract signing automation",             "effort": "Low",    "impact": "High",   "roi": 82, "time_saved": 8},
    ],
    "Customer Service": [
        {"idea": "AI chatbot for tier-1 & tier-2 support",         "effort": "Medium", "impact": "High",   "roi": 92, "time_saved": 25},
        {"idea": "Ticket routing & priority classification",        "effort": "Low",    "impact": "High",   "roi": 85, "time_saved": 15},
        {"idea": "Auto-response drafting for agents",               "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 12},
        {"idea": "Customer churn prediction & intervention",        "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 10},
        {"idea": "Voice & video call summarization",                "effort": "Low",    "impact": "High",   "roi": 75, "time_saved": 8},
        {"idea": "Feedback & review analysis at scale",             "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 5},
        {"idea": "Escalation detection & smart handoff",            "effort": "Low",    "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "FAQ & knowledge base generation from tickets",    "effort": "Low",    "impact": "Medium", "roi": 62, "time_saved": 4},
        {"idea": "Agent assist — real-time answer suggestions",     "effort": "Medium", "impact": "High",   "roi": 84, "time_saved": 14},
        {"idea": "SLA breach prediction & alerting",                "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 8},
        {"idea": "Multi-channel conversation summarisation",        "effort": "Low",    "impact": "High",   "roi": 72, "time_saved": 6},
        {"idea": "Proactive service outage notifications",          "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 8},
        {"idea": "Customer effort score prediction",                "effort": "Medium", "impact": "Medium", "roi": 60, "time_saved": 5},
        {"idea": "Self-service portal content optimisation",        "effort": "Medium", "impact": "High",   "roi": 70, "time_saved": 7},
        {"idea": "Repeat contact root cause analysis",              "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Post-interaction survey automation",              "effort": "Low",    "impact": "Medium", "roi": 58, "time_saved": 4},
        {"idea": "Warranty & returns processing automation",        "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 10},
    ],
    "Operations": [
        {"idea": "Inventory demand forecasting",                    "effort": "High",   "impact": "High",   "roi": 90, "time_saved": 20},
        {"idea": "Process bottleneck detection",                    "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 15},
        {"idea": "AI-powered quality control inspection",           "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 18},
        {"idea": "Workflow orchestration & intelligent routing",    "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 14},
        {"idea": "Order status update automation",                  "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 7},
        {"idea": "Predictive maintenance scheduling",               "effort": "High",   "impact": "High",   "roi": 85, "time_saved": 20},
        {"idea": "Resource & capacity allocation optimisation",     "effort": "High",   "impact": "High",   "roi": 80, "time_saved": 16},
        {"idea": "SLA breach alerting & response",                  "effort": "Low",    "impact": "High",   "roi": 70, "time_saved": 8},
        {"idea": "Returns & reverse logistics automation",          "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 10},
        {"idea": "Facilities management scheduling",                "effort": "Medium", "impact": "Medium", "roi": 62, "time_saved": 6},
        {"idea": "Shift & workforce schedule optimisation",         "effort": "High",   "impact": "High",   "roi": 84, "time_saved": 14},
        {"idea": "Process mining & improvement recommendations",    "effort": "High",   "impact": "High",   "roi": 86, "time_saved": 18},
        {"idea": "Energy usage monitoring & optimisation",          "effort": "Medium", "impact": "Medium", "roi": 64, "time_saved": 6},
        {"idea": "Automated daily/weekly ops reports",              "effort": "Low",    "impact": "Medium", "roi": 60, "time_saved": 5},
        {"idea": "Exception & anomaly detection in workflows",      "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 10},
        {"idea": "Capacity planning & scenario modelling",          "effort": "High",   "impact": "High",   "roi": 82, "time_saved": 12},
    ],
    "Finance & Accounting": [
        {"idea": "Invoice processing & OCR extraction",             "effort": "Medium", "impact": "High",   "roi": 92, "time_saved": 22},
        {"idea": "Expense report automation & policy check",        "effort": "Low",    "impact": "High",   "roi": 85, "time_saved": 14},
        {"idea": "Fraud detection & transaction alerting",          "effort": "High",   "impact": "High",   "roi": 95, "time_saved": 30},
        {"idea": "Automated financial report generation",           "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 16},
        {"idea": "Budget variance analysis & alerts",               "effort": "Medium", "impact": "High",   "roi": 75, "time_saved": 10},
        {"idea": "Accounts payable automation",                     "effort": "Medium", "impact": "High",   "roi": 88, "time_saved": 18},
        {"idea": "Accounts receivable & collections automation",    "effort": "Medium", "impact": "High",   "roi": 86, "time_saved": 16},
        {"idea": "Tax compliance monitoring & filing prep",         "effort": "High",   "impact": "High",   "roi": 82, "time_saved": 15},
        {"idea": "Cash flow forecasting & liquidity alerts",        "effort": "High",   "impact": "High",   "roi": 78, "time_saved": 12},
        {"idea": "Payroll processing & anomaly detection",          "effort": "Medium", "impact": "High",   "roi": 85, "time_saved": 14},
        {"idea": "Month-end close acceleration",                    "effort": "High",   "impact": "High",   "roi": 84, "time_saved": 20},
        {"idea": "Intercompany reconciliation automation",          "effort": "High",   "impact": "High",   "roi": 80, "time_saved": 18},
        {"idea": "Capital expenditure approval workflow",           "effort": "Medium", "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "Credit risk scoring for new customers",           "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 10},
        {"idea": "Treasury & FX exposure monitoring",               "effort": "High",   "impact": "High",   "roi": 78, "time_saved": 10},
        {"idea": "Audit trail & evidence collection automation",    "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 8},
        {"idea": "Real-time spend analytics dashboard",             "effort": "Medium", "impact": "High",   "roi": 72, "time_saved": 8},
        {"idea": "Vendor payment scheduling optimisation",          "effort": "Low",    "impact": "Medium", "roi": 62, "time_saved": 5},
    ],
    "Human Resources": [
        {"idea": "Resume screening & skills ranking",               "effort": "Low",    "impact": "High",   "roi": 88, "time_saved": 20},
        {"idea": "Interview scheduling automation",                 "effort": "Low",    "impact": "High",   "roi": 82, "time_saved": 14},
        {"idea": "Employee onboarding workflow automation",         "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 12},
        {"idea": "Performance review drafting & calibration",       "effort": "Medium", "impact": "Medium", "roi": 65, "time_saved": 8},
        {"idea": "HR policy & benefits Q&A chatbot",                "effort": "Medium", "impact": "High",   "roi": 75, "time_saved": 10},
        {"idea": "Employee attrition risk prediction",              "effort": "High",   "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "Time & attendance anomaly detection",             "effort": "Low",    "impact": "Medium", "roi": 68, "time_saved": 6},
        {"idea": "Job description & posting generation",            "effort": "Low",    "impact": "Medium", "roi": 60, "time_saved": 4},
        {"idea": "Learning & development path recommendation",      "effort": "Medium", "impact": "High",   "roi": 72, "time_saved": 8},
        {"idea": "Employee engagement survey analysis",             "effort": "Low",    "impact": "High",   "roi": 70, "time_saved": 6},
        {"idea": "Compensation benchmarking automation",            "effort": "Medium", "impact": "Medium", "roi": 62, "time_saved": 5},
        {"idea": "Workforce diversity & inclusion analytics",       "effort": "Medium", "impact": "Medium", "roi": 60, "time_saved": 4},
        {"idea": "Candidate sourcing & outreach automation",        "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 12},
        {"idea": "Offboarding checklist & knowledge capture",       "effort": "Low",    "impact": "Medium", "roi": 58, "time_saved": 4},
        {"idea": "Labor law & compliance monitoring",               "effort": "High",   "impact": "High",   "roi": 82, "time_saved": 10},
        {"idea": "Internal mobility & skills gap matching",         "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 7},
        {"idea": "Background verification workflow",                "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 8},
    ],
    "Information Technology": [
        {"idea": "IT helpdesk & tier-1 support chatbot",            "effort": "Medium", "impact": "High",   "roi": 90, "time_saved": 25},
        {"idea": "AI-assisted code review",                         "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 14},
        {"idea": "Incident detection & root cause analysis",        "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 20},
        {"idea": "Security threat detection & SIEM enrichment",     "effort": "High",   "impact": "High",   "roi": 95, "time_saved": 30},
        {"idea": "Automated test case generation",                  "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 16},
        {"idea": "Cloud infrastructure cost optimisation",          "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 12},
        {"idea": "Log analysis & anomaly summarisation",            "effort": "Low",    "impact": "High",   "roi": 76, "time_saved": 10},
        {"idea": "API & technical documentation generation",        "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 7},
        {"idea": "Change management & impact analysis",             "effort": "Medium", "impact": "High",   "roi": 72, "time_saved": 8},
        {"idea": "Automated patch management & rollout",            "effort": "High",   "impact": "High",   "roi": 84, "time_saved": 14},
        {"idea": "Dev onboarding & codebase Q&A bot",               "effort": "Low",    "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Data pipeline monitoring & alerting",             "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "License & software asset management",             "effort": "Low",    "impact": "Medium", "roi": 68, "time_saved": 6},
        {"idea": "Disaster recovery runbook automation",            "effort": "High",   "impact": "High",   "roi": 86, "time_saved": 16},
        {"idea": "User access review & de-provisioning",            "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 8},
        {"idea": "Capacity planning for infrastructure",            "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 8},
        {"idea": "CI/CD pipeline intelligence & optimisation",      "effort": "High",   "impact": "High",   "roi": 82, "time_saved": 12},
    ],
    "Supply & Vendor Management": [
        {"idea": "Vendor risk scoring & monitoring",                "effort": "Medium", "impact": "High",   "roi": 85, "time_saved": 14},
        {"idea": "Purchase order automation & approval",            "effort": "Low",    "impact": "High",   "roi": 82, "time_saved": 12},
        {"idea": "Contract review & obligation extraction",         "effort": "Medium", "impact": "High",   "roi": 88, "time_saved": 18},
        {"idea": "Supplier performance monitoring & scorecards",    "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 10},
        {"idea": "Demand-supply matching & reorder triggers",       "effort": "High",   "impact": "High",   "roi": 90, "time_saved": 22},
        {"idea": "Logistics route optimisation",                    "effort": "High",   "impact": "High",   "roi": 85, "time_saved": 20},
        {"idea": "Shipment tracking & ETA alerts",                  "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "RFP / RFQ response generation",                   "effort": "Medium", "impact": "Medium", "roi": 68, "time_saved": 8},
        {"idea": "Spend analytics & category management",           "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 10},
        {"idea": "Supplier onboarding & qualification",             "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Supply chain disruption prediction",              "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 18},
        {"idea": "Customs & trade compliance automation",           "effort": "High",   "impact": "High",   "roi": 82, "time_saved": 14},
        {"idea": "Tail spend identification & consolidation",       "effort": "Medium", "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "3-way match automation (PO/GR/invoice)",         "effort": "Medium", "impact": "High",   "roi": 86, "time_saved": 14},
        {"idea": "Warehouse slot & inventory placement AI",         "effort": "High",   "impact": "High",   "roi": 80, "time_saved": 14},
        {"idea": "Vendor contract renewal alerts & negotiation",    "effort": "Low",    "impact": "High",   "roi": 72, "time_saved": 6},
    ],
    "Legal & Compliance": [
        {"idea": "Contract drafting & clause recommendation",       "effort": "Medium", "impact": "High",   "roi": 88, "time_saved": 18},
        {"idea": "Legal document review & redlining",               "effort": "Medium", "impact": "High",   "roi": 86, "time_saved": 16},
        {"idea": "Regulatory change monitoring & alerts",           "effort": "Medium", "impact": "High",   "roi": 84, "time_saved": 14},
        {"idea": "GDPR / data privacy compliance checks",           "effort": "High",   "impact": "High",   "roi": 90, "time_saved": 20},
        {"idea": "Policy violation detection in communications",    "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 16},
        {"idea": "Legal research & case law summarisation",         "effort": "Low",    "impact": "High",   "roi": 80, "time_saved": 14},
        {"idea": "NDA & standard agreement generation",             "effort": "Low",    "impact": "High",   "roi": 82, "time_saved": 10},
        {"idea": "IP & trademark monitoring",                       "effort": "Medium", "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "Litigation hold & e-discovery automation",        "effort": "High",   "impact": "High",   "roi": 84, "time_saved": 18},
        {"idea": "Contract obligation tracking & expiry alerts",    "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 8},
        {"idea": "Anti-money laundering (AML) screening",          "effort": "High",   "impact": "High",   "roi": 92, "time_saved": 22},
        {"idea": "Sanctions & watchlist screening automation",      "effort": "Medium", "impact": "High",   "roi": 88, "time_saved": 16},
        {"idea": "Internal audit findings classification",          "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 10},
        {"idea": "Compliance training assignment automation",       "effort": "Low",    "impact": "Medium", "roi": 62, "time_saved": 5},
        {"idea": "Board & shareholder reporting automation",        "effort": "Medium", "impact": "Medium", "roi": 65, "time_saved": 7},
    ],
    "Data & Analytics": [
        {"idea": "Automated data quality checks & profiling",       "effort": "Medium", "impact": "High",   "roi": 84, "time_saved": 14},
        {"idea": "Self-serve analytics chatbot (NL to SQL)",        "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 20},
        {"idea": "Automated dashboard & report generation",         "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 14},
        {"idea": "Data pipeline failure detection & alerting",      "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 10},
        {"idea": "Master data management deduplication",            "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 10},
        {"idea": "Anomaly detection in business KPIs",              "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 12},
        {"idea": "Predictive analytics model deployment",           "effort": "High",   "impact": "High",   "roi": 90, "time_saved": 20},
        {"idea": "Data catalogue auto-documentation",               "effort": "Medium", "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "Automated A/B test analysis & reporting",         "effort": "Low",    "impact": "Medium", "roi": 68, "time_saved": 5},
        {"idea": "Data lineage & impact analysis",                  "effort": "High",   "impact": "High",   "roi": 76, "time_saved": 10},
        {"idea": "Churn / LTV / propensity model refresh",          "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 14},
        {"idea": "Market & economic signal monitoring",             "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Automated insight narrative generation",          "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 8},
        {"idea": "Data access governance & PII masking",            "effort": "High",   "impact": "High",   "roi": 84, "time_saved": 10},
    ],
    "Product & Engineering": [
        {"idea": "User feedback clustering & roadmap input",        "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 10},
        {"idea": "Feature usage analytics & drop-off detection",    "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "AI-generated release notes & changelogs",         "effort": "Low",    "impact": "Medium", "roi": 62, "time_saved": 4},
        {"idea": "Bug triage & severity classification",            "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 8},
        {"idea": "Sprint velocity & delivery risk forecasting",     "effort": "Medium", "impact": "High",   "roi": 72, "time_saved": 6},
        {"idea": "Automated code documentation & diagrams",         "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "Dependency vulnerability scanning & alerting",    "effort": "Low",    "impact": "High",   "roi": 82, "time_saved": 8},
        {"idea": "UX / usability test analysis automation",         "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 7},
        {"idea": "On-call alert noise reduction & grouping",        "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "Product spec & PRD drafting assistant",           "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 5},
        {"idea": "Performance regression detection in CI",          "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 8},
        {"idea": "Localisation & translation automation",           "effort": "Medium", "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "API contract & schema change detection",          "effort": "Low",    "impact": "High",   "roi": 72, "time_saved": 6},
        {"idea": "Competitive product benchmarking",                "effort": "Medium", "impact": "High",   "roi": 70, "time_saved": 6},
    ],
    "Healthcare & Life Sciences": [
        {"idea": "Clinical documentation & note summarisation",     "effort": "Medium", "impact": "High",   "roi": 90, "time_saved": 25},
        {"idea": "Prior authorisation request automation",          "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 20},
        {"idea": "Medical coding & claims processing",              "effort": "High",   "impact": "High",   "roi": 92, "time_saved": 24},
        {"idea": "Patient no-show prediction & scheduling",         "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 12},
        {"idea": "Drug interaction & contraindication alerts",      "effort": "High",   "impact": "High",   "roi": 94, "time_saved": 20},
        {"idea": "Clinical trial patient matching",                 "effort": "High",   "impact": "High",   "roi": 86, "time_saved": 18},
        {"idea": "Adverse event detection & pharmacovigilance",     "effort": "High",   "impact": "High",   "roi": 90, "time_saved": 20},
        {"idea": "Healthcare chatbot for patient queries",          "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 16},
        {"idea": "Radiology & pathology image pre-screening AI",    "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 18},
        {"idea": "Revenue cycle denial management",                 "effort": "Medium", "impact": "High",   "roi": 84, "time_saved": 14},
        {"idea": "Regulatory submission document preparation",      "effort": "High",   "impact": "High",   "roi": 82, "time_saved": 16},
        {"idea": "Remote patient monitoring alerting",              "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 20},
    ],
    "Real Estate & Facilities": [
        {"idea": "Lease abstraction & obligation extraction",       "effort": "Medium", "impact": "High",   "roi": 86, "time_saved": 16},
        {"idea": "Space utilisation & occupancy analytics",         "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "Preventive maintenance scheduling & tracking",    "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 14},
        {"idea": "Tenant onboarding & communications automation",   "effort": "Low",    "impact": "High",   "roi": 76, "time_saved": 8},
        {"idea": "Property valuation & market analysis",            "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Energy & utilities consumption monitoring",       "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 10},
        {"idea": "Lease renewal alert & negotiation prep",          "effort": "Low",    "impact": "High",   "roi": 72, "time_saved": 6},
        {"idea": "Visitor management & access control automation",  "effort": "Low",    "impact": "Medium", "roi": 62, "time_saved": 5},
        {"idea": "Facilities work order routing & tracking",        "effort": "Low",    "impact": "Medium", "roi": 65, "time_saved": 6},
        {"idea": "Capital project status monitoring & alerts",      "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
    ],
    "Education & Training": [
        {"idea": "Personalised learning path recommendation",       "effort": "Medium", "impact": "High",   "roi": 82, "time_saved": 12},
        {"idea": "Automated assignment grading & feedback",         "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 16},
        {"idea": "Course content generation & updating",            "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 10},
        {"idea": "Student / learner engagement monitoring",         "effort": "Low",    "impact": "High",   "roi": 72, "time_saved": 7},
        {"idea": "Skills gap analysis across workforce",            "effort": "Medium", "impact": "High",   "roi": 78, "time_saved": 8},
        {"idea": "Certification & compliance tracking",             "effort": "Low",    "impact": "High",   "roi": 75, "time_saved": 6},
        {"idea": "Q&A chatbot for training content",                "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Learning outcome & ROI measurement",              "effort": "Medium", "impact": "Medium", "roi": 64, "time_saved": 6},
        {"idea": "Adaptive assessment generation",                  "effort": "High",   "impact": "High",   "roi": 80, "time_saved": 10},
        {"idea": "Instructor & facilitator scheduling",             "effort": "Low",    "impact": "Medium", "roi": 60, "time_saved": 4},
    ],
    "Cross-Functional": [
        {"idea": "Meeting notes & action item capture",             "effort": "Low",    "impact": "High",   "roi": 78, "time_saved": 10},
        {"idea": "Cross-department executive reporting",            "effort": "Medium", "impact": "High",   "roi": 75, "time_saved": 12},
        {"idea": "Document management & semantic search",           "effort": "Medium", "impact": "High",   "roi": 72, "time_saved": 8},
        {"idea": "Internal knowledge base chatbot",                 "effort": "Medium", "impact": "High",   "roi": 80, "time_saved": 14},
        {"idea": "Regulatory compliance monitoring",                "effort": "High",   "impact": "High",   "roi": 88, "time_saved": 20},
        {"idea": "Data quality & deduplication pipeline",           "effort": "Medium", "impact": "High",   "roi": 76, "time_saved": 10},
        {"idea": "Executive dashboard auto-generation",             "effort": "Medium", "impact": "High",   "roi": 70, "time_saved": 8},
        {"idea": "Project status summarisation & RAG reporting",    "effort": "Low",    "impact": "High",   "roi": 70, "time_saved": 7},
        {"idea": "Interdepartmental SLA tracking",                  "effort": "Medium", "impact": "Medium", "roi": 62, "time_saved": 5},
        {"idea": "ESG & sustainability data collection & reporting","effort": "High",   "impact": "High",   "roi": 78, "time_saved": 12},
        {"idea": "Employee communications & newsletter generation", "effort": "Low",    "impact": "Medium", "roi": 58, "time_saved": 4},
        {"idea": "Spend & budget visibility across departments",    "effort": "Medium", "impact": "High",   "roi": 74, "time_saved": 8},
        {"idea": "Digital signature & approval workflow",           "effort": "Low",    "impact": "High",   "roi": 80, "time_saved": 8},
        {"idea": "Vendor & partner communication automation",       "effort": "Low",    "impact": "Medium", "roi": 62, "time_saved": 5},
    ],
}

CAT_ICONS = {
    "Sales & Marketing":          "📈",
    "Customer Onboarding":        "🚀",
    "Customer Service":           "💬",
    "Operations":                 "⚙️",
    "Finance & Accounting":       "💰",
    "Human Resources":            "👥",
    "Information Technology":     "💻",
    "Supply & Vendor Management": "📦",
    "Legal & Compliance":         "⚖️",
    "Data & Analytics":           "📊",
    "Product & Engineering":      "🛠️",
    "Healthcare & Life Sciences":  "🏥",
    "Real Estate & Facilities":   "🏢",
    "Education & Training":       "🎓",
    "Cross-Functional":           "🔗",
}

CAT_COLORS = [
    "#4f46e5","#7c3aed","#0891b2","#059669","#16a34a",
    "#d97706","#dc2626","#9333ea","#0e7490","#b45309",
    "#be185d","#047857","#1d4ed8","#7e22ce","#64748b",
]

EFFORT_NUM = {"Low": 1, "Medium": 2, "High": 3}
IMPACT_NUM = {"Low": 1, "Medium": 2, "High": 3}


def all_df():
    rows = []
    for cat, ideas in AUTOMATION_IDEAS.items():
        for idea in ideas:
            rows.append({**idea, "category": cat})
    return pd.DataFrame(rows)


def effort_badge(e):
    cls = {"Low": "badge-green", "Medium": "badge-yellow", "High": "badge-red"}[e]
    return f'<span class="badge {cls}">{e} Effort</span>'

def impact_badge(i):
    cls = {"Low": "badge-red", "Medium": "badge-yellow", "High": "badge-green"}[i]
    return f'<span class="badge {cls}">{i} Impact</span>'


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ AutomateIQ")
    st.caption("AI Process Intelligence Platform")
    st.divider()

    page = st.radio(
        "Go to",
        ["📊  Dashboard", "📚  Explore Library", "🔍  Analyze Process",
         "🗺️  Priority Map", "⚠️  Risk Assessment",
         "💰  ROI Calculator", "📋  Implementation Plan", "❓  Help"],
        label_visibility="collapsed",
    )
    page = page.split("  ", 1)[1]  # strip icon prefix

    st.divider()
    df_s = all_df()
    st.caption(f"**{len(df_s)}** automation ideas across **9** functions")


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown('<p class="page-title">AI Automation Command Center</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Explore and prioritize AI automation opportunities across your enterprise</p>', unsafe_allow_html=True)

    df = all_df()
    hi   = len(df[df["impact"]=="High"])
    qw   = len(df[(df["impact"]=="High") & (df["effort"]=="Low")])
    avg_r = df["roi"].mean()
    hrs  = df["time_saved"].sum()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl, sub, green in [
        (c1, len(df),        "Total Ideas",             "9 business functions",  False),
        (c2, hi,             "High-Impact",             f"{hi/len(df)*100:.0f}% of all ideas", True),
        (c3, f"{avg_r:.0f}%","Avg ROI Potential",       "Across all categories", True),
        (c4, f"{hrs}h",      "Weekly Hours Saved",      "Across all processes",  True),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{lbl}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-sub {'green' if green else ''}">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown('<p class="section-hdr">Average ROI by Business Function</p>', unsafe_allow_html=True)
        cat_df = (df.groupby("category")
                  .agg(avg_roi=("roi","mean"), count=("idea","count"))
                  .reset_index().sort_values("avg_roi"))
        cat_df["label"] = cat_df["category"].map(CAT_ICONS) + "  " + cat_df["category"]
        fig = go.Figure(go.Bar(
            x=cat_df["avg_roi"], y=cat_df["label"], orientation="h",
            marker_color="#4f46e5",
            text=cat_df["avg_roi"].map("{:.0f}%".format),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Avg ROI: %{x:.0f}%<extra></extra>",
        ))
        styled_fig(fig, 370)
        fig.update_xaxes(range=[0, 108], title_text="Avg ROI %")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<p class="section-hdr">Ideas by Function</p>', unsafe_allow_html=True)
        pie_df = df.groupby("category").size().reset_index(name="n")
        pie_df["lbl"] = pie_df["category"].map(CAT_ICONS) + " " + pie_df["category"].str.split(" ").str[0]
        fig2 = go.Figure(go.Pie(
            labels=pie_df["lbl"], values=pie_df["n"],
            hole=0.55,
            marker=dict(colors=CAT_COLORS, line=dict(color="#ffffff", width=2)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value} ideas (%{percent})<extra></extra>",
        ))
        fig2.add_annotation(text=f"<b>{len(df)}</b><br>ideas",
                            x=0.5, y=0.5, showarrow=False,
                            font=dict(color="#1e293b", size=16, family="Inter"))
        styled_fig(fig2, 370)
        fig2.update_layout(showlegend=True,
            legend=dict(font=dict(size=9), orientation="v"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    bot_l, bot_r = st.columns([2, 3], gap="large")
    with bot_l:
        st.markdown('<p class="section-hdr">Effort × Impact Density</p>', unsafe_allow_html=True)
        heat = df.groupby(["effort","impact"]).size().unstack(fill_value=0)
        heat = heat.reindex(index=["Low","Medium","High"], columns=["Low","Medium","High"], fill_value=0)
        fig3 = go.Figure(go.Heatmap(
            z=heat.values, x=heat.columns.tolist(), y=heat.index.tolist(),
            colorscale=[[0,"#f5f3ff"],[0.5,"#818cf8"],[1,"#4f46e5"]],
            text=heat.values, texttemplate="%{text}",
            textfont=dict(size=20, color="#1e293b"),
            showscale=False,
            hovertemplate="Effort %{y} / Impact %{x}: %{z} ideas<extra></extra>",
        ))
        styled_fig(fig3, 260)
        fig3.update_xaxes(title_text="Impact")
        fig3.update_yaxes(title_text="Effort")
        st.plotly_chart(fig3, use_container_width=True)

    with bot_r:
        st.markdown('<p class="section-hdr">⚡ Quick Wins — High Impact, Low Effort</p>', unsafe_allow_html=True)
        qw_df = df[(df["impact"]=="High") & (df["effort"]=="Low")].sort_values("roi", ascending=False).head(5)
        for _, r in qw_df.iterrows():
            st.markdown(f"""
            <div class="idea-card">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:12px">
                <div style="flex:1;min-width:0">
                  <div class="idea-title">{r['idea']}</div>
                  <div class="idea-cat">{CAT_ICONS[r['category']]} {r['category']}</div>
                  {effort_badge(r['effort'])} {impact_badge(r['impact'])}
                </div>
                <div style="text-align:right;flex-shrink:0">
                  <div style="font-size:1.6rem;font-weight:800;color:#4f46e5;line-height:1">{r['roi']}%</div>
                  <div style="font-size:0.68rem;color:#94a3b8;margin-top:2px">ROI</div>
                  <div style="font-size:0.75rem;color:#16a34a;font-weight:600;margin-top:2px">↓ {r['time_saved']}h/wk</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# EXPLORE LIBRARY
# ════════════════════════════════════════════════════════════════════════════
elif page == "Explore Library":
    st.markdown('<p class="page-title">Automation Idea Library</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Filter and browse 540+ pre-catalogued AI automation opportunities</p>', unsafe_allow_html=True)

    df = all_df()
    with st.expander("🔎  Filters", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1: cats  = st.multiselect("Department",  list(AUTOMATION_IDEAS.keys()), default=list(AUTOMATION_IDEAS.keys()))
        with fc2: effs  = st.multiselect("Effort",      ["Low","Medium","High"],       default=["Low","Medium","High"])
        with fc3: imps  = st.multiselect("Impact",      ["Low","Medium","High"],       default=["High"])
        with fc4: min_r = st.slider("Min ROI %", 0, 100, 60)

    filt = df[df["category"].isin(cats) & df["effort"].isin(effs) &
              df["impact"].isin(imps) & (df["roi"] >= min_r)].sort_values("roi", ascending=False)

    st.caption(f"Showing **{len(filt)}** of {len(df)} ideas")

    if filt.empty:
        st.info("No ideas match your filters — try adjusting above.")
    else:
        for cat in [c for c in list(AUTOMATION_IDEAS.keys()) if c in cats]:
            sub = filt[filt["category"] == cat]
            if sub.empty: continue
            st.markdown(f'<p class="section-hdr">{CAT_ICONS[cat]} {cat} <span style="font-weight:400;color:#94a3b8;font-size:0.8rem">— {len(sub)} ideas</span></p>', unsafe_allow_html=True)
            for _, r in sub.iterrows():
                st.markdown(f"""
                <div class="idea-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;gap:12px">
                    <div style="flex:1">
                      <div class="idea-title">{r['idea']}</div>
                      {effort_badge(r['effort'])} {impact_badge(r['impact'])}
                      <span class="badge badge-indigo">ROI {r['roi']}%</span>
                      <span class="badge badge-sky">{r['time_saved']}h/wk saved</span>
                    </div>
                    <div style="background:#eef2ff;border-radius:8px;padding:6px 14px;text-align:center;flex-shrink:0">
                      <div style="font-size:1.15rem;font-weight:800;color:#4f46e5">{r['roi']}%</div>
                      <div style="font-size:0.62rem;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:.5px">ROI</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ANALYZE PROCESS
# ════════════════════════════════════════════════════════════════════════════
elif page == "Analyze Process":
    st.markdown('<p class="page-title">Process Analyzer</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Describe your business process to get tailored AI automation recommendations</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["✍️  Describe a Process", "📄  Upload Document"])

    with tab1:
        col_l, col_r = st.columns([2, 1], gap="large")
        with col_l:
            dept = st.selectbox("Department", list(AUTOMATION_IDEAS.keys()))
            proc = st.text_input("Process Name", placeholder="e.g. Monthly invoice reconciliation")
            desc = st.text_area("Describe the process — steps, pain points, tools used",
                height=148,
                placeholder="e.g. Our AP team exports invoices from ERP monthly, cross-checks against POs in Excel, flags discrepancies, emails vendors, then updates a tracker. Takes ~3 days for 2 staff.")
        with col_r:
            freq = st.selectbox("Frequency", ["Daily","Weekly","Monthly","Quarterly"])
            vol  = st.number_input("Volume / cycle",    min_value=1, value=100)
            team = st.number_input("Team members",      min_value=1, value=2)
            hrs  = st.number_input("Hours / cycle",     min_value=1, value=16)

        if st.button("Analyze & Match Automations", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                time.sleep(0.9)

            df = all_df()
            matches = df[df["category"]==dept].sort_values("roi", ascending=False)
            mult = {"Daily":250,"Weekly":52,"Monthly":12,"Quarterly":4}[freq]
            annual_hrs = int(hrs * 0.65) * mult

            st.success(f"Found **{len(matches)} automation opportunities** for **{dept}**")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Matches",          len(matches))
            m2.metric("Hours Saved/Year", f"{annual_hrs:,}")
            m3.metric("Readiness Score",  f"{int(matches['roi'].mean())}%")
            m4.metric("Top Pick",         matches.iloc[0]["idea"][:24]+"…")

            st.markdown('<p class="section-hdr">Top Recommendations</p>', unsafe_allow_html=True)
            rank_col = ["#d97706","#94a3b8","#b45309","#4f46e5","#4f46e5","#4f46e5"]
            for i, (_, r) in enumerate(matches.head(6).iterrows()):
                st.markdown(f"""
                <div class="idea-card">
                  <div style="display:flex;gap:14px;align-items:center">
                    <div style="width:32px;height:32px;border-radius:50%;background:#f5f3ff;
                                border:2px solid #c7d2fe;display:flex;align-items:center;
                                justify-content:center;font-size:0.82rem;font-weight:800;
                                color:{rank_col[i]};flex-shrink:0">#{i+1}</div>
                    <div style="flex:1">
                      <div class="idea-title">{r['idea']}</div>
                      <div class="idea-cat">{CAT_ICONS[r['category']]} {r['category']}</div>
                      {effort_badge(r['effort'])} {impact_badge(r['impact'])}
                      <span class="badge badge-sky">{r['time_saved']}h/wk saved</span>
                    </div>
                    <div style="text-align:right;flex-shrink:0">
                      <div style="font-size:1.5rem;font-weight:800;color:#4f46e5">{r['roi']}%</div>
                      <div style="font-size:0.65rem;color:#94a3b8">ROI</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

    with tab2:
        up = st.file_uploader("Upload process document (TXT or CSV)", type=["txt","csv"])
        if up:
            st.text_area("Preview", up.read().decode("utf-8", errors="ignore")[:2000], height=220)
            st.info("Copy key details into the **Describe a Process** tab for best results.")


# ════════════════════════════════════════════════════════════════════════════
# PRIORITY MAP
# ════════════════════════════════════════════════════════════════════════════
elif page == "Priority Map":
    st.markdown('<p class="page-title">Priority Opportunity Map</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Visualize all automation opportunities by effort, impact, and ROI</p>', unsafe_allow_html=True)

    df = all_df()
    view = st.radio("View", ["Priority Matrix","ROI Heatmap","Function Breakdown"], horizontal=True)

    if view == "Priority Matrix":
        df["e_n"] = df["effort"].map(EFFORT_NUM)
        df["i_n"] = df["impact"].map(IMPACT_NUM)
        color_map = dict(zip(list(AUTOMATION_IDEAS.keys()), CAT_COLORS))
        fig = px.scatter(df, x="e_n", y="i_n", size="roi", color="category",
                         hover_name="idea",
                         hover_data={"roi":True,"time_saved":True,"effort":True,"impact":True,"e_n":False,"i_n":False,"category":False},
                         size_max=26, color_discrete_map=color_map,
                         labels={"e_n":"Effort Level","i_n":"Impact Level"})
        fig.update_xaxes(tickvals=[1,2,3], ticktext=["Low","Medium","High"])
        fig.update_yaxes(tickvals=[1,2,3], ticktext=["Low","Medium","High"])
        fig.add_shape(type="rect", x0=0.5,y0=2.5,x1=1.5,y1=3.5,
                      fillcolor="rgba(79,70,229,0.06)",
                      line=dict(color="#4f46e5",dash="dot",width=1.5))
        fig.add_annotation(x=1,y=3.48,text="⚡ Quick Win Zone",showarrow=False,
                           font=dict(color="#4f46e5",size=11,family="Inter"))
        styled_fig(fig, 500)
        st.plotly_chart(fig, use_container_width=True)

    elif view == "ROI Heatmap":
        pivot = df.groupby(["category","effort"])["roi"].mean().unstack(fill_value=0)
        pivot = pivot.reindex(columns=["Low","Medium","High"], fill_value=0)
        fig = go.Figure(go.Heatmap(
            z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
            colorscale=[[0,"#f5f3ff"],[0.5,"#818cf8"],[1,"#4f46e5"]],
            text=pivot.values.round(0).astype(int),
            texttemplate="%{text}%", textfont=dict(size=13,color="#1e293b"),
            showscale=True,
            hovertemplate="<b>%{y}</b><br>Effort: %{x}<br>Avg ROI: %{z:.0f}%<extra></extra>",
        ))
        styled_fig(fig, 440)
        st.plotly_chart(fig, use_container_width=True)

    else:
        cats_s = df.groupby("category").agg(
            ideas=("idea","count"), avg_roi=("roi","mean"), hrs=("time_saved","sum")
        ).reset_index().sort_values("avg_roi",ascending=False)

        fig = make_subplots(rows=1, cols=3,
            subplot_titles=["Ideas per Function","Avg ROI %","Weekly Hours Saved"],
            shared_yaxes=True)
        for ci, col in enumerate([cats_s["ideas"], cats_s["avg_roi"], cats_s["hrs"]], 1):
            fig.add_trace(go.Bar(
                x=cats_s["category"], y=col,
                marker_color=CAT_COLORS[:len(cats_s)],
                text=col.round(0).astype(int), textposition="outside",
                textfont=dict(size=10,color="#374151"), showlegend=False,
            ), row=1, col=ci)
        styled_fig(fig, 420)
        fig.update_xaxes(tickangle=38, tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# RISK ASSESSMENT
# ════════════════════════════════════════════════════════════════════════════
elif page == "Risk Assessment":
    st.markdown('<p class="page-title">Automation Readiness & Risk</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Score your organization before committing to automation projects</p>', unsafe_allow_html=True)

    df = all_df()
    rc1, rc2 = st.columns(2)
    with rc1: sel_cat  = st.selectbox("Category", list(AUTOMATION_IDEAS.keys()))
    with rc2: sel_idea = st.selectbox("Idea",     df[df["category"]==sel_cat]["idea"].tolist())
    row = df[(df["category"]==sel_cat) & (df["idea"]==sel_idea)].iloc[0]

    st.divider()
    st.markdown("**Rate your organization on each dimension (1 = Low, 5 = High)**")

    sl1, sl2 = st.columns(2)
    with sl1:
        dq = st.slider("Data Quality",              1,5,3)
        tr = st.slider("Technology Readiness",      1,5,3)
        cm = st.slider("Change Management Culture", 1,5,3)
    with sl2:
        vd = st.slider("Vendor / Tool Availability",1,5,3)
        cr = st.slider("Compliance Risk (5 = Low)", 1,5,3)
        ic = st.slider("Integration Complexity (5 = Simple)",1,5,3)

    readiness = int(sum([dq*6,tr*6,cm*5,vd*4,cr*4,ic*5]) / sum([30,30,25,20,20,25]) * 100)
    color = "#059669" if readiness>=70 else ("#d97706" if readiness>=45 else "#dc2626")

    gc, rc = st.columns(2)
    with gc:
        st.markdown('<p class="section-hdr">Readiness Gauge</p>', unsafe_allow_html=True)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=readiness,
            number={"suffix":"%","font":{"color":"#1e293b","size":48,"family":"Inter"}},
            gauge={
                "axis":{"range":[0,100],"tickfont":{"color":"#64748b","size":10}},
                "bar":{"color":color,"thickness":0.2},
                "bgcolor":"#f8fafc","bordercolor":"#e2e8f0","borderwidth":1,
                "steps":[
                    {"range":[0,45],"color":"#fef2f2"},
                    {"range":[45,70],"color":"#fefce8"},
                    {"range":[70,100],"color":"#f0fdf4"},
                ],
            },
            title={"text":"Overall Readiness","font":{"color":"#64748b","size":13,"family":"Inter"}},
        ))
        styled_fig(fig, 290)
        st.plotly_chart(fig, use_container_width=True)

    with rc:
        st.markdown('<p class="section-hdr">Factor Radar</p>', unsafe_allow_html=True)
        lbls = ["Data Quality","Tech Ready","Change Mgmt","Vendors","Compliance","Integration"]
        vals = [dq,tr,cm,vd,cr,ic]
        fig2 = go.Figure(go.Scatterpolar(
            r=vals+[vals[0]], theta=lbls+[lbls[0]], fill="toself",
            fillcolor="rgba(79,70,229,0.1)",
            line=dict(color="#4f46e5",width=2),
            marker=dict(color="#4f46e5",size=7),
        ))
        fig2.update_layout(polar=dict(
            bgcolor="#ffffff",
            radialaxis=dict(visible=True,range=[0,5],
                            tickfont=dict(color="#94a3b8",size=9),
                            gridcolor="#f1f5f9",linecolor="#e2e8f0"),
            angularaxis=dict(tickfont=dict(color="#374151",size=10),
                             gridcolor="#f1f5f9",linecolor="#e2e8f0"),
        ))
        styled_fig(fig2, 290)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<p class="section-hdr">Recommendations</p>', unsafe_allow_html=True)
    recs = []
    if dq<3: recs.append(("📊","Data Quality",   "Invest in data governance and cleansing pipelines before launching automation."))
    if tr<3: recs.append(("🔧","Technology",     "Audit your tech stack; consider low-code platforms to reduce technical debt."))
    if cm<3: recs.append(("👥","Change Mgmt",    "Create a communication and training plan; involve impacted teams early."))
    if vd<3: recs.append(("🤝","Vendors",        "Evaluate multiple vendor options to avoid single-point-of-failure dependency."))
    if cr<3: recs.append(("⚖️","Compliance",     "Engage legal and compliance teams early; document all data flows."))
    if ic<3: recs.append(("🔗","Integration",    "Use an iPaaS (MuleSoft, Make, Zapier) to bridge complex legacy systems."))
    if not recs: recs.append(("✅","All Clear",   "Readiness looks strong — you can proceed with confidence."))
    for icon, title, text in recs:
        st.markdown(f"""
        <div class="idea-card">
          <div style="display:flex;gap:12px;align-items:flex-start">
            <div style="font-size:1.2rem;flex-shrink:0">{icon}</div>
            <div>
              <div style="font-weight:700;color:#1e293b;font-size:0.88rem;margin-bottom:3px">{title}</div>
              <div style="color:#64748b;font-size:0.82rem;line-height:1.55">{text}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# ROI CALCULATOR
# ════════════════════════════════════════════════════════════════════════════
elif page == "ROI Calculator":
    st.markdown('<p class="page-title">ROI Calculator</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Build the financial business case for your automation investment</p>', unsafe_allow_html=True)

    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        rate   = st.number_input("Hourly employee cost ($)", value=65, min_value=10)
        hrs_wk = st.number_input("Process hours / week",     value=20, min_value=1)
    with rc2:
        err_rt  = st.slider("Error rate (%)", 0, 50, 10)
        err_cst = st.number_input("Cost per error ($)", value=500, min_value=0)
    with rc3:
        auto_p   = st.slider("Automation coverage (%)", 10, 100, 70)
        impl_cst = st.number_input("Implementation cost ($)", value=25000, min_value=0, step=1000)

    annual_labor  = hrs_wk * rate * 52
    annual_errors = (err_rt/100) * (hrs_wk*52/8) * err_cst
    save_labor    = annual_labor  * (auto_p/100)
    save_errors   = annual_errors * (auto_p/100) * 0.85
    total_save    = save_labor + save_errors
    net_roi       = total_save - impl_cst
    roi_pct       = (net_roi/impl_cst*100) if impl_cst else 0
    payback       = (impl_cst/(total_save/12)) if total_save else 999

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Annual Process Cost",  f"${annual_labor+annual_errors:,.0f}")
    m2.metric("Annual Savings",       f"${total_save:,.0f}", f"+{auto_p}%")
    m3.metric("3-Year Net ROI",       f"${net_roi*3:,.0f}",  f"{roi_pct:.0f}%")
    m4.metric("Payback Period",       f"{payback:.1f} mo")

    years = list(range(1,6))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"Year {y}" for y in years], y=[total_save*y for y in years],
        name="Cumulative Savings", marker_color="#818cf8",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[f"Year {y}" for y in years], y=[total_save*y-impl_cst for y in years],
        mode="lines+markers+text", name="Net ROI",
        line=dict(color="#059669",width=3), marker=dict(size=8,color="#059669"),
        text=[f"${total_save*y-impl_cst:,.0f}" for y in years],
        textposition="top center", textfont=dict(size=10,color="#059669"),
    ))
    fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8", line_width=1)
    styled_fig(fig, 340)
    fig.update_layout(title="5-Year Savings & Net ROI",
                      legend=dict(orientation="h",y=-0.18),
                      yaxis_tickprefix="$", yaxis_tickformat=",")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(pd.DataFrame({
        "Year":            [f"Year {y}" for y in years],
        "Gross Savings":   [f"${total_save*y:,.0f}" for y in years],
        "Net ROI":         [f"${total_save*y-impl_cst:,.0f}" for y in years],
        "Cumulative ROI %":[f"{(total_save*y-impl_cst)/impl_cst*100:.0f}%" if impl_cst else "∞" for y in years],
    }), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION PLAN
# ════════════════════════════════════════════════════════════════════════════
elif page == "Implementation Plan":
    st.markdown('<p class="page-title">Implementation Roadmap</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">A phased automation rollout plan tailored to your focus areas</p>', unsafe_allow_html=True)

    df = all_df()
    pc1, pc2, pc3 = st.columns(3)
    with pc1: focus    = st.multiselect("Focus areas", list(AUTOMATION_IDEAS.keys()), default=["Finance & Accounting","Customer Service"])
    with pc2: timeline = st.slider("Timeline (months)", 3, 24, 12)
    with pc3: budget   = st.number_input("Total budget ($)", value=100000, min_value=5000, step=5000)

    if st.button("Generate Roadmap", type="primary", use_container_width=True):
        with st.spinner("Building your roadmap..."):
            time.sleep(0.7)

        sub = df[df["category"].isin(focus)].copy()
        sub["pri"] = sub["impact"].map(IMPACT_NUM)*10 + sub["roi"]//10 - sub["effort"].map(EFFORT_NUM)
        sub = sub.sort_values("pri", ascending=False)

        ph1 = sub[sub["effort"]=="Low"].head(4)
        ph2 = sub[sub["effort"]=="Medium"].head(4)
        ph3 = sub[sub["effort"]=="High"].head(3)

        phases = [
            ("Phase 1","Quick Wins",           f"Months 1–3",              ph1,
             "Low-effort, high-impact automations you can deploy in weeks."),
            ("Phase 2","Core Automation",      f"Months 4–{min(9,timeline)}",ph2,
             "Medium-complexity initiatives requiring integration work."),
            ("Phase 3","Strategic Initiatives",f"Months {min(10,timeline)}–{timeline}",ph3,
             "High-complexity projects needing cross-team coordination."),
        ]

        for p_s, p_t, p_r, p_df, p_d in phases:
            if p_df.empty: continue
            st.markdown(f"""
            <div class="phase-box">
              <h4>{p_s} — {p_t} &nbsp;·&nbsp; {p_r}</h4>
              <p>{p_d}</p>
            </div>""", unsafe_allow_html=True)
            for i, (_, r) in enumerate(p_df.iterrows()):
                st.markdown(f"""
                <div class="idea-card">
                  <div style="display:flex;gap:14px;align-items:center">
                    <div style="width:30px;height:30px;border-radius:50%;
                                background:#eef2ff;border:1.5px solid #c7d2fe;
                                display:flex;align-items:center;justify-content:center;
                                font-size:0.8rem;font-weight:700;color:#4f46e5;flex-shrink:0">{i+1}</div>
                    <div style="flex:1">
                      <div class="idea-title">{r['idea']}</div>
                      <div class="idea-cat">{CAT_ICONS[r['category']]} {r['category']}</div>
                      {effort_badge(r['effort'])} {impact_badge(r['impact'])}
                      <span class="badge badge-sky">{r['time_saved']}h/wk saved</span>
                    </div>
                    <div style="text-align:right;flex-shrink:0">
                      <div style="font-size:1.4rem;font-weight:800;color:#4f46e5">{r['roi']}%</div>
                      <div style="font-size:0.62rem;color:#94a3b8">ROI</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

        # Gantt chart
        st.markdown('<p class="section-hdr" style="margin-top:1.5rem">Timeline View</p>', unsafe_allow_html=True)
        gantt = []
        offsets = [0, 3, min(9,timeline)]
        pcols = {"Quick Wins":"#4f46e5","Core Automation":"#7c3aed","Strategic Initiatives":"#9333ea"}
        for (_, p_t, _, p_df, _), off in zip(phases, offsets):
            dur = max(1.5, timeline/3*0.7)
            for j,(_, r) in enumerate(p_df.iterrows()):
                gantt.append({"Task":r["idea"][:38],"Start":off+j*0.2,"Duration":dur,"Phase":p_t})
        if gantt:
            gdf = pd.DataFrame(gantt)
            fig = px.bar(gdf, base="Start", x="Duration", y="Task", color="Phase",
                         orientation="h", color_discrete_map=pcols,
                         labels={"Duration":"Duration (months)","Task":""})
            styled_fig(fig, max(300, len(gantt)*28))
            fig.update_layout(xaxis_title="Month",barmode="overlay",
                              legend=dict(orientation="h",y=-0.14))
            st.plotly_chart(fig, use_container_width=True)

        lines = [f"AutomateIQ — Implementation Plan",
                 f"Generated: {datetime.now().strftime('%B %d, %Y')}",
                 f"Timeline: {timeline} months | Budget: ${budget:,}","="*60]
        for p_s,p_t,p_r,p_df,_ in phases:
            if p_df.empty: continue
            lines += [f"\n{p_s}: {p_t} ({p_r})", "-"*40]
            for _,r in p_df.iterrows():
                lines.append(f"  • {r['idea']} ({r['category']}) — ROI {r['roi']}% | {r['effort']} Effort | {r['time_saved']}h/wk saved")
        st.download_button("⬇️ Export Roadmap", "\n".join(lines),
                           file_name="automation_roadmap.txt", mime="text/plain")


# ════════════════════════════════════════════════════════════════════════════
# HELP
# ════════════════════════════════════════════════════════════════════════════
elif page == "Help":
    st.markdown('<p class="page-title">Help & Getting Started</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Everything you need to get the most out of AutomateIQ</p>', unsafe_allow_html=True)

    steps = [
        ("📚","1. Explore Library",      "Filter 540+ automation ideas by department, effort, impact, and minimum ROI."),
        ("🔍","2. Analyze Process",      "Describe a specific process to get matched recommendations and hours-saved estimates."),
        ("🗺️","3. Priority Map",         "View all opportunities in an interactive priority matrix, heatmap, or bar charts."),
        ("⚠️","4. Risk Assessment",      "Score your org across 6 readiness factors and get tailored mitigation advice."),
        ("💰","5. ROI Calculator",       "Enter real process costs to generate savings projections and a 5-year ROI table."),
        ("📋","6. Implementation Plan",  "Generate a phased roadmap — quick wins first — and export it as a text report."),
    ]
    for icon, title, desc in steps:
        st.markdown(f"""
        <div class="idea-card">
          <div style="display:flex;gap:14px;align-items:flex-start">
            <div style="font-size:1.3rem;flex-shrink:0">{icon}</div>
            <div>
              <div style="font-weight:700;color:#1e293b;font-size:0.92rem;margin-bottom:4px">{title}</div>
              <div style="color:#64748b;font-size:0.83rem;line-height:1.55">{desc}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div class="tip-box">
      <div style="font-weight:700;color:#1e293b;font-size:0.88rem;margin-bottom:0.6rem">💡 Pro Tips</div>
      <div style="color:#64748b;font-size:0.83rem;line-height:2.1">
        → Start on the <b style="color:#4f46e5">Dashboard</b> — Quick Wins give you the fastest, clearest starting points<br>
        → Use <b style="color:#4f46e5">ROI Calculator</b> numbers when presenting to executives or finance<br>
        → Run <b style="color:#4f46e5">Risk Assessment</b> per initiative — each has a different readiness profile<br>
        → Export the <b style="color:#4f46e5">Implementation Plan</b> to share a structured roadmap with stakeholders
      </div>
    </div>
    <p style="color:#94a3b8;font-size:0.75rem;text-align:center;margin-top:1rem">
      Built with Streamlit · Plotly · Python · Data from McKinsey, Gartner & industry research
    </p>
    """, unsafe_allow_html=True)
