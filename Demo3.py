import streamlit as st
import sqlite3
import hashlib


DB_PATH = "iotfeedbridge.db"


st.set_page_config(
    page_title="FeedBridge",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        contact TEXT,
        email TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS food_donations (
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
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ngo_demands (
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
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ngo_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ngo_id INTEGER,
        donation_id INTEGER,
        action TEXT,
        quantity_accepted REAL,
        preferred_pickup_time TEXT,
        priority TEXT,
        remarks TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS volunteer_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id INTEGER,
        donation_id INTEGER,
        pickup_location TEXT,
        drop_location TEXT,
        assigned_time TEXT,
        delivery_status TEXT DEFAULT 'Assigned',
        remarks TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    conn.commit()
    conn.close()


def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password, role, full_name, contact, email):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username,password,role,full_name,contact,email) VALUES (?,?,?,?,?,?)",
            (username, hash_pw(password), role, full_name, contact, email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password, role):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=? AND role=?",
        (username, hash_pw(password), role)
    ).fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def db_count(table, where_text="1=1"):
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) FROM " + table + " WHERE " + where_text).fetchone()
    conn.close()
    return row[0]


def find_matches():
    conn = get_conn()
    donations = conn.execute("SELECT * FROM food_donations WHERE status='pending'").fetchall()
    demands = conn.execute("SELECT * FROM ngo_demands WHERE status='pending'").fetchall()
    conn.close()

    matches = []

    for donation in donations:
        for demand in demands:
            score = 0

            if donation["food_type"] == demand["food_type_needed"]:
                score = score + 3

            if donation["quantity"] >= demand["quantity_needed"]:
                score = score + 2

            if score >= 2:
                item = {
                    "donation": dict(donation),
                    "demand": dict(demand),
                    "score": score
                }
                matches.append(item)

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches


def setup_session():
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if "role" not in st.session_state:
        st.session_state.role = None

    if "user" not in st.session_state:
        st.session_state.user = None

    if "lang" not in st.session_state:
        st.session_state.lang = "English"


def go(page_name):
    st.session_state.page = page_name
    st.rerun()


def logout():
    st.session_state.user = None
    st.session_state.role = None
    go("home")


def short_text(text, limit):
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def show_header(title, badge):
    left, right = st.columns([6, 1])
    with left:
        st.title(title)
        st.caption(badge)
    with right:
        if st.button("Logout", use_container_width=True):
            logout()


def show_logo():
    st.title("🌿 IoT FeedBridge")
    st.caption("Smart Food Distribution Network")


def show_status(text):
    if text == "pending":
        st.warning("Status: Pending")
    elif text == "matched":
        st.success("Status: Matched")
    elif text == "assigned":
        st.info("Status: Assigned")
    elif text == "delivered":
        st.success("Status: Delivered")
    else:
        st.write("Status:", text)



