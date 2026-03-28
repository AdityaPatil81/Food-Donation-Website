import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime
import json

# --- SQL status constants (auto-added fix) ---
# --- SQL status constants (fixed) ---
MATCHED = "status='matched'"
PENDING = "status='pending'"
DELIVERED = "status='delivered'"


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FeedBridge",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:       #0a0f0a;
    --bg2:      #0f1a0f;
    --bg3:      #142014;
    --card:     #111a11;
    --border:   #1e3a1e;
    --green:    #22c55e;
    --green2:   #16a34a;
    --green3:   #4ade80;
    --green4:   #bbf7d0;
    --text:     #e2f0e2;
    --muted:    #6b9e6b;
    --accent:   #86efac;
    --red:      #f87171;
    --yellow:   #fbbf24;
    --orange:   #fb923c;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding: 1.5rem 2rem !important; max-width: 1200px !important; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}
.hero-logo {
    font-family: 'Space Mono', monospace;
    font-size: 3.2rem;
    font-weight: 700;
    color: var(--green);
    letter-spacing: -1px;
    line-height: 1;
    text-shadow: 0 0 40px rgba(34,197,94,0.3);
}
.hero-logo span { color: var(--green3); }
.hero-tagline {
    color: var(--muted);
    font-size: 0.9rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.4rem;
    font-family: 'Space Mono', monospace;
}
.hero-line {
    width: 80px; height: 2px;
    background: linear-gradient(90deg, transparent, var(--green), transparent);
    margin: 1.2rem auto;
}

/* ── Role cards ── */
.role-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.2rem;
    margin: 2rem 0;
}
.role-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 1.2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.role-card::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(34,197,94,0.05), transparent);
    opacity: 0;
    transition: opacity 0.25s;
}
.role-card:hover::before { opacity: 1; }
.role-card:hover {
    border-color: var(--green);
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(34,197,94,0.15);
}
.role-icon { font-size: 2.8rem; margin-bottom: 0.8rem; }
.role-title {
    font-size: 1rem; font-weight: 700;
    color: var(--green3); letter-spacing: 0.5px;
}
.role-desc { font-size: 0.75rem; color: var(--muted); margin-top: 0.4rem; line-height: 1.5; }

/* ── Section header ── */
.section-header {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 1.5rem; padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--border);
}
.section-header h2 {
    font-size: 1.4rem; font-weight: 800;
    color: var(--green3); margin: 0;
}
.section-badge {
    background: rgba(34,197,94,0.1);
    border: 1px solid var(--green2);
    color: var(--green);
    font-size: 0.7rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 1px; text-transform: uppercase;
    font-family: 'Space Mono', monospace;
}

