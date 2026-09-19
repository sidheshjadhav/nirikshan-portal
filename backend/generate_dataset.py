"""
Synthetic Infrastructure Project Monitoring Dataset Generator — v3 (Calibrated)
Calibrated to match the OFFICIAL figures stated in MoSPI / PAIMANA (as of 2026):
  - 1,981 ongoing projects
  - 17 Central Ministries/Departments
  - 22 infrastructure sectors
  - 36 States and Union Territories (including Ladakh, Jammu and Kashmir, Himachal Pradesh, Uttarakhand)
  - Aggregate original cost   ~ Rs 37.13 lakh crore
  - Aggregate revised cost    ~ Rs 42.78 lakh crore
  - Cumulative expenditure    ~ Rs 20.36 lakh crore
Exact figures for states highlighted in MoSPI reports:
  - Ladakh: 9 projects, Orig: ₹52,745.96 Cr, Rev: ₹41,982.80 Cr, Exp: ₹31,642.63 Cr
  - Jammu and Kashmir: 52 projects, Orig: ₹172,125.46 Cr, Rev: ₹119,458.58 Cr, Exp: ₹114,037.36 Cr
  - Himachal Pradesh: 37 projects, Orig: ₹143,839.41 Cr, Rev: ₹96,645.29 Cr, Exp: ₹102,900.15 Cr
  - Uttarakhand: 52 projects, Orig: ₹146,179.29 Cr, Rev: ₹96,740.21 Cr, Exp: ₹103,701.12 Cr
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

np.random.seed(42)
random.seed(42)

SECTOR_MINISTRY = {
    "Roads & Highways": "Ministry of Road Transport & Highways",
    "Railways": "Ministry of Railways",
    "Ports & Shipping": "Ministry of Ports, Shipping & Waterways",
    "Inland Waterways": "Ministry of Ports, Shipping & Waterways",
    "Civil Aviation": "Ministry of Civil Aviation",
    "Power": "Ministry of Power",
    "Renewable Energy": "Ministry of New & Renewable Energy",
    "Petroleum & Natural Gas": "Ministry of Petroleum & Natural Gas",
    "Coal": "Ministry of Coal",
    "Steel": "Ministry of Steel",
    "Mining": "Ministry of Mines",
    "Irrigation": "Ministry of Jal Shakti",
    "Water Resources": "Ministry of Jal Shakti",
    "Water Supply & Sanitation": "Ministry of Jal Shakti",
    "Urban Development": "Ministry of Housing & Urban Affairs",
    "Housing": "Ministry of Housing & Urban Affairs",
    "Telecommunications": "Ministry of Communications",
    "Postal Infrastructure": "Ministry of Communications",
    "Healthcare Infrastructure": "Ministry of Health & Family Welfare",
    "Education Infrastructure": "Ministry of Education",
    "Fertilizers": "Ministry of Chemicals & Fertilizers",
    "Rural Infrastructure": "Ministry of Rural Development",
}
sectors = list(SECTOR_MINISTRY.keys())
assert len(sectors) == 22
assert len(set(SECTOR_MINISTRY.values())) == 17

delay_reasons_pool = [
    "Land acquisition delay", "Forest/environment clearance delay",
    "Funding constraints", "Change in project scope",
    "Contractual issues", "Law and order problems",
    "Geological surprises", "Shortage of skilled manpower",
    "Delay in tendering/equipment supply", "Rehabilitation & resettlement issues",
    "Utility shifting delay", "Court cases/litigation",
    "Price escalation of raw materials", "Poor contractor mobilization",
    "COVID-19 related disruption", "Monsoon/weather delays"
]

implementing_agencies = [
    "NHAI", "IRCON", "RVNL", "NTPC", "PowerGrid", "GAIL", "ONGC",
    "Coal India Ltd", "NBCC", "RITES", "IRCTC", "AAI", "SAIL",
    "State PWD", "State Irrigation Dept", "BSNL", "HUDCO", "NHPC",
    "IWAI", "Deendayal Port Trust", "NMDC", "IFFCO", "ABC Infrastructure Ltd."
]

contractor_names = [
    "Larsen & Toubro Infra", "Shapoorji Pallonji Infra", "Afcons Infrastructure",
    "GMR Infrastructure", "GR Infraprojects", "KNR Constructions",
    "Dilip Buildcon Ltd", "IRB Infrastructure", "NCC Limited",
    "HCC (Hindustan Construction)", "Tata Projects", "Reliance Infrastructure",
    "Simplex Infrastructures", "Gammon India", "Ashoka Buildcon",
    "Sadbhav Engineering", "PNC Infratech", "Megha Engineering (MEIL)",
    "J Kumar Infraprojects", "Patel Engineering"
]
contractor_weights = np.array([1 / (i + 1) for i in range(len(contractor_names))])
contractor_weights = contractor_weights / contractor_weights.sum()

import json

calibrated_file = os.path.join(os.path.dirname(__file__), "calibrated_targets.json")
with open(calibrated_file, "r") as f:
    STATE_TARGETS = json.load(f)

total_projects_target = sum(t['count'] for t in STATE_TARGETS.values())
assert total_projects_target == 1981, f"Expected 1981 projects, got {total_projects_target}"


rows = []
proj_id_counter = 1

for state, tgt in STATE_TARGETS.items():
    cnt = tgt['count']
    total_orig = tgt['orig']
    total_rev = tgt['rev']
    total_exp = tgt['exp']

    # Distribute totals across projects in this state with Dirichlet distribution
    if cnt == 1:
        orig_costs = np.array([total_orig])
        rev_costs = np.array([total_rev])
        exp_costs = np.array([total_exp])
    else:
        raw_orig_w = np.random.dirichlet(np.ones(cnt) * 3)
        orig_costs = np.round(raw_orig_w * total_orig, 2)
        orig_costs[-1] = round(total_orig - orig_costs[:-1].sum(), 2)

        raw_rev_w = np.random.dirichlet(np.ones(cnt) * 3)
        rev_costs = np.round(raw_rev_w * total_rev, 2)
        rev_costs[-1] = round(total_rev - rev_costs[:-1].sum(), 2)

        raw_exp_w = np.random.dirichlet(np.ones(cnt) * 3)
        exp_costs = np.round(raw_exp_w * total_exp, 2)
        exp_costs[-1] = round(total_exp - exp_costs[:-1].sum(), 2)

    for i in range(cnt):
        orig_cost = round(float(orig_costs[i]), 2)
        rev_cost = round(float(rev_costs[i]), 2)
        exp_cost = round(float(exp_costs[i]), 2)

        sector = random.choice(sectors)
        ministry = SECTOR_MINISTRY[sector]
        agency = random.choice(implementing_agencies)
        contractor = np.random.choice(contractor_names, p=contractor_weights)

        planned_duration_months = int(np.random.choice(
            [24, 36, 48, 60, 72, 84, 96], p=[0.1, 0.2, 0.25, 0.2, 0.13, 0.08, 0.04]
        ))
        start_date = datetime(2017, 1, 1) + timedelta(days=random.randint(0, 365 * 6))
        planned_completion = start_date + timedelta(days=planned_duration_months * 30)

        # Realistic delay generation
        is_delayed = bool(rev_cost > orig_cost * 1.03 or np.random.random() < 0.28)
        if is_delayed:
            delay_months = int(np.random.randint(4, 52))
        else:
            delay_months = 0

        cost_overrun_pct = round(max(0.0, (rev_cost - orig_cost) / orig_cost * 100), 2)
        has_cost_overrun = bool(cost_overrun_pct > 2.0)
        actual_or_expected_completion = planned_completion + timedelta(days=delay_months * 30)
        actual_duration_months = planned_duration_months + delay_months

        today_sim = datetime(2026, 4, 1)
        elapsed_months = max(1, (today_sim - start_date).days / 30)
        progress_fraction = min(1.0, elapsed_months / max(actual_duration_months, 1))

        if is_delayed:
            physical_progress_pct = round(max(10.0, min(94.0, progress_fraction * 100 * np.random.uniform(0.7, 0.95))), 1)
        else:
            physical_progress_pct = round(max(15.0, min(100.0, progress_fraction * 100 * np.random.uniform(0.85, 1.1))), 1)
        physical_progress_pct = min(physical_progress_pct, 100.0)

        # Status: MoSPI screenshots show 0 completed for Ladakh, J&K, HP, Uttarakhand during current month
        if state in ['Ladakh', 'Jammu and Kashmir', 'Himachal Pradesh', 'Uttarakhand']:
            status = "Delayed" if is_delayed else "On Track"
        else:
            status = "Completed" if physical_progress_pct >= 98.0 else ("Delayed" if is_delayed else "On Track")

        expenditure_pct = round(min(100.0, (exp_cost / rev_cost) * 100), 1)
        fund_utilization_pct = round(min(100.0, (exp_cost / orig_cost) * 100), 1)

        milestones_total = random.choice([4, 6, 8, 10, 12])
        milestones_completed = min(milestones_total, int(round(milestones_total * (physical_progress_pct / 100.0))))

        num_reasons = random.randint(1, 2) if is_delayed else 0
        reasons = random.sample(delay_reasons_pool, num_reasons) if num_reasons > 0 else []

        # Risk calculation
        risk_score_raw = (
            (delay_months / 60) * 45 +
            (cost_overrun_pct / 50) * 35 +
            (1 - milestones_completed / milestones_total) * 15 +
            (1 - fund_utilization_pct / 100) * 5
        )
        risk_score = round(float(np.clip(risk_score_raw + np.random.normal(0, 3), 0, 100)), 1)
        if risk_score > 50:
            risk_label = "High"
        elif risk_score > 25:
            risk_label = "Medium"
        else:
            risk_label = "Low"

        pid = f"PRJ{proj_id_counter:05d}"
        proj_name = f"{state} {sector} Infra Development Phase-{i+1}"

        rows.append({
            "project_id": pid,
            "project_name": proj_name,
            "sector": sector,
            "ministry": ministry,
            "implementing_agency": agency,
            "contractor_name": contractor,
            "state": state,
            "original_cost_crore": orig_cost,
            "revised_cost_crore": rev_cost,
            "cost_overrun_pct": cost_overrun_pct,
            "has_cost_overrun": has_cost_overrun,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "planned_duration_months": planned_duration_months,
            "actual_duration_months": actual_duration_months,
            "planned_completion_date": planned_completion.strftime("%Y-%m-%d"),
            "expected_actual_completion_date": actual_or_expected_completion.strftime("%Y-%m-%d"),
            "delay_months": delay_months,
            "is_delayed": is_delayed,
            "physical_progress_pct": physical_progress_pct,
            "expenditure_pct": expenditure_pct,
            "expenditure_crore": exp_cost,
            "fund_utilization_pct": fund_utilization_pct,
            "milestones_total": milestones_total,
            "milestones_completed": milestones_completed,
            "delay_reasons": "; ".join(reasons) if reasons else "None",
            "status": status,
            "risk_score": risk_score,
            "risk_label": risk_label
        })
        proj_id_counter += 1

df = pd.DataFrame(rows)
cols = [
    "project_id", "project_name", "sector", "ministry", "implementing_agency", "contractor_name",
    "state", "original_cost_crore", "revised_cost_crore", "cost_overrun_pct", "has_cost_overrun",
    "start_date", "planned_duration_months", "actual_duration_months", "planned_completion_date",
    "expected_actual_completion_date", "delay_months", "is_delayed", "physical_progress_pct",
    "expenditure_pct", "expenditure_crore", "fund_utilization_pct",
    "milestones_total", "milestones_completed", "delay_reasons", "status", "risk_score", "risk_label"
]
df = df[cols]

out_csv = os.path.join(os.path.dirname(__file__), "dataset.csv")
df.to_csv(out_csv, index=False)

print(f"Generated {len(df)} rows across {df['sector'].nunique()} sectors, {df['ministry'].nunique()} ministries, {df['state'].nunique()} states/UTs")
print(f"Total original cost: Rs {df['original_cost_crore'].sum()/100000:.2f} lakh crore")
print(f"Total revised cost: Rs {df['revised_cost_crore'].sum()/100000:.2f} lakh crore")
print(f"Total cumulative expenditure: Rs {df['expenditure_crore'].sum()/100000:.2f} lakh crore")

for check_state in ['Ladakh', 'Jammu and Kashmir', 'Himachal Pradesh', 'Uttarakhand']:
    sdf = df[df['state'] == check_state]
    print(f"[{check_state}] Projects: {len(sdf)}, Orig: {sdf['original_cost_crore'].sum():.2f} Cr, Rev: {sdf['revised_cost_crore'].sum():.2f} Cr, Exp: {sdf['expenditure_crore'].sum():.2f} Cr")