TEXT = {
    "English": {
        "tagline": "Connecting food donors, NGOs and volunteers through intelligent matching",
        "enter_as": "Enter as",
        "welcome": "Welcome",
        "back_home": "Back to Home",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "full_name": "Full Name / Organization Name",
        "contact": "Contact Number",
        "email": "Email ID",
        "choose_username": "Choose Username",
        "choose_password": "Choose Password",
        "confirm_password": "Confirm Password",
        "create_account": "Create Account",
        "fill_required": "Please fill all required fields.",
        "invalid_creds": "Invalid credentials or wrong role.",
        "pwd_mismatch": "Passwords do not match.",
        "reg_success": "Registered successfully. Please login.",
        "username_exists": "Username already exists.",
    },
    "मराठी": {
        "tagline": "अन्नदाते, NGO आणि स्वयंसेवक यांना बुद्धिमान जुळणीद्वारे जोडणे",
        "enter_as": "म्हणून प्रवेश करा",
        "welcome": "स्वागत",
        "back_home": "मुख्यपृष्ठावर परत",
        "login": "लॉगिन",
        "register": "नोंदणी",
        "username": "वापरकर्तानाव",
        "password": "पासवर्ड",
        "full_name": "पूर्ण नाव / संस्थेचे नाव",
        "contact": "संपर्क क्रमांक",
        "email": "ईमेल आयडी",
        "choose_username": "वापरकर्तानाव निवडा",
        "choose_password": "पासवर्ड निवडा",
        "confirm_password": "पासवर्ड पुष्टी करा",
        "create_account": "खाते तयार करा",
        "fill_required": "कृपया सर्व आवश्यक माहिती भरा.",
        "invalid_creds": "चुकीची माहिती किंवा चुकीची भूमिका.",
        "pwd_mismatch": "पासवर्ड जुळत नाहीत.",
        "reg_success": "नोंदणी यशस्वी. कृपया लॉगिन करा.",
        "username_exists": "वापरकर्तानाव आधीच अस्तित्वात आहे.",
    },
    "हिंदी": {
        "tagline": "खाद्य दाताओं, NGO और स्वयंसेवकों को बुद्धिमान मिलान से जोड़ना",
        "enter_as": "के रूप में प्रवेश करें",
        "welcome": "स्वागत है",
        "back_home": "होम पर वापस",
        "login": "लॉगिन",
        "register": "पंजीकरण",
        "username": "उपयोगकर्ता नाम",
        "password": "पासवर्ड",
        "full_name": "पूरा नाम / संस्था का नाम",
        "contact": "संपर्क नंबर",
        "email": "ईमेल आईडी",
        "choose_username": "उपयोगकर्ता नाम चुनें",
        "choose_password": "पासवर्ड चुनें",
        "confirm_password": "पासवर्ड की पुष्टि करें",
        "create_account": "खाता बनाएं",
        "fill_required": "कृपया सभी आवश्यक फ़ील्ड भरें।",
        "invalid_creds": "गलत क्रेडेंशियल या गलत भूमिका।",
        "pwd_mismatch": "पासवर्ड मेल नहीं खाते।",
        "reg_success": "पंजीकरण सफल. कृपया लॉगिन करें.",
        "username_exists": "उपयोगकर्ता नाम पहले से मौजूद है.",
    }
}


def T(key):
    lang = st.session_state.lang
    if key in TEXT[lang]:
        return TEXT[lang][key]
    return TEXT["English"].get(key, key)


def page_home():
    lang = st.selectbox("Language", ["English", "मराठी", "हिंदी"])
    st.session_state.lang = lang

    show_logo()
    st.write(T("tagline"))
    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("🍽️ Food Donors")
        st.caption("Hotels, restaurants and event organizers")
        if st.button(T("enter_as") + " Donor", use_container_width=True):
            st.session_state.role = "donor"
            go("auth")

    with col2:
        st.subheader("🏢 Organizations")
        st.caption("Central coordination hub")
        if st.button(T("enter_as") + " Organization", use_container_width=True):
            st.session_state.role = "organization"
            go("auth")

    with col3:
        st.subheader("🤝 NGOs")
        st.caption("Request and receive food donations")
        if st.button(T("enter_as") + " NGO", use_container_width=True):
            st.session_state.role = "ngo"
            go("auth")

    with col4:
        st.subheader("🚴 Volunteers")
        st.caption("Pickup and delivery logistics")
        if st.button(T("enter_as") + " Volunteer", use_container_width=True):
            st.session_state.role = "volunteer"
            go("auth")

    st.divider()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Donations", db_count("food_donations"))
    m2.metric("Demands", db_count("ngo_demands"))
    m3.metric("Matched", db_count("food_donations", "status='matched'"))
    m4.metric("Deliveries", db_count("volunteer_assignments"))


def page_auth():
    role = st.session_state.role
    role_names = {
        "donor": "Food Donor",
        "organization": "Organization",
        "ngo": "NGO",
        "volunteer": "Volunteer"
    }

    if role is None:
        go("home")

    if st.button(T("back_home")):
        go("home")

    st.title(role_names[role] + " Portal")
    tab1, tab2 = st.tabs([T("login"), T("register")])

    with tab1:
        with st.form("login_form"):
            username = st.text_input(T("username"))
            password = st.text_input(T("password"), type="password")
            submitted = st.form_submit_button(T("login"), use_container_width=True)

            if submitted:
                user = login_user(username, password, role)

                if user:
                    st.session_state.user = user
                    go("dashboard_" + role)
                else:
                    st.error(T("invalid_creds"))

    with tab2:
        with st.form("register_form"):
            full_name = st.text_input(T("full_name"))
            contact = st.text_input(T("contact"))
            email = st.text_input(T("email"))
            username = st.text_input(T("choose_username"))
            password = st.text_input(T("choose_password"), type="password")
            confirm_password = st.text_input(T("confirm_password"), type="password")
            submitted = st.form_submit_button(T("create_account"), use_container_width=True)

            if submitted:
                if password != confirm_password:
                    st.error(T("pwd_mismatch"))
                elif not full_name or not contact or not username or not password:
                    st.error(T("fill_required"))
                else:
                    created = register_user(username, password, role, full_name, contact, email)

                    if created:
                        st.success(T("reg_success"))
                    else:
                        st.error(T("username_exists"))


def dashboard_donor():
    user = st.session_state.user
    show_logo()
    show_header("🍽️ Food Donor Dashboard", "Donor")
    st.write(T("welcome") + ", " + user["full_name"])

    tab1, tab2 = st.tabs(["➕ Submit Donation", "📋 My Donations"])

    with tab1:
        with st.form("donation_form"):
            col1, col2 = st.columns(2)

            with col1:
                donor_name = st.text_input("Donor Name", value=user["full_name"])
                org_name = st.text_input("Organization / Restaurant Name")
                contact = st.text_input("Contact Number", value=user["contact"])

            with col2:
                food_type = st.selectbox("Type of Food", ["Veg", "Non-Veg", "Both"])
                food_category = st.selectbox("Food Category", ["Cooked", "Packaged", "Both"])
                quantity_unit = st.selectbox("Quantity Unit", ["Person-wise", "Kg"])

            col3, col4 = st.columns(2)

            with col3:
                quantity = st.number_input("Quantity", min_value=0.0, step=0.5)
                prep_time = st.text_input("Time of Preparation")

            with col4:
                pickup_address = st.text_area("Pickup Address")

            special = st.text_area("Special Instructions")
            submitted = st.form_submit_button("🚀 Submit Donation", use_container_width=True)

            if submitted:
                if not donor_name or not org_name or quantity <= 0 or not pickup_address:
                    st.error(T("fill_required"))
                else:
                    conn = get_conn()
                    conn.execute("""
                    INSERT INTO food_donations
                    (donor_id,donor_name,org_name,contact,food_type,food_category,
                     quantity,quantity_unit,prep_time,pickup_address,special_instructions)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        user["id"], donor_name, org_name, contact, food_type, food_category,
                        quantity, quantity_unit, prep_time, pickup_address, special
                    ))
                    conn.commit()
                    conn.close()
                    st.success("Donation submitted. Organization will coordinate pickup.")

    with tab2:
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM food_donations WHERE donor_id=? ORDER BY created_at DESC",
            (user["id"],)
        ).fetchall()
        conn.close()

        if not rows:
            st.info("No donations yet. Submit your first one.")

        for row in rows:
            with st.container(border=True):
                st.subheader("🍱 " + row["org_name"])
                show_status(row["status"])
                st.write(row["food_type"] + " / " + row["food_category"])
                st.write("Quantity:", row["quantity"], row["quantity_unit"])
                st.write("Pickup:", row["pickup_address"])
                st.caption("Created at: " + row["created_at"])


def dashboard_ngo():
    user = st.session_state.user
    show_logo()
    show_header("🤝 NGO Dashboard", "NGO")
    st.write(T("welcome") + ", " + user["full_name"])

    tab1, tab2, tab3 = st.tabs(["📢 Post Demand", "📋 My Demands", "🔔 Matched Donations"])

    with tab1:
        with st.form("ngo_demand_form"):
            col1, col2 = st.columns(2)

            with col1:
                ngo_name = st.text_input("NGO Name", value=user["full_name"])
                contact_person = st.text_input("Contact Person Name")
                contact = st.text_input("Contact Number", value=user["contact"])
                email = st.text_input("Email ID", value=user["email"])

            with col2:
                ngo_address = st.text_area("NGO Address")
                service_area = st.text_input("Service Area")
                max_capacity = st.number_input("Maximum Capacity", min_value=0, step=10)
                storage = st.selectbox("Storage Facility Available", ["Yes", "No"])

            food_needed = st.selectbox("Food Type Needed", ["Veg", "Non-Veg", "Both"])
            quantity_needed = st.number_input("Quantity Needed", min_value=0.0, step=0.5)
            quantity_unit = st.selectbox("Unit", ["Person-wise", "Kg"])
            priority = st.selectbox("Priority Level", ["High", "Medium", "Low"], index=1)
            remarks = st.text_area("Remarks")
            submitted = st.form_submit_button("📢 Post Food Demand", use_container_width=True)

            if submitted:
                if not ngo_name or not contact_person or not ngo_address or quantity_needed <= 0:
                    st.error(T("fill_required"))
                else:
                    conn = get_conn()
                    conn.execute("""
                    INSERT INTO ngo_demands
                    (ngo_id,ngo_name,contact_person,contact,email,ngo_address,service_area,
                     max_capacity,storage_available,food_type_needed,quantity_needed,
                     quantity_unit,priority,remarks)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """, (
                        user["id"], ngo_name, contact_person, contact, email, ngo_address,
                        service_area, max_capacity, storage, food_needed, quantity_needed,
                        quantity_unit, priority, remarks
                    ))
                    conn.commit()
                    conn.close()
                    st.success("Demand posted. Organization will review and match.")

    with tab2:
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM ngo_demands WHERE ngo_id=? ORDER BY created_at DESC",
            (user["id"],)
        ).fetchall()
        conn.close()

        if not rows:
            st.info("No demands posted yet.")

        for row in rows:
            with st.container(border=True):
                st.subheader("📢 " + row["ngo_name"])
                st.write("Need:", row["food_type_needed"])
                st.write("Quantity:", row["quantity_needed"], row["quantity_unit"])
                st.write("Priority:", row["priority"])
                show_status(row["status"])
                st.write("Address:", row["ngo_address"])
                st.caption("Created at: " + row["created_at"])

    with tab3:
        conn = get_conn()
        rows = conn.execute("""
        SELECT * FROM food_donations
        WHERE matched_ngo_id=? AND status IN ('matched','assigned')
        ORDER BY created_at DESC
        """, (user["id"],)).fetchall()
        conn.close()

        if not rows:
            st.info("No matched donations yet.")

        for row in rows:
            with st.container(border=True):
                st.success("✅ Matched Donation")
                st.write("Food:", row["food_type"], "/", row["food_category"])
                st.write("Quantity:", row["quantity"], row["quantity_unit"])
                st.write("Donor:", row["org_name"])
                st.write("Pickup:", row["pickup_address"])
                st.write("Time:", row["prep_time"])

                conn = get_conn()
                existing = conn.execute(
                    "SELECT * FROM ngo_responses WHERE ngo_id=? AND donation_id=?",
                    (user["id"], row["id"])
                ).fetchone()
                conn.close()

                if existing:
                    st.success("Response submitted")
                else:
                    with st.expander("Respond to this Donation"):
                        with st.form("ngo_response_" + str(row["id"])):
                            action = st.selectbox("Action", ["Accept", "Reject"])
                            qty = st.number_input(
                                "Quantity to Accept",
                                min_value=0.0,
                                max_value=float(row["quantity"]),
                                step=0.5
                            )
                            pickup_time = st.text_input("Preferred Pickup Time")
                            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
                            remarks = st.text_area("Remarks")
                            submitted = st.form_submit_button("Submit Response")

                            if submitted:
                                conn = get_conn()
                                conn.execute("""
                                INSERT INTO ngo_responses
                                (ngo_id,donation_id,action,quantity_accepted,preferred_pickup_time,priority,remarks)
                                VALUES (?,?,?,?,?,?,?)
                                """, (
                                    user["id"], row["id"], action, qty, pickup_time, priority, remarks
                                ))
                                conn.commit()
                                conn.close()
                                st.success("Response submitted")
                                st.rerun()


def dashboard_organization():
    user = st.session_state.user
    show_logo()
    show_header("🏢 Organization Dashboard", "Admin Hub")
    st.write(T("welcome") + ", " + user["full_name"])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Donations", db_count("food_donations"))
    col2.metric("Pending", db_count("food_donations", "status='pending'"))
    col3.metric("Matched", db_count("food_donations", "status='matched'"))
    col4.metric("NGO Demands", db_count("ngo_demands", "status='pending'"))
    col5.metric("Active Deliveries", db_count("volunteer_assignments", "delivery_status!='Delivered'"))

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Smart Matches",
        "🍽️ Donations",
        "📢 NGO Demands",
        "🚴 Volunteers"
    ])

    with tab1:
        st.subheader("🤖 AI-Suggested Matches")
        matches = find_matches()

        if not matches:
            st.info("No pending matches found.")

        for match in matches:
            donation = match["donation"]
            demand = match["demand"]

            with st.container(border=True):
                if match["score"] >= 4:
                    st.success("🔥 Strong Match - Score " + str(match["score"]) + "/5")
                else:
                    st.info("✅ Good Match - Score " + str(match["score"]) + "/5")

                col_a, col_b = st.columns(2)

                with col_a:
                    st.write("🍱 Donor")
                    st.write(donation["org_name"])
                    st.write(donation["food_type"], "/", donation["food_category"])
                    st.write("Quantity:", donation["quantity"], donation["quantity_unit"])
                    st.write("Pickup:", short_text(donation["pickup_address"], 60))

                with col_b:
                    st.write("🤝 NGO")
                    st.write(demand["ngo_name"])
                    st.write("Needs:", demand["food_type_needed"])
                    st.write("Quantity:", demand["quantity_needed"], demand["quantity_unit"])
                    st.write("Serves:", demand["max_capacity"])

                key = "approve_" + str(donation["id"]) + "_" + str(demand["id"])
                if st.button("✅ Approve Match", key=key):
                    conn = get_conn()
                    conn.execute(
                        "UPDATE food_donations SET status='matched', matched_ngo_id=? WHERE id=?",
                        (demand["ngo_id"], donation["id"])
                    )
                    conn.execute(
                        "UPDATE ngo_demands SET status='matched', matched_donation_id=? WHERE id=?",
                        (donation["id"], demand["id"])
                    )
                    conn.commit()
                    conn.close()
                    st.success("Match approved.")
                    st.rerun()

    with tab2:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM food_donations ORDER BY created_at DESC").fetchall()
        conn.close()

        if not rows:
            st.info("No donations found.")

        for row in rows:
            with st.container(border=True):
                st.subheader("🍱 " + row["org_name"] + " - " + row["donor_name"])
                show_status(row["status"])
                st.write(row["food_type"], "/", row["food_category"])
                st.write("Quantity:", row["quantity"], row["quantity_unit"])
                st.write("Pickup:", row["pickup_address"])
                st.write("Contact:", row["contact"])

    with tab3:
        conn = get_conn()
        rows = conn.execute("SELECT * FROM ngo_demands ORDER BY created_at DESC").fetchall()
        conn.close()

        if not rows:
            st.info("No NGO demands found.")

        for row in rows:
            with st.container(border=True):
                st.subheader("📢 " + row["ngo_name"])
                st.write("Contact Person:", row["contact_person"])
                st.write("Need:", row["food_type_needed"])
                st.write("Quantity:", row["quantity_needed"], row["quantity_unit"])
                st.write("Priority:", row["priority"])
                show_status(row["status"])
                st.write("Address:", row["ngo_address"])

    with tab4:
        volunteer_tab()


def volunteer_tab():
    conn = get_conn()
    matched_donations = conn.execute("""
    SELECT fd.*, u.full_name as ngo_name
    FROM food_donations fd
    LEFT JOIN users u ON fd.matched_ngo_id = u.id
    WHERE fd.status='matched' AND fd.assigned_volunteer_id IS NULL
    """).fetchall()
    volunteers = conn.execute("SELECT * FROM users WHERE role='volunteer'").fetchall()
    assignments = conn.execute("""
    SELECT va.*, u.full_name as volunteer_name, fd.org_name, fd.pickup_address
    FROM volunteer_assignments va
    JOIN users u ON va.volunteer_id = u.id
    JOIN food_donations fd ON va.donation_id = fd.id
    ORDER BY va.created_at DESC
    """).fetchall()
    conn.close()

    st.subheader("Assign Volunteers to Matched Donations")

    if not matched_donations:
        st.info("No matched donations awaiting volunteer assignment.")

    for donation in matched_donations:
        with st.container(border=True):
            st.write("🚴 Needs Volunteer - " + donation["org_name"])
            st.write("Pickup:", donation["pickup_address"])
            st.write("Time:", donation["prep_time"])

            if volunteers:
                volunteer_names = []
                volunteer_ids = []

                for volunteer in volunteers:
                    volunteer_names.append(volunteer["full_name"])
                    volunteer_ids.append(volunteer["id"])

                with st.form("assign_vol_" + str(donation["id"])):
                    selected_name = st.selectbox("Assign Volunteer", volunteer_names)
                    drop_location = st.text_input("Drop Location")
                    assigned_time = st.text_input("Assigned Time")
                    submitted = st.form_submit_button("Assign")

                    if submitted:
                        index = volunteer_names.index(selected_name)
                        volunteer_id = volunteer_ids[index]

                        conn = get_conn()
                        conn.execute("""
                        INSERT INTO volunteer_assignments
                        (volunteer_id,donation_id,pickup_location,drop_location,assigned_time)
                        VALUES (?,?,?,?,?)
                        """, (
                            volunteer_id,
                            donation["id"],
                            donation["pickup_address"],
                            drop_location,
                            assigned_time
                        ))
                        conn.execute(
                            "UPDATE food_donations SET assigned_volunteer_id=?, status='assigned' WHERE id=?",
                            (volunteer_id, donation["id"])
                        )
                        conn.commit()
                        conn.close()
                        st.success("Volunteer assigned.")
                        st.rerun()
            else:
                st.warning("No volunteers registered yet.")

    st.divider()
    st.subheader("Active Assignments")

    if not assignments:
        st.info("No assignments yet.")

    for assignment in assignments:
        with st.container(border=True):
            st.write("🚴 " + assignment["volunteer_name"] + " → " + assignment["org_name"])
            st.write("Status:", assignment["delivery_status"])
            st.write("Pickup:", assignment["pickup_address"])
            st.write("Drop:", assignment["drop_location"])
            st.write("Time:", assignment["assigned_time"])


def dashboard_volunteer():
    user = st.session_state.user
    show_logo()
    show_header("🚴 Volunteer Dashboard", "Volunteer")
    st.write(T("welcome") + ", " + user["full_name"])

    tab1, tab2 = st.tabs(["📦 My Assignments", "👤 My Profile"])

    with tab1:
        conn = get_conn()
        rows = conn.execute("""
        SELECT va.*, fd.org_name, fd.food_type, fd.food_category, fd.quantity,
               fd.quantity_unit, fd.prep_time, fd.special_instructions,
               fd.pickup_address as donation_pickup
        FROM volunteer_assignments va
        JOIN food_donations fd ON va.donation_id = fd.id
        WHERE va.volunteer_id=?
        ORDER BY va.created_at DESC
        """, (user["id"],)).fetchall()
        conn.close()

        if not rows:
            st.info("No assignments yet. The Organization will assign pickups to you.")

        for row in rows:
            with st.container(border=True):
                st.subheader("🚴 Assignment - " + row["org_name"])
                st.write("Status:", row["delivery_status"])
                st.write("Food:", row["food_type"], "/", row["food_category"])
                st.write("Quantity:", row["quantity"], row["quantity_unit"])
                st.write("Pickup:", row["donation_pickup"])
                st.write("Drop:", row["drop_location"])
                st.write("Time:", row["assigned_time"])

                if row["special_instructions"]:
                    st.write("Instructions:", row["special_instructions"])

                if row["delivery_status"] != "Delivered":
                    options = []

                    if row["delivery_status"] == "Assigned":
                        options = ["Picked", "In Transit"]
                    elif row["delivery_status"] == "Picked":
                        options = ["In Transit", "Delivered"]
                    elif row["delivery_status"] == "In Transit":
                        options = ["Delivered"]

                    if options:
                        with st.form("vol_update_" + str(row["id"])):
                            new_status = st.selectbox("Update Status", options)
                            remarks = st.text_input("Remarks")
                            submitted = st.form_submit_button("Update Status")

                            if submitted:
                                conn = get_conn()
                                conn.execute(
                                    "UPDATE volunteer_assignments SET delivery_status=?, remarks=? WHERE id=?",
                                    (new_status, remarks, row["id"])
                                )

                                if new_status == "Delivered":
                                    conn.execute(
                                        "UPDATE food_donations SET status='delivered' WHERE id=?",
                                        (row["donation_id"],)
                                    )

                                conn.commit()
                                conn.close()
                                st.success("Status updated.")
                                st.rerun()

    with tab2:
        with st.form("vol_profile"):
            vehicle = st.selectbox("Vehicle Type", ["Bike", "Car", "Van", "Walk"])
            availability = st.selectbox("Availability Status", ["Available", "Busy", "Offline"])
            location = st.text_input("Current Location")
            submitted = st.form_submit_button("Update Profile")

            if submitted:
                st.success("Profile updated.")

        total_assignments = db_count(
            "volunteer_assignments",
            "volunteer_id=" + str(user["id"])
        )
        total_delivered = db_count(
            "volunteer_assignments",
            "volunteer_id=" + str(user["id"]) + " AND delivery_status='Delivered'"
        )

        col1, col2 = st.columns(2)
        col1.metric("Total Assignments", total_assignments)
        col2.metric("Delivered", total_delivered)



init_db()
setup_session()

page = st.session_state.page

if page == "home":
    page_home()
elif page == "auth":
    page_auth()
elif page == "dashboard_donor":
    if st.session_state.user:
        dashboard_donor()
    else:
        go("auth")
elif page == "dashboard_organization":
    if st.session_state.user:
        dashboard_organization()
    else:
        go("auth")
elif page == "dashboard_ngo":
    if st.session_state.user:
        dashboard_ngo()
    else:
        go("auth")
elif page == "dashboard_volunteer":
    if st.session_state.user:
        dashboard_volunteer()
    else:
        go("auth")
else:
    go("home")