/* ── Cards ── */
.info-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.info-card.match {
    border-color: var(--green);
    box-shadow: 0 0 20px rgba(34,197,94,0.1);
}
.info-card.demand { border-left: 3px solid var(--orange); }
.info-card.donation { border-left: 3px solid var(--green); }
.info-card.volunteer { border-left: 3px solid #60a5fa; }

.card-title {
    font-size: 0.85rem; font-weight: 700;
    color: var(--accent); margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 0.5rem;
}
.card-row {
    display: flex; flex-wrap: wrap; gap: 0.6rem;
    font-size: 0.78rem; color: var(--muted);
}
.card-tag {
    background: rgba(34,197,94,0.08);
    border: 1px solid var(--border);
    padding: 2px 8px; border-radius: 6px;
    color: var(--text); font-size: 0.72rem;
}
.card-tag.green { border-color: var(--green2); color: var(--green3); }
.card-tag.orange { border-color: #92400e; color: var(--orange); }
.card-tag.blue { border-color: #1e40af; color: #93c5fd; }

/* ── Status pills ── */
.pill {
    display: inline-block;
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.7rem; font-weight: 700;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.5px;
}
.pill-green { background: rgba(34,197,94,0.15); color: var(--green3); border: 1px solid var(--green2); }
.pill-red   { background: rgba(248,113,113,0.15); color: var(--red);    border: 1px solid #991b1b; }
.pill-yellow{ background: rgba(251,191,36,0.15);  color: var(--yellow); border: 1px solid #92400e; }
.pill-blue  { background: rgba(96,165,250,0.15);  color: #93c5fd;       border: 1px solid #1e40af; }
.pill-orange{ background: rgba(251,146,60,0.15);  color: var(--orange); border: 1px solid #92400e; }

/* ── Match alert ── */
.match-alert {
    background: linear-gradient(135deg, rgba(34,197,94,0.08), rgba(34,197,94,0.03));
    border: 1px solid var(--green);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    position: relative;
}
.match-alert-title {
    font-size: 0.9rem; font-weight: 800;
    color: var(--green3); margin-bottom: 0.6rem;
}
.match-vs {
    display: flex; align-items: center; gap: 1rem;
    flex-wrap: wrap;
}
.match-side {
    flex: 1; min-width: 140px;
    background: rgba(0,0,0,0.3); border-radius: 8px;
    padding: 0.6rem 0.8rem;
}
.match-arrow { color: var(--green3); font-size: 1.4rem; font-weight: 700; }

/* ── Metric boxes ── */
.metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.metric-box {
    flex: 1; min-width: 100px;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 1rem;
    text-align: center;
}
.metric-val { font-size: 2rem; font-weight: 800; color: var(--green3); font-family: 'Space Mono', monospace; }
.metric-lbl { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.2rem; }

/* ── Forms ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px rgba(34,197,94,0.1) !important;
}
label, .stSelectbox label, .stTextInput label { color: var(--muted) !important; font-size: 0.8rem !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--green2), var(--green)) !important;
    color: #0a0f0a !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(34,197,94,0.3) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg3) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--card) !important;
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    padding: 4px !important;
    gap: 4px !important;
}
[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: rgba(34,197,94,0.15) !important;
    color: var(--green3) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Alerts ── */
[data-testid="stSuccess"] { background: rgba(34,197,94,0.08) !important; border-left: 3px solid var(--green) !important; }
[data-testid="stError"]   { background: rgba(248,113,113,0.08) !important; border-left: 3px solid var(--red) !important; }
[data-testid="stWarning"] { background: rgba(251,191,36,0.08) !important; border-left: 3px solid var(--yellow) !important; }
[data-testid="stInfo"]    { background: rgba(96,165,250,0.08) !important; border-left: 3px solid #60a5fa !important; }

/* ── Back button ── */
.back-btn { margin-bottom: 1.5rem; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--green2); }

/* ── Login/Register card ── */
.auth-card {
    max-width: 440px; margin: 2rem auto;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 18px; padding: 2.5rem;
}
.auth-title {
    font-size: 1.3rem; font-weight: 800;
    color: var(--green3); margin-bottom: 0.3rem;
}
.auth-sub { font-size: 0.8rem; color: var(--muted); margin-bottom: 1.8rem; }

/* ── Step indicator ── */
.steps { display: flex; gap: 0.5rem; margin-bottom: 1.2rem; flex-wrap: wrap; }
.step {
    font-size: 0.7rem; font-family: 'Space Mono', monospace;
    padding: 4px 10px; border-radius: 6px;
    background: var(--bg3); border: 1px solid var(--border);
    color: var(--muted);
}
.step.active { background: rgba(34,197,94,0.12); border-color: var(--green2); color: var(--green3); }
</style>
""", unsafe_allow_html=True)

# ── DATABASE ───────────────────────────────────────────────────────────────────
DB_PATH = "iotfeedbridge.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        contact TEXT,
        email TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS food_donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER,
        donor_name TEXT,
        org_name TEXT,
        contact TEXT,
        food_type TEXT,
        food_category TEXT,
        quantity REAL,
        quantity_unit TEXT,
        prep_time TEXT,
        pickup_address TEXT,
        special_instructions TEXT,
        status TEXT DEFAULT 'pending',
        matched_ngo_id INTEGER,
        assigned_volunteer_id INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS ngo_demands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ngo_id INTEGER,
        ngo_name TEXT,
        contact_person TEXT,
        contact TEXT,
        email TEXT,
        ngo_address TEXT,
        service_area TEXT,
        max_capacity INTEGER,
        storage_available TEXT,
        food_type_needed TEXT,
        quantity_needed REAL,
        quantity_unit TEXT,
        priority TEXT DEFAULT 'Medium',
        remarks TEXT,
        status TEXT DEFAULT 'pending',
        matched_donation_id INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS ngo_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ngo_id INTEGER,
        donation_id INTEGER,
        action TEXT,
        quantity_accepted REAL,
        preferred_pickup_time TEXT,
        priority TEXT,
        remarks TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS volunteer_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER,
        donation_id INTEGER,
        pickup_location TEXT,
        drop_location TEXT,
        assigned_time TEXT,
        delivery_status TEXT DEFAULT 'Assigned',
        remarks TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )""")

    conn.commit()
    conn.close()

init_db()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def register_user(username, password, role, full_name, contact, email):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (username,password,role,full_name,contact,email) VALUES (?,?,?,?,?,?)",
                     (username, hash_pw(password), role, full_name, contact, email))
        conn.commit()
        return True, "Registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

def login_user(username, password, role):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?",
                       (username, hash_pw(password), role)).fetchone()
    conn.close()
    return dict(row) if row else None

def find_matches():
    conn = get_conn()
    donations = conn.execute(
        "SELECT * FROM food_donations WHERE status='pending'"
    ).fetchall()
    demands = conn.execute(
        "SELECT * FROM ngo_demands WHERE status='pending'"
    ).fetchall()
    conn.close()
    matches = []
    for don in donations:
        for dem in demands:
            score = 0
            if don['food_type'] and dem['food_type_needed']:
                if don['food_type'].lower() == dem['food_type_needed'].lower(): score += 3
            if don['quantity'] and dem['quantity_needed']:
                if don['quantity'] >= dem['quantity_needed']: score += 2
            if score >= 2:
                matches.append({'donation': dict(don), 'demand': dict(dem), 'score': score})
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches

def db_count(table, where="1=1"):
    conn = get_conn()
    val = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}").fetchone()[0]
    conn.close()
    return val

# ── TRANSLATIONS ──────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "English": {
        "tagline": "Connecting food donors · NGOs · Volunteers through intelligent matching",
        "enter_as": "Enter as",
        "donations": "Donations", "demands": "Demands", "matched": "Matched", "deliveries": "Deliveries",
        "back_home": "← Back to Home", "login": "🔐  Login", "register": "📝  Register",
        "username": "Username", "password": "Password", "login_btn": "Login",
        "full_name": "Full Name / Organization Name", "contact": "Contact Number",
        "email": "Email ID", "choose_username": "Choose Username",
        "choose_password": "Choose Password", "confirm_password": "Confirm Password",
        "create_account": "Create Account", "logout": "Logout",
        "welcome": "Welcome",
        # Donor
        "donor_dashboard": "🍽️ Food Donor Dashboard", "submit_donation": "➕  Submit Donation",
        "my_donations": "📋  My Donations", "donor_name": "Donor Name",
        "org_name": "Organization / Restaurant Name", "food_type": "Type of Food",
        "food_cat": "Food Category", "qty_unit": "Quantity Unit", "quantity": "Quantity",
        "prep_time": "Time of Preparation (e.g. 2:00 PM)", "pickup_addr": "Pickup Address",
        "special_inst": "Special Instructions (optional)", "submit_donation_btn": "🚀 Submit Donation",
        "donation_success": "✅ Donation submitted! Organization will coordinate pickup.",
        "fill_required": "Please fill all required fields.",
        # NGO
        "ngo_dashboard": "🤝 NGO Dashboard", "post_demand": "📢  Post Demand",
        "my_demands": "📋  My Demands", "matched_donations": "🔔  Matched Donations",
        "ngo_name": "NGO Name", "contact_person": "Contact Person Name",
        "ngo_address": "NGO Address", "service_area": "Service Area (City / Radius)",
        "max_capacity": "Maximum Capacity (people)", "storage": "Storage Facility Available",
        "food_needed": "Food Type Needed", "qty_needed": "Quantity Needed",
        "unit": "Unit", "priority": "Priority Level", "remarks": "Remarks (optional)",
        "post_demand_btn": "📢 Post Food Demand",
        "demand_success": "✅ Demand posted! Organization will review and match.",
        "no_demands": "No demands posted yet.", "no_donations": "No donations yet. Submit your first one!",
        "no_matched": "No matched donations yet. Post a demand and the Organization will match it.",
        "respond": "📝 Respond to this Donation", "action": "Action",
        "qty_accept": "Quantity to Accept", "preferred_time": "Preferred Pickup Time",
        "submit_response": "Submit Response", "response_submitted": "✅ Response Submitted",
        # Org
        "org_dashboard": "🏢 Organization Dashboard",
        "smart_matches": "🎯  Smart Matches", "all_donations": "🍽️  Donations",
        "ngo_demands_tab": "📢  NGO Demands", "volunteers_tab": "🚴  Volunteers",
        "total_donations": "Total Donations", "pending": "Pending",
        "ngo_demands_lbl": "NGO Demands", "active_deliveries": "Active Deliveries",
        "smart_match_title": "🤖 AI-Suggested Matches",
        "no_matches": "No pending matches found. Waiting for donations and demands to align.",
        "approve_match": "✅ Approve Match", "match_approved": "Match approved! NGO and Donor notified.",
        "strong_match": "🔥 Strong Match", "good_match": "✅ Good Match",
        "donor_lbl": "🍱 DONOR", "ngo_lbl": "🤝 NGO",
        "assign_vol": "Assign Volunteers to Matched Donations",
        "no_matched_dons": "No matched donations awaiting volunteer assignment.",
        "assign_volunteer": "Assign Volunteer", "drop_loc": "Drop Location (NGO Address)",
        "assigned_time": "Assigned Time", "assign_btn": "Assign",
        "no_volunteers": "No volunteers registered yet.",
        "active_assignments": "Active Assignments", "no_assignments": "No assignments yet.",
        # Volunteer
        "vol_dashboard": "🚴 Volunteer Dashboard",
        "my_assignments": "📦  My Assignments", "my_profile": "👤  My Profile",
        "no_assign": "No assignments yet. The Organization will assign pickups to you.",
        "vehicle": "Vehicle Type", "availability": "Availability Status",
        "current_loc": "Current Location", "update_profile": "Update Profile",
        "profile_updated": "Profile updated!", "update_status": "Update Status",
        "total_assignments": "Total Assignments", "delivered": "Delivered",
        "assignment_lbl": "Assignment", "pickup": "Pickup", "drop": "Drop",
        # Auth messages
        "invalid_creds": "Invalid credentials or wrong role.",
        "pwd_mismatch": "Passwords don't match.",
        "reg_success": "Registered successfully! Please login.",
        "username_exists": "Username already exists.",
        "lang_label": "🌐 Language",
        "serves": "Serves", "storage_lbl": "Storage", "cap_lbl": "Cap",
        "needs_volunteer": "Needs Volunteer",
        "matched_donation": "✅ Matched Donation",
    },
    "मराठी": {
        "tagline": "अन्नदाते · NGO · स्वयंसेवक यांना बुद्धिमान जुळणीद्वारे जोडणे",
        "enter_as": "म्हणून प्रवेश करा",
        "donations": "देणग्या", "demands": "मागण्या", "matched": "जुळवलेले", "deliveries": "वितरण",
        "back_home": "← मुख्यपृष्ठावर परत", "login": "🔐  लॉगिन", "register": "📝  नोंदणी",
        "username": "वापरकर्तानाव", "password": "पासवर्ड", "login_btn": "लॉगिन",
        "full_name": "पूर्ण नाव / संस्थेचे नाव", "contact": "संपर्क क्रमांक",
        "email": "ईमेल आयडी", "choose_username": "वापरकर्तानाव निवडा",
        "choose_password": "पासवर्ड निवडा", "confirm_password": "पासवर्ड पुष्टी करा",
        "create_account": "खाते तयार करा", "logout": "लॉगआउट",
        "welcome": "स्वागत",
        "donor_dashboard": "🍽️ अन्नदाता डॅशबोर्ड", "submit_donation": "➕  देणगी सादर करा",
        "my_donations": "📋  माझ्या देणग्या", "donor_name": "दात्याचे नाव",
        "org_name": "संस्था / हॉटेलचे नाव", "food_type": "अन्नाचा प्रकार",
        "food_cat": "अन्न श्रेणी", "qty_unit": "प्रमाण एकक", "quantity": "प्रमाण",
        "prep_time": "तयारीची वेळ (उदा. दुपारी 2:00)", "pickup_addr": "पिकअप पत्ता",
        "special_inst": "विशेष सूचना (पर्यायी)", "submit_donation_btn": "🚀 देणगी सादर करा",
        "donation_success": "✅ देणगी सादर केली! संस्था पिकअपचे समन्वय करेल.",
        "fill_required": "कृपया सर्व आवश्यक माहिती भरा.",
        "ngo_dashboard": "🤝 NGO डॅशबोर्ड", "post_demand": "📢  मागणी नोंदवा",
        "my_demands": "📋  माझ्या मागण्या", "matched_donations": "🔔  जुळलेल्या देणग्या",
        "ngo_name": "NGO चे नाव", "contact_person": "संपर्क व्यक्तीचे नाव",
        "ngo_address": "NGO चा पत्ता", "service_area": "सेवा क्षेत्र (शहर / परिघ)",
        "max_capacity": "कमाल क्षमता (लोक)", "storage": "साठवण सुविधा उपलब्ध",
        "food_needed": "आवश्यक अन्न प्रकार", "qty_needed": "आवश्यक प्रमाण",
        "unit": "एकक", "priority": "प्राधान्य पातळी", "remarks": "शेरा (पर्यायी)",
        "post_demand_btn": "📢 अन्न मागणी नोंदवा",
        "demand_success": "✅ मागणी नोंदवली! संस्था आढावा घेऊन जुळवेल.",
        "no_demands": "अद्याप कोणतीही मागणी नाही.", "no_donations": "अद्याप देणगी नाही. पहिली देणगी द्या!",
        "no_matched": "अद्याप जुळलेल्या देणग्या नाहीत. मागणी नोंदवा.",
        "respond": "📝 या देणगीला प्रतिसाद द्या", "action": "कृती",
        "qty_accept": "स्वीकारायचे प्रमाण", "preferred_time": "पसंतीची पिकअप वेळ",
        "submit_response": "प्रतिसाद सादर करा", "response_submitted": "✅ प्रतिसाद सादर केला",
        "org_dashboard": "🏢 संस्था डॅशबोर्ड",
        "smart_matches": "🎯  स्मार्ट जुळणी", "all_donations": "🍽️  देणग्या",
        "ngo_demands_tab": "📢  NGO मागण्या", "volunteers_tab": "🚴  स्वयंसेवक",
        "total_donations": "एकूण देणग्या", "pending": "प्रलंबित",
        "ngo_demands_lbl": "NGO मागण्या", "active_deliveries": "सक्रिय वितरण",
        "smart_match_title": "🤖 AI-सुचवलेल्या जुळण्या",
        "no_matches": "कोणत्याही प्रलंबित जुळण्या नाहीत.",
        "approve_match": "✅ जुळणी मंजूर करा", "match_approved": "जुळणी मंजूर! NGO आणि दात्याला कळवले.",
        "strong_match": "🔥 मजबूत जुळणी", "good_match": "✅ चांगली जुळणी",
        "donor_lbl": "🍱 दाता", "ngo_lbl": "🤝 NGO",
        "assign_vol": "जुळलेल्या देणग्यांसाठी स्वयंसेवक नियुक्त करा",
        "no_matched_dons": "स्वयंसेवक नियुक्तीसाठी कोणतीही देणगी नाही.",
        "assign_volunteer": "स्वयंसेवक नियुक्त करा", "drop_loc": "ड्रॉप स्थान (NGO पत्ता)",
        "assigned_time": "नियुक्त वेळ", "assign_btn": "नियुक्त करा",
        "no_volunteers": "अद्याप कोणताही स्वयंसेवक नोंदणीकृत नाही.",
        "active_assignments": "सक्रिय नियुक्त्या", "no_assignments": "अद्याप नियुक्त्या नाहीत.",
        "vol_dashboard": "🚴 स्वयंसेवक डॅशबोर्ड",
        "my_assignments": "📦  माझ्या नियुक्त्या", "my_profile": "👤  माझे प्रोफाइल",
        "no_assign": "अद्याप नियुक्त्या नाहीत. संस्था पिकअप नियुक्त करेल.",
        "vehicle": "वाहन प्रकार", "availability": "उपलब्धता स्थिती",
        "current_loc": "सध्याचे स्थान", "update_profile": "प्रोफाइल अपडेट करा",
        "profile_updated": "प्रोफाइल अपडेट केले!", "update_status": "स्थिती अपडेट करा",
        "total_assignments": "एकूण नियुक्त्या", "delivered": "वितरित",
        "assignment_lbl": "नियुक्ती", "pickup": "पिकअप", "drop": "ड्रॉप",
        "invalid_creds": "चुकीची माहिती किंवा चुकीची भूमिका.",
        "pwd_mismatch": "पासवर्ड जुळत नाहीत.",
        "reg_success": "नोंदणी यशस्वी! कृपया लॉगिन करा.",
        "username_exists": "वापरकर्तानाव आधीच अस्तित्वात आहे.",
        "lang_label": "🌐 भाषा",
        "serves": "सेवा", "storage_lbl": "साठवण", "cap_lbl": "क्षमता",
        "needs_volunteer": "स्वयंसेवक आवश्यक",
        "matched_donation": "✅ जुळलेली देणगी",
    },
    "हिंदी": {
        "tagline": "खाद्य दाताओं · NGO · स्वयंसेवकों को बुद्धिमान मिलान से जोड़ना",
        "enter_as": "के रूप में प्रवेश करें",
        "donations": "दान", "demands": "मांगें", "matched": "मिलान", "deliveries": "डिलीवरी",
        "back_home": "← होम पर वापस", "login": "🔐  लॉगिन", "register": "📝  पंजीकरण",
        "username": "उपयोगकर्ता नाम", "password": "पासवर्ड", "login_btn": "लॉगिन",
        "full_name": "पूरा नाम / संस्था का नाम", "contact": "संपर्क नंबर",
        "email": "ईमेल आईडी", "choose_username": "उपयोगकर्ता नाम चुनें",
        "choose_password": "पासवर्ड चुनें", "confirm_password": "पासवर्ड की पुष्टि करें",
        "create_account": "खाता बनाएं", "logout": "लॉगआउट",
        "welcome": "स्वागत है",
        "donor_dashboard": "🍽️ खाद्य दाता डैशबोर्ड", "submit_donation": "➕  दान जमा करें",
        "my_donations": "📋  मेरे दान", "donor_name": "दाता का नाम",
        "org_name": "संस्था / रेस्तरां का नाम", "food_type": "भोजन का प्रकार",
        "food_cat": "भोजन श्रेणी", "qty_unit": "मात्रा इकाई", "quantity": "मात्रा",
        "prep_time": "तैयारी का समय (जैसे दोपहर 2:00)", "pickup_addr": "पिकअप पता",
        "special_inst": "विशेष निर्देश (वैकल्पिक)", "submit_donation_btn": "🚀 दान जमा करें",
        "donation_success": "✅ दान जमा हुआ! संस्था पिकअप समन्वय करेगी।",
        "fill_required": "कृपया सभी आवश्यक फ़ील्ड भरें।",
        "ngo_dashboard": "🤝 NGO डैशबोर्ड", "post_demand": "📢  मांग दर्ज करें",
        "my_demands": "📋  मेरी मांगें", "matched_donations": "🔔  मिलान किए गए दान",
        "ngo_name": "NGO का नाम", "contact_person": "संपर्क व्यक्ति का नाम",
        "ngo_address": "NGO का पता", "service_area": "सेवा क्षेत्र (शहर / दायरा)",
        "max_capacity": "अधिकतम क्षमता (लोग)", "storage": "भंडारण सुविधा उपलब्ध",
        "food_needed": "आवश्यक भोजन प्रकार", "qty_needed": "आवश्यक मात्रा",
        "unit": "इकाई", "priority": "प्राथमिकता स्तर", "remarks": "टिप्पणी (वैकल्पिक)",
        "post_demand_btn": "📢 खाद्य मांग दर्ज करें",
        "demand_success": "✅ मांग दर्ज की गई! संस्था समीक्षा करके मिलान करेगी।",
        "no_demands": "अभी तक कोई मांग नहीं।", "no_donations": "अभी तक दान नहीं। पहला दान करें!",
        "no_matched": "अभी तक कोई मिलान नहीं। मांग दर्ज करें।",
        "respond": "📝 इस दान पर प्रतिक्रिया दें", "action": "कार्रवाई",
        "qty_accept": "स्वीकार करने की मात्रा", "preferred_time": "पसंदीदा पिकअप समय",
        "submit_response": "प्रतिक्रिया जमा करें", "response_submitted": "✅ प्रतिक्रिया जमा हुई",
        "org_dashboard": "🏢 संस्था डैशबोर्ड",
        "smart_matches": "🎯  स्मार्ट मिलान", "all_donations": "🍽️  दान",
        "ngo_demands_tab": "📢  NGO मांगें", "volunteers_tab": "🚴  स्वयंसेवक",
        "total_donations": "कुल दान", "pending": "लंबित",
        "ngo_demands_lbl": "NGO मांगें", "active_deliveries": "सक्रिय डिलीवरी",
        "smart_match_title": "🤖 AI-सुझाए गए मिलान",
        "no_matches": "कोई लंबित मिलान नहीं मिला।",
        "approve_match": "✅ मिलान स्वीकृत करें", "match_approved": "मिलान स्वीकृत! NGO और दाता को सूचित किया।",
        "strong_match": "🔥 मजबूत मिलान", "good_match": "✅ अच्छा मिलान",
        "donor_lbl": "🍱 दाता", "ngo_lbl": "🤝 NGO",
        "assign_vol": "मिलान किए गए दान के लिए स्वयंसेवक नियुक्त करें",
        "no_matched_dons": "स्वयंसेवक नियुक्ति के लिए कोई दान नहीं।",
        "assign_volunteer": "स्वयंसेवक नियुक्त करें", "drop_loc": "ड्रॉप स्थान (NGO पता)",
        "assigned_time": "नियुक्त समय", "assign_btn": "नियुक्त करें",
        "no_volunteers": "अभी तक कोई स्वयंसेवक पंजीकृत नहीं।",
        "active_assignments": "सक्रिय नियुक्तियां", "no_assignments": "अभी तक नियुक्तियां नहीं।",
        "vol_dashboard": "🚴 स्वयंसेवक डैशबोर्ड",
        "my_assignments": "📦  मेरी नियुक्तियां", "my_profile": "👤  मेरी प्रोफाइल",
        "no_assign": "अभी तक नियुक्तियां नहीं। संस्था पिकअप नियुक्त करेगी।",
        "vehicle": "वाहन प्रकार", "availability": "उपलब्धता स्थिति",
        "current_loc": "वर्तमान स्थान", "update_profile": "प्रोफाइल अपडेट करें",
        "profile_updated": "प्रोफाइल अपडेट हुई!", "update_status": "स्थिति अपडेट करें",
        "total_assignments": "कुल नियुक्तियां", "delivered": "डिलीवर हुआ",
        "assignment_lbl": "नियुक्ति", "pickup": "पिकअप", "drop": "ड्रॉप",
        "invalid_creds": "गलत क्रेडेंशियल या गलत भूमिका।",
        "pwd_mismatch": "पासवर्ड मेल नहीं खाते।",
        "reg_success": "पंजीकरण सफल! कृपया लॉगिन करें।",
        "username_exists": "उपयोगकर्ता नाम पहले से मौजूद है।",
        "lang_label": "🌐 भाषा",
        "serves": "सेवा", "storage_lbl": "भंडारण", "cap_lbl": "क्षमता",
        "needs_volunteer": "स्वयंसेवक आवश्यक",
        "matched_donation": "✅ मिलान किया गया दान",
    }
}

def T(key):
    lang = st.session_state.get("lang", "English")
    return TRANSLATIONS.get(lang, TRANSLATIONS["English"]).get(key, TRANSLATIONS["English"].get(key, key))

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [("page","home"),("user",None),("role",None),("lang","English")]:
    if k not in st.session_state: st.session_state[k] = v

def go(page): st.session_state.page = page; st.rerun()
def logout(): st.session_state.user = None; st.session_state.role = None; go("home")

# ── LOGO + LANGUAGE SWITCHER ──────────────────────────────────────────────────
def render_logo(small=False):
    size = "1.6rem" if small else "3.2rem"
    if small:
        col_logo, col_lang = st.columns([8, 2])
        with col_logo:
            st.markdown(f"""
            <div style="margin-bottom:0.5rem">
                <div style="font-family:'Space Mono',monospace;font-size:{size};font-weight:700;
                            color:#22c55e;text-shadow:0 0 30px rgba(34,197,94,0.3)">
                    IoT<span style="color:#4ade80">Feed</span>Bridge
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_lang:
            lang = st.selectbox(
                T("lang_label"), ["English","मराठी","हिंदी"],
                index=["English","मराठी","हिंदी"].index(st.session_state.lang),
                key="lang_switch_small", label_visibility="collapsed"
            )
            if lang != st.session_state.lang:
                st.session_state.lang = lang; st.rerun()
    else:
        col1, col2, col3 = st.columns([1, 4, 1])
        with col3:
            lang = st.selectbox(
                T("lang_label"), ["English","मराठी","हिंदी"],
                index=["English","मराठी","हिंदी"].index(st.session_state.lang),
                key="lang_switch_home", label_visibility="visible"
            )
            if lang != st.session_state.lang:
                st.session_state.lang = lang; st.rerun()
        with col2:
            st.markdown(f"""
            <div style="text-align:center">
                <div style="font-family:'Space Mono',monospace;font-size:{size};font-weight:700;
                            color:#22c55e;text-shadow:0 0 40px rgba(34,197,94,0.3)">
                    IoT<span style="color:#4ade80">Feed</span>Bridge
                </div>
                <div style="font-size:0.7rem;color:#6b9e6b;letter-spacing:3px;text-transform:uppercase;font-family:'Space Mono',monospace">
                    Smart Food Distribution Network
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    render_logo()
    st.markdown('<div class="hero-line"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <p style="text-align:center;color:#6b9e6b;font-size:0.85rem;margin-bottom:2rem">
        {T("tagline")}
    </p>
    """, unsafe_allow_html=True)

    roles = [
        ("🍽️", "Food Donors", "Hotels, restaurants & event organizers", "donor"),
        ("🏢", "Organizations", "Central coordination hub", "organization"),
        ("🤝", "NGOs", "Request & receive food donations", "ngo"),
        ("🚴", "Volunteers", "Pickup & delivery logistics", "volunteer"),
    ]

    cols = st.columns(4)
    for i, (icon, title, desc, role) in enumerate(roles):
        with cols[i]:
            st.markdown(f"""
            <div class="role-card" style="margin-bottom:0.5rem">
                <div class="role-icon">{icon}</div>
                <div class="role-title">{title}</div>
                <div class="role-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"{T('enter_as')} {title.split()[0]}", key=f"role_{role}", use_container_width=True):
                st.session_state.role = role
                go("auth")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-box"><div class="metric-val">{db_count("food_donations")}</div><div class="metric-lbl">{T("donations")}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-box"><div class="metric-val">{db_count("ngo_demands")}</div><div class="metric-lbl">{T("demands")}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-box"><div class="metric-val">{db_count("food_donations",MATCHED)}</div><div class="metric-lbl">{T("matched")}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-box"><div class="metric-val">{db_count("volunteer_assignments")}</div><div class="metric-lbl">{T("deliveries")}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUTH
# ══════════════════════════════════════════════════════════════════════════════
def page_auth():
    role = st.session_state.role
    icons = {"donor":"🍽️","organization":"🏢","ngo":"🤝","volunteer":"🚴"}
    labels = {"donor":"Food Donor","organization":"Organization","ngo":"NGO","volunteer":"Volunteer"}

    col1, col2, col3 = st.columns([1,2,1])
    with col3:
        lang = st.selectbox(
            T("lang_label"), ["English","मराठी","हिंदी"],
            index=["English","मराठी","हिंदी"].index(st.session_state.lang),
            key="lang_auth"
        )
        if lang != st.session_state.lang:
            st.session_state.lang = lang; st.rerun()
    with col2:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button(T("back_home")): go("home")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin-bottom:1.5rem">
            <div style="font-size:3rem">{icons[role]}</div>
            <div style="font-size:1.3rem;font-weight:800;color:#4ade80">{labels[role]} Portal</div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs([T("login"), T("register")])

        with tab1:
            with st.form("login_form"):
                uname = st.text_input(T("username"))
                pwd   = st.text_input(T("password"), type="password")
                if st.form_submit_button(T("login_btn"), use_container_width=True):
                    user = login_user(uname, pwd, role)
                    if user:
                        st.session_state.user = user
                        go(f"dashboard_{role}")
                    else:
                        st.error(T("invalid_creds"))

        with tab2:
            with st.form("register_form"):
                full_name = st.text_input(T("full_name"))
                contact   = st.text_input(T("contact"))
                email     = st.text_input(T("email"))
                uname2    = st.text_input(T("choose_username"))
                pwd2      = st.text_input(T("choose_password"), type="password")
                pwd3      = st.text_input(T("confirm_password"), type="password")
                if st.form_submit_button(T("create_account"), use_container_width=True):
                    if pwd2 != pwd3:
                        st.error(T("pwd_mismatch"))
                    elif not all([full_name, contact, uname2, pwd2]):
                        st.error(T("fill_required"))
                    else:
                        ok, msg = register_user(uname2, pwd2, role, full_name, contact, email)
                        if ok: st.success(T("reg_success"))
                        else:  st.error(T("username_exists"))

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD: FOOD DONOR
# ══════════════════════════════════════════════════════════════════════════════
def dashboard_donor():
    user = st.session_state.user
    render_logo(small=True)
    c1, c2 = st.columns([8,1])
    with c1:
        st.markdown(f"""
        <div class="section-header">
            <h2>{T("donor_dashboard")}</h2>
            <span class="section-badge">Donor</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if st.button(T("logout")): logout()

    st.markdown(f'<p style="color:#6b9e6b;font-size:0.82rem;margin-top:-1rem;margin-bottom:1.5rem">{T("welcome")}, <b style="color:#4ade80">{user["full_name"]}</b></p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs([T("submit_donation"), T("my_donations")])

    with tab1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        with st.form("donation_form"):
            c1, c2 = st.columns(2)
            with c1:
                donor_name = st.text_input(T("donor_name"), value=user["full_name"])
                org_name   = st.text_input(T("org_name"))
                contact    = st.text_input(T("contact"), value=user["contact"])
            with c2:
                food_type  = st.selectbox(T("food_type"), ["Veg", "Non-Veg", "Both"])
                food_cat   = st.selectbox(T("food_cat"), ["Cooked", "Packaged", "Both"])
                qty_unit   = st.selectbox(T("qty_unit"), ["Person-wise", "Kg"])

            c3, c4 = st.columns(2)
            with c3:
                quantity   = st.number_input(T("quantity"), min_value=0.0, step=0.5)
                prep_time  = st.text_input(T("prep_time"))
            with c4:
                pickup_addr = st.text_area(T("pickup_addr"), height=80)

            special = st.text_area(T("special_inst"), height=70)

            submitted = st.form_submit_button(T("submit_donation_btn"), use_container_width=True)
            if submitted:
                if not all([donor_name, org_name, quantity, pickup_addr]):
                    st.error(T("fill_required"))
                else:
                    conn = get_conn()
                    conn.execute("""INSERT INTO food_donations
                        (donor_id,donor_name,org_name,contact,food_type,food_category,
                         quantity,quantity_unit,prep_time,pickup_address,special_instructions)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                        (user["id"], donor_name, org_name, contact, food_type, food_cat,
                         quantity, qty_unit, prep_time, pickup_addr, special))
                    conn.commit()
                    conn.close()
                    st.success(T("donation_success"))
                    st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM food_donations WHERE donor_id=? ORDER BY created_at DESC", (user["id"],)).fetchall()
        conn.close()
        if not rows:
            st.info(T("no_donations"))
        for r in rows:
            status_cls = {"pending":"pill-yellow","matched":"pill-green","delivered":"pill-blue"}.get(r["status"],"pill-yellow")
            st.markdown(f"""
            <div class="info-card donation">
                <div class="card-title">
                    🍱 {r['org_name']} — {r['food_type']} / {r['food_category']}
                    <span class="pill {status_cls}">{r['status'].upper()}</span>
                </div>
                <div class="card-row">
                    <span class="card-tag green">📦 {r['quantity']} {r['quantity_unit']}</span>
                    <span class="card-tag">📍 {r['pickup_address'][:40]}...</span>
                    <span class="card-tag">🕐 {r['prep_time']}</span>
                    <span class="card-tag">📅 {r['created_at'][:16]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD: NGO
# ══════════════════════════════════════════════════════════════════════════════
def dashboard_ngo():
    user = st.session_state.user
    render_logo(small=True)
    c1, c2 = st.columns([8,1])
    with c1:
        st.markdown(f"""
        <div class="section-header">
            <h2>{T("ngo_dashboard")}</h2>
            <span class="section-badge">NGO</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if st.button(T("logout")): logout()

    st.markdown(f'<p style="color:#6b9e6b;font-size:0.82rem;margin-top:-1rem;margin-bottom:1.5rem">{T("welcome")}, <b style="color:#4ade80">{user["full_name"]}</b></p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([T("post_demand"), T("my_demands"), T("matched_donations")])

    with tab1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        with st.form("ngo_demand_form"):
            c1, c2 = st.columns(2)
            with c1:
                ngo_name    = st.text_input(T("ngo_name"), value=user["full_name"])
                contact_p   = st.text_input(T("contact_person"))
                contact     = st.text_input(T("contact"), value=user["contact"])
                email       = st.text_input(T("email"), value=user.get("email",""))
            with c2:
                ngo_addr    = st.text_area(T("ngo_address"), height=80)
                service_area= st.text_input(T("service_area"))
                max_cap     = st.number_input(T("max_capacity"), min_value=0, step=10)
                storage     = st.selectbox(T("storage"), ["Yes","No"])

            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                food_needed = st.selectbox(T("food_needed"), ["Veg","Non-Veg","Both"])
                qty_needed  = st.number_input(T("qty_needed"), min_value=0.0, step=0.5)
                qty_unit    = st.selectbox(T("unit"), ["Person-wise","Kg"])
            with c4:
                priority    = st.selectbox(T("priority"), ["High","Medium","Low"])
                remarks     = st.text_area(T("remarks"), height=70)

            if st.form_submit_button(T("post_demand_btn"), use_container_width=True):
                if not all([ngo_name, contact_p, ngo_addr, qty_needed]):
                    st.error(T("fill_required"))
                else:
                    conn = get_conn()
                    conn.execute("""INSERT INTO ngo_demands
                        (ngo_id,ngo_name,contact_person,contact,email,ngo_address,service_area,
                         max_capacity,storage_available,food_type_needed,quantity_needed,
                         quantity_unit,priority,remarks)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (user["id"], ngo_name, contact_p, contact, email, ngo_addr,
                         service_area, max_cap, storage, food_needed, qty_needed,
                         qty_unit, priority, remarks))
                    conn.commit()
                    conn.close()
                    st.success(T("demand_success"))
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM ngo_demands WHERE ngo_id=? ORDER BY created_at DESC", (user["id"],)).fetchall()
        conn.close()
        if not rows:
            st.info(T("no_demands"))
        for r in rows:
            pri_cls = {"High":"pill-red","Medium":"pill-yellow","Low":"pill-green"}.get(r["priority"],"pill-yellow")
            st.markdown(f"""
            <div class="info-card demand">
                <div class="card-title">
                    📢 {r['ngo_name']} — {r['food_type_needed']}
                    <span class="pill {pri_cls}">{r['priority'].upper()}</span>
                    <span class="pill pill-blue" style="margin-left:4px">{r['status'].upper()}</span>
                </div>
                <div class="card-row">
                    <span class="card-tag orange">🍽️ {r['quantity_needed']} {r['quantity_unit']}</span>
                    <span class="card-tag">👥 {T("cap_lbl")}: {r['max_capacity']}</span>
                    <span class="card-tag">📍 {r['ngo_address'][:35]}...</span>
                    <span class="card-tag">📅 {r['created_at'][:16]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        conn = get_conn()
        matched_donations = conn.execute(
            "SELECT fd.* FROM food_donations fd WHERE fd.matched_ngo_id=? AND fd.status IN ('matched','assigned')",
            (user["id"],)
        ).fetchall()
        conn.close()
        if not matched_donations:
            st.info(T("no_matched"))
        for r in matched_donations:
            st.markdown(f"""
            <div class="match-alert">
                <div class="match-alert-title">{T("matched_donation")}</div>
                <div class="card-row">
                    <span class="card-tag green">🍱 {r['food_type']} / {r['food_category']}</span>
                    <span class="card-tag green">📦 {r['quantity']} {r['quantity_unit']}</span>
                    <span class="card-tag">🏪 {r['org_name']}</span>
                    <span class="card-tag">📍 {r['pickup_address'][:35]}...</span>
                    <span class="card-tag">🕐 {r['prep_time']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            conn2 = get_conn()
            existing = conn2.execute("SELECT * FROM ngo_responses WHERE ngo_id=? AND donation_id=?",
                                     (user["id"], r["id"])).fetchone()
            conn2.close()
            if existing:
                st.markdown(f'<span class="pill pill-green" style="margin-left:1rem">{T("response_submitted")}</span>', unsafe_allow_html=True)
            else:
                with st.expander(T("respond")):
                    with st.form(f"ngo_response_{r['id']}"):
                        action  = st.selectbox(T("action"), ["Accept","Reject"], key=f"act_{r['id']}")
                        qty_acc = st.number_input(T("qty_accept"), min_value=0.0,
                                                   max_value=float(r['quantity']), step=0.5, key=f"qty_{r['id']}")
                        ptime   = st.text_input(T("preferred_time"), key=f"pt_{r['id']}")
                        pri     = st.selectbox(T("priority"), ["High","Medium","Low"], index=1, key=f"pri_{r['id']}")
                        rem     = st.text_area(T("remarks"), key=f"rem_{r['id']}")
                        if st.form_submit_button(T("submit_response")):
                            conn3 = get_conn()
                            conn3.execute("""INSERT INTO ngo_responses
                                (ngo_id,donation_id,action,quantity_accepted,preferred_pickup_time,priority,remarks)
                                VALUES (?,?,?,?,?,?,?)""",
                                (user["id"], r["id"], action, qty_acc, ptime, pri, rem))
                            conn3.commit()
                            conn3.close()
                            st.success(T("response_submitted"))
                            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD: ORGANIZATION
# ══════════════════════════════════════════════════════════════════════════════
def dashboard_organization():
    user = st.session_state.user
    render_logo(small=True)
    c1, c2 = st.columns([8,1])
    with c1:
        st.markdown(f"""
        <div class="section-header">
            <h2>{T("org_dashboard")}</h2>
            <span class="section-badge">Admin Hub</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if st.button(T("logout")): logout()

    st.markdown(f'<p style="color:#6b9e6b;font-size:0.82rem;margin-top:-1rem;margin-bottom:1.5rem">{T("welcome")}, <b style="color:#4ade80">{user["full_name"]}</b></p>', unsafe_allow_html=True)

    d_total   = db_count("food_donations")
    d_pending = db_count("food_donations",PENDING)
    d_matched = db_count("food_donations",MATCHED)
    n_demands = db_count("ngo_demands",PENDING)
    v_active  = db_count("volunteer_assignments","delivery_status!='Delivered'")

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box"><div class="metric-val">{d_total}</div><div class="metric-lbl">{T("total_donations")}</div></div>
        <div class="metric-box"><div class="metric-val" style="color:#fbbf24">{d_pending}</div><div class="metric-lbl">{T("pending")}</div></div>
        <div class="metric-box"><div class="metric-val">{d_matched}</div><div class="metric-lbl">{T("matched")}</div></div>
        <div class="metric-box"><div class="metric-val" style="color:#fb923c">{n_demands}</div><div class="metric-lbl">{T("ngo_demands_lbl")}</div></div>
        <div class="metric-box"><div class="metric-val" style="color:#60a5fa">{v_active}</div><div class="metric-lbl">{T("active_deliveries")}</div></div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([T("smart_matches"), T("all_donations"), T("ngo_demands_tab"), T("volunteers_tab")])

    with tab1:
        st.markdown(f"### {T('smart_match_title')}")
        matches = find_matches()
        if not matches:
            st.info(T("no_matches"))
        for m in matches:
            don = m["donation"]
            dem = m["demand"]
            score = m["score"]
            score_lbl = T("strong_match") if score >= 4 else T("good_match")
            st.markdown(f"""
            <div class="match-alert">
                <div class="match-alert-title">{score_lbl} — Score {score}/5</div>
                <div class="match-vs">
                    <div class="match-side">
                        <div style="color:#4ade80;font-size:0.75rem;font-weight:700;margin-bottom:0.3rem">{T("donor_lbl")}</div>
                        <div style="font-size:0.82rem;font-weight:600">{don['org_name']}</div>
                        <div style="font-size:0.72rem;color:#6b9e6b">{don['food_type']} · {don['food_category']}</div>
                        <div style="font-size:0.72rem;color:#6b9e6b">📦 {don['quantity']} {don['quantity_unit']}</div>
                        <div style="font-size:0.72rem;color:#6b9e6b">📍 {don['pickup_address'][:30]}...</div>
                    </div>
                    <div class="match-arrow">→</div>
                    <div class="match-side">
                        <div style="color:#fb923c;font-size:0.75rem;font-weight:700;margin-bottom:0.3rem">{T("ngo_lbl")}</div>
                        <div style="font-size:0.82rem;font-weight:600">{dem['ngo_name']}</div>
                        <div style="font-size:0.72rem;color:#6b9e6b">{dem['food_type_needed']} needed</div>
                        <div style="font-size:0.72rem;color:#6b9e6b">📦 {dem['quantity_needed']} {dem['quantity_unit']}</div>
                        <div style="font-size:0.72rem;color:#6b9e6b">👥 {T("serves")} {dem['max_capacity']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_a, col_b = st.columns([1,4])
            with col_a:
                if st.button(T("approve_match"), key=f"approve_{don['id']}_{dem['id']}"):
                    conn = get_conn()
                    conn.execute("UPDATE food_donations SET status='matched', matched_ngo_id=? WHERE id=?",
                                 (dem["ngo_id"], don["id"]))
                    conn.execute("UPDATE ngo_demands SET status='matched', matched_donation_id=? WHERE id=?",
                                 (don["id"], dem["id"]))
                    conn.commit()
                    conn.close()
                    st.success(T("match_approved"))
                    st.rerun()

    with tab2:
        conn = get_conn()
        dons = conn.execute("SELECT * FROM food_donations ORDER BY created_at DESC").fetchall()
        conn.close()
        for r in dons:
            status_cls = {"pending":"pill-yellow","matched":"pill-green","delivered":"pill-blue","assigned":"pill-orange"}.get(r["status"],"pill-yellow")
            st.markdown(f"""
            <div class="info-card donation">
                <div class="card-title">
                    🍱 {r['org_name']} — {r['donor_name']}
                    <span class="pill {status_cls}">{r['status'].upper()}</span>
                </div>
                <div class="card-row">
                    <span class="card-tag green">{r['food_type']} / {r['food_category']}</span>
                    <span class="card-tag">📦 {r['quantity']} {r['quantity_unit']}</span>
                    <span class="card-tag">📍 {r['pickup_address'][:40]}</span>
                    <span class="card-tag">🕐 {r['prep_time']}</span>
                    <span class="card-tag">📞 {r['contact']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        conn = get_conn()
        dems = conn.execute("SELECT * FROM ngo_demands ORDER BY created_at DESC").fetchall()
        conn.close()
        for r in dems:
            pri_cls = {"High":"pill-red","Medium":"pill-yellow","Low":"pill-green"}.get(r["priority"],"pill-yellow")
            st.markdown(f"""
            <div class="info-card demand">
                <div class="card-title">
                    📢 {r['ngo_name']} — {r['contact_person']}
                    <span class="pill {pri_cls}">{r['priority'].upper()}</span>
                    <span class="pill pill-blue" style="margin-left:4px">{r['status'].upper()}</span>
                </div>
                <div class="card-row">
                    <span class="card-tag orange">{r['food_type_needed']} · {r['quantity_needed']} {r['quantity_unit']}</span>
                    <span class="card-tag">👥 {r['max_capacity']} people</span>
                    <span class="card-tag">📍 {r['ngo_address'][:35]}</span>
                    <span class="card-tag">🏪 {T("storage_lbl")}: {r['storage_available']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        conn = get_conn()
        matched_dons = conn.execute(
            "SELECT fd.*, u.full_name as ngo_name2 FROM food_donations fd "
            "LEFT JOIN users u ON fd.matched_ngo_id = u.id "
            "WHERE fd.status='matched' AND fd.assigned_volunteer_id IS NULL"
        ).fetchall()
        volunteers = conn.execute("SELECT * FROM users WHERE role='volunteer'").fetchall()
        assignments = conn.execute(
            "SELECT va.*, u.full_name as vol_name, fd.org_name, fd.pickup_address "
            "FROM volunteer_assignments va "
            "JOIN users u ON va.volunteer_id=u.id "
            "JOIN food_donations fd ON va.donation_id=fd.id "
            "ORDER BY va.created_at DESC"
        ).fetchall()
        conn.close()

        st.markdown(f"#### {T('assign_vol')}")
        if not matched_dons:
            st.info(T("no_matched_dons"))
        for don in matched_dons:
            st.markdown(f"""
            <div class="info-card volunteer">
                <div class="card-title">🚴 {T("needs_volunteer")} — {don['org_name']}</div>
                <div class="card-row">
                    <span class="card-tag blue">📍 {T("pickup")}: {don['pickup_address'][:40]}</span>
                    <span class="card-tag blue">🕐 {don['prep_time']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if volunteers:
                vol_options = {v["full_name"]: v["id"] for v in volunteers}
                with st.form(f"assign_vol_{don['id']}"):
                    sel_vol = st.selectbox(T("assign_volunteer"), list(vol_options.keys()), key=f"sv_{don['id']}")
                    drop_loc = st.text_input(T("drop_loc"), key=f"dl_{don['id']}")
                    asgn_time = st.text_input(T("assigned_time"), key=f"at_{don['id']}")
                    if st.form_submit_button(T("assign_btn")):
                        vid = vol_options[sel_vol]
                        conn2 = get_conn()
                        conn2.execute("""INSERT INTO volunteer_assignments
                            (volunteer_id,donation_id,pickup_location,drop_location,assigned_time)
                            VALUES (?,?,?,?,?)""",
                            (vid, don["id"], don["pickup_address"], drop_loc, asgn_time))
                        conn2.execute("UPDATE food_donations SET assigned_volunteer_id=?, status='assigned' WHERE id=?",
                                      (vid, don["id"]))
                        conn2.commit()
                        conn2.close()
                        st.success(f"✅ {sel_vol} {T('assign_btn')}!")
                        st.rerun()
            else:
                st.warning(T("no_volunteers"))

        st.markdown("---")
        st.markdown(f"#### {T('active_assignments')}")
        if not assignments:
            st.info(T("no_assignments"))
        for a in assignments:
            status_cls = {"Assigned":"pill-yellow","Picked":"pill-orange","In Transit":"pill-blue","Delivered":"pill-green"}.get(a["delivery_status"],"pill-yellow")
            st.markdown(f"""
            <div class="info-card volunteer">
                <div class="card-title">
                    🚴 {a['vol_name']} → {a['org_name']}
                    <span class="pill {status_cls}">{a['delivery_status'].upper()}</span>
                </div>
                <div class="card-row">
                    <span class="card-tag blue">📍 {T("pickup")}: {a['pickup_address'][:30]}</span>
                    <span class="card-tag blue">🏁 {T("drop")}: {a['drop_location'][:30]}</span>
                    <span class="card-tag">🕐 {a['assigned_time']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD: VOLUNTEER
# ══════════════════════════════════════════════════════════════════════════════
def dashboard_volunteer():
    user = st.session_state.user
    render_logo(small=True)
    c1, c2 = st.columns([8,1])
    with c1:
        st.markdown(f"""
        <div class="section-header">
            <h2>{T("vol_dashboard")}</h2>
            <span class="section-badge">Volunteer</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if st.button(T("logout")): logout()

    st.markdown(f'<p style="color:#6b9e6b;font-size:0.82rem;margin-top:-1rem;margin-bottom:1.5rem">{T("welcome")}, <b style="color:#4ade80">{user["full_name"]}</b></p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs([T("my_assignments"), T("my_profile")])

    with tab1:
        conn = get_conn()
        assignments = conn.execute("""
            SELECT va.*, fd.org_name, fd.food_type, fd.food_category, fd.quantity,
                   fd.quantity_unit, fd.prep_time, fd.special_instructions,
                   fd.pickup_address as don_pickup
            FROM volunteer_assignments va
            JOIN food_donations fd ON va.donation_id=fd.id
            WHERE va.volunteer_id=?
            ORDER BY va.created_at DESC
        """, (user["id"],)).fetchall()
        conn.close()

        if not assignments:
            st.info(T("no_assign"))
        for a in assignments:
            status_cls = {"Assigned":"pill-yellow","Picked":"pill-orange","In Transit":"pill-blue","Delivered":"pill-green"}.get(a["delivery_status"],"pill-yellow")
            st.markdown(f"""
            <div class="info-card volunteer">
                <div class="card-title">
                    🚴 {T("assignment_lbl")} — {a['org_name']}
                    <span class="pill {status_cls}">{a['delivery_status'].upper()}</span>
                </div>
                <div class="card-row">
                    <span class="card-tag blue">🍱 {a['food_type']} / {a['food_category']}</span>
                    <span class="card-tag blue">📦 {a['quantity']} {a['quantity_unit']}</span>
                    <span class="card-tag">📍 {T("pickup")}: {a['don_pickup'][:35]}</span>
                    <span class="card-tag">🏁 {T("drop")}: {a['drop_location'][:35]}</span>
                    <span class="card-tag">🕐 {a['assigned_time']}</span>
                </div>
                {f'<div style="margin-top:0.5rem;font-size:0.75rem;color:#6b9e6b">📝 {a["special_instructions"]}</div>' if a['special_instructions'] else ''}
            </div>
            """, unsafe_allow_html=True)

            if a["delivery_status"] != "Delivered":
                next_statuses = {"Assigned":["Picked","In Transit"],"Picked":["In Transit","Delivered"],"In Transit":["Delivered"]}
                options = next_statuses.get(a["delivery_status"], [])
                if options:
                    with st.form(f"vol_update_{a['id']}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            new_status = st.selectbox(T("update_status"), options, key=f"ns_{a['id']}")
                        with c2:
                            remarks = st.text_input(T("remarks"), key=f"vr_{a['id']}")
                        if st.form_submit_button(T("update_status")):
                            conn2 = get_conn()
                            conn2.execute("UPDATE volunteer_assignments SET delivery_status=?, remarks=? WHERE id=?",
                                          (new_status, remarks, a["id"]))
                            if new_status == "Delivered":
                                conn2.execute("UPDATE food_donations SET status='delivered' WHERE id=?",
                                              (a["donation_id"],))
                            conn2.commit()
                            conn2.close()
                            st.success(f"{T('update_status')}: {new_status}")
                            st.rerun()

    with tab2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        with st.form("vol_profile"):
            c1, c2 = st.columns(2)
            with c1:
                vehicle = st.selectbox(T("vehicle"), ["Bike","Car","Van","Walk"])
                avail   = st.selectbox(T("availability"), ["Available","Busy","Offline"])
            with c2:
                location = st.text_input(T("current_loc"))
            if st.form_submit_button(T("update_profile")):
                st.success(T("profile_updated"))
        st.markdown('</div>', unsafe_allow_html=True)

        total_del = db_count("volunteer_assignments", f"volunteer_id={user['id']} AND delivery_status='Delivered'")
        total_asgn = db_count("volunteer_assignments", f"volunteer_id={user['id']}")
        st.markdown(f"""
        <div class="metric-row" style="margin-top:1rem">
            <div class="metric-box"><div class="metric-val">{total_asgn}</div><div class="metric-lbl">{T("total_assignments")}</div></div>
            <div class="metric-box"><div class="metric-val">{total_del}</div><div class="metric-lbl">{T("delivered")}</div></div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
page = st.session_state.page

if page == "home":
    page_home()
elif page == "auth":
    page_auth()
elif page == "dashboard_donor":
    if st.session_state.user: dashboard_donor()
    else: go("auth")
elif page == "dashboard_organization":
    if st.session_state.user: dashboard_organization()
    else: go("auth")
elif page == "dashboard_ngo":
    if st.session_state.user: dashboard_ngo()
    else: go("auth")
elif page == "dashboard_volunteer":
    if st.session_state.user: dashboard_volunteer()
    else: go("auth")
else:
    go("home")




    #Food Donor Username - taj123
    #password - taj@123

    #Organization Username - adi123
    #password - adi@123

    #NGO Username - kartik123
    #password - kartik@123

    #Volunteer Username - prachi123
    #password - prachi@123