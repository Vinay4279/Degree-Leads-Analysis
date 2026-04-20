# ==============================================================================
# STEP 1: IMPORTING LIBRARIES (Zaroori modules import kar rahe hain)
# ==============================================================================
import streamlit as st
import pandas as pd
import mysql.connector
import datetime
import base64

# ==============================================================================
# STEP 2: PAGE CONFIGURATION & ENTERPRISE UI STYLING (CSS)
# ==============================================================================
# Page ka naam aur icon set karna
st.set_page_config(page_title="Degree Leads Analysis", page_icon="🎓", layout="wide")

# CSS styling for professional look, center alignment, and removing extra spaces
st.markdown("""
<style>
    /* Main Title par premium blue gradient color lagana */
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        letter-spacing: -1px;
    }
    
    /* Tabs (Main Menu) ko modern aur sleek look dena */
    div[data-testid="stTabs"] button {
        font-size: 16px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        border-radius: 8px 8px 0 0;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #00f2fe !important;
        border-bottom: 3px solid #00f2fe !important;
        background: rgba(0, 242, 254, 0.05);
    }
    
    /* Input fields (Search, Date, Selectbox) ko Glassmorphism (transparent) look dena */
    .stTextInput>div>div>input, 
    .stDateInput>div>div>input, 
    .stSelectbox>div>div>div {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease-in-out !important;
        background-color: rgba(30, 41, 59, 0.5) !important;
        color: white !important;
    }
    .stTextInput>div>div>input:focus, 
    .stDateInput>div>div>input:focus, 
    .stSelectbox>div>div>div:focus,
    .stTextInput>div>div>input:hover, 
    .stDateInput>div>div>input:hover, 
    .stSelectbox>div>div>div:hover {
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.25) !important;
        background-color: rgba(15, 23, 42, 0.8) !important;
    }

    /* Login Form ki default border ko chhupana taaki clean dikhe */
    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* Data Tables (DataFrames) ko premium borders aur shadow dena */
    .stDataFrame {
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .stDataFrame:hover {
        box-shadow: 0 0 20px rgba(0, 242, 254, 0.15);
        border-color: rgba(0, 242, 254, 0.3);
        transition: 0.3s ease;
    }

    /* Buttons (Login, Refresh, Download) ko premium dark look aur hover effect dena */
    .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        color: #e2e8f0 !important;
        transition: all 0.3s ease !important;
        padding: 10px 24px !important;
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: #ffffff !important;
        border: 1px solid transparent !important;
        box-shadow: 0 6px 20px rgba(0, 242, 254, 0.4) !important;
        transform: translateY(-2px);
    }

    /* Info Boxes (First Login Tracker) */
    .stAlert {
        border-radius: 8px !important;
        border: 1px solid rgba(0, 242, 254, 0.2) !important;
        background-color: rgba(0, 242, 254, 0.05) !important;
        color: #e2e8f0 !important;
        backdrop-filter: blur(10px);
    }

    /* Layout ko bada karne ke liye max-width ko 96% karna */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 96% !important;
    }
    
    /* --- SIDEBAR ALIGNMENT & EXTRA SPACE REMOVAL --- */
    /* Sidebar ke sabhi text aur elements ko center align karna */
    [data-testid="stSidebar"] { text-align: center; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 { text-align: center !important; }
    [data-testid="stSidebar"] label p { text-align: center !important; width: 100% !important; display: block !important; }
    [data-testid="stSidebar"] input { text-align: center !important; }
    [data-testid="stSidebar"] [data-baseweb="select"] div[class*="ValueContainer"] { justify-content: center !important; }
    [data-testid="stSidebar"] [data-testid="stAlert"] { display: flex; justify-content: center; text-align: center; }
    
    /* Sidebar ki faaltu empty space (padding) ko hatana */
    [data-testid="stSidebarHeader"] { padding-top: 1rem !important; padding-bottom: 0rem !important; min-height: auto !important; }
    [data-testid="stSidebarUserContent"] { padding-top: 0rem !important; }
    hr { border-color: rgba(255, 255, 255, 0.1) !important; margin-top: 1rem !important; margin-bottom: 1rem !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# STEP 3: USER CREDENTIALS & LOGIN SYSTEM (Security & Memory Tracking)
# ==============================================================================
# Users ki dictionary jisme ID, Password aur Full Name save hai
USERS = {
    "hx1001": {"pwd": "hx1001", "name": "Vipul Bhatnagar"},
    "hx1192": {"pwd": "hx1192", "name": "Vipin Rawat"},
    "hx1464": {"pwd": "hx1464", "name": "Pramod Kumar"},
    "hx0000": {"pwd": "hx0000", "name": "Devender"},
    "hx0335": {"pwd": "hx0335", "name": "Vinay Solanki"} # ADMIN
}

# --- SERVER-SIDE MEMORY TO TRACK FIRST LOGIN PERMANENTLY FOR THE DAY ---
# Ye function page refresh/logout hone par bhi First Login time ko memory me lock rakhta hai
@st.cache_resource
def get_daily_login_tracker():
    return {}

# Token generate karna taaki URL me session save rahe (Din bhar ke liye)
def generate_token(uname):
    tracker = get_daily_login_tracker()
    today_str = str(datetime.date.today())
    
    # Naya din shuru hote hi purani memory clear karna
    if today_str not in tracker:
        tracker.clear() 
        tracker[today_str] = {}
        
    # Agar user aaj pehli baar aaya hai, toh uska Indian Time (IST) save kar lo
    if uname not in tracker[today_str]:
        ist_timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        tracker[today_str][uname] = datetime.datetime.now(ist_timezone).strftime("%d %b %Y %H:%M")
        
    login_time = tracker[today_str][uname]
    raw = f"{uname}|{datetime.date.today()}|{login_time}"
    return base64.b64encode(raw.encode()).decode()

# Token ko verify karna ki kya wo aaj ka hi token hai
def verify_token(token):
    try:
        raw = base64.b64decode(token).decode()
        parts = raw.split("|")
        if len(parts) == 3:
            uname, date_str, login_time = parts
            if date_str == str(datetime.date.today()) and uname in USERS:
                return uname, login_time
    except:
        pass
    return None, None

# Password check karne ka main function
def check_password():
    # URL mein token check karke auto-login karna
    if "token" in st.query_params:
        valid_user, login_time = verify_token(st.query_params["token"])
        if valid_user:
            st.session_state["password_correct"] = True
            st.session_state["username"] = valid_user
            st.session_state["current_user"] = USERS[valid_user]["name"]
            st.session_state["login_time"] = login_time

    # Agar login nahi hai, toh None rakho taaki error na dikhe
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = None 

    # Submit button dabane ke baad id/password check karna
    def password_entered():
        uname = st.session_state["username_input"].strip().lower()
        pwd = st.session_state["password_input"].strip().lower()
        
        if uname in USERS and USERS[uname]["pwd"] == pwd:
            st.session_state["password_correct"] = True
            st.session_state["username"] = uname
            st.session_state["current_user"] = USERS[uname]["name"]
            
            new_token = generate_token(uname)
            st.query_params["token"] = new_token
            _, login_time = verify_token(new_token)
            st.session_state["login_time"] = login_time
            del st.session_state["password_input"]  
        else:
            st.session_state["password_correct"] = False 

    # Agar password_correct me True nahi hai, toh Login Screen dikhana
    if not st.session_state.get("password_correct"):
        st.markdown("<br><br><br>", unsafe_allow_html=True) 
        col1, col2, col3 = st.columns([1, 1.5, 1]) 
        with col2:
            st.markdown("<h3 style='text-align: center; color: #94a3b8; font-weight: 500; letter-spacing: 2px; margin-bottom: -15px;'>HERO VIRED PVT LTD.</h3>", unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center; font-size: 36px;'>🔐 <span class='gradient-text'>Login to Degree Leads Analysis</span></h1>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Form ka use kiya gaya hai taaki "Press Enter to Apply" ka text na aaye
            with st.form("login_form"):
                st.text_input("Username", key="username_input")
                st.text_input("Password", type="password", key="password_input")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Secure Login", use_container_width=True, on_click=password_entered)
            
            # Sirf tabhi error dikhana jab ID/Pass galat ho (False)
            if st.session_state["password_correct"] == False:
                st.error("😕 Invalid Username or Password")
        return False
    return True

# ==============================================================================
# STEP 4: MAIN DASHBOARD & SIDEBAR LAYOUT
# ==============================================================================
# Agar user successfully login kar leta hai, toh dashboard dikhana
if check_password():
    
    # --- SECURITY: STRICTLY HIDE "MANAGE APP", GITHUB & PENCIL FOR NON-ADMINS ---
    # Is baar hum sirf specific tools hide kar rahe hain taaki Sidebar Unhide (Hamburger) safe rahe.
    if st.session_state["username"] != "hx0335":
        st.markdown("""
            <style>
                /* Right side ke elements (Manage, Github, Menu, Share, Star) hide karna for non-admin */
                [data-testid="stActionElements"],
                [data-testid="stToolbar"],
                button[title="Share app"], 
                button[title="Record a screencast"],
                [data-testid="stToolbar"] button[aria-label="Share"],
                [data-testid="stToolbar"] button[aria-label="Record a screencast"] {
                    display: none !important;
                }
                
                /* 'Deploy' / 'Manage App' top button specific block */
                .stDeployButton {
                    display: none !important;
                }
                
                /* Streamlit Cloud ka floating "Manage App" bottom-right badge strictly hide karna */
                .viewerBadge_container, 
                [class*="viewerBadge"], 
                #manage-app-badge {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
    
    # --- SIDEBAR CREATION ---
    st.sidebar.markdown("<div style='text-align: center; margin-top: -10px; margin-bottom: 5px;'><small style='color: #94a3b8;'><b>Created By Vinay Solanki (HX0335)</b></small></div>", unsafe_allow_html=True)
    st.sidebar.markdown("<h2 style='text-align: center; margin-top: 0px;'>Hero Vired Pvt Ltd.</h2>", unsafe_allow_html=True)
    
    # Center aligned Welcome Name
    st.sidebar.markdown(f"<div style='text-align: center; border-radius: 8px; border: 1px solid rgba(0, 200, 0, 0.3); background-color: rgba(0, 150, 0, 0.05); padding: 5px; color: #e2e8f0; margin-top: 5px; margin-bottom: 5px;'><p style='margin: 0; font-weight: 600;'>Welcome {st.session_state['current_user']}</p></div>", unsafe_allow_html=True)
    
    # Center aligned First Login Time
    if "login_time" in st.session_state:
        st.sidebar.markdown(f"<div style='text-align: center; border-radius: 8px; border: 1px solid rgba(0, 242, 254, 0.3); background-color: rgba(0, 242, 254, 0.05); padding: 5px; color: #e2e8f0; margin-top: 5px; margin-bottom: 5px;'><p style='margin: 0; font-weight: 600;'>🕒 First Login: {st.session_state['login_time']}</p></div>", unsafe_allow_html=True)
        
    st.sidebar.markdown("---")
    
    # Refresh Button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Date Filters (Default is 1st day of month to today)
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    
    start_date = st.sidebar.date_input("Start Date", value=first_day_of_month)
    end_date = st.sidebar.date_input("End Date", value=today)
    
    # Lead Source Filter
    source_filter = st.sidebar.selectbox("Source", ["All", "FACEBOOK", "GOOGLE", "LINKEDIN"])
    
    # Data Ownership Filter (Only for Admins/Managers)
    owner_filter = "All"
    current_username = st.session_state["username"]
    if current_username not in ["hx1192", "hx1464", "hx0000"]:
        owner_filter = st.sidebar.selectbox("Owner", ["All", "Vipin & Pramod", "Devender"])
    
    st.sidebar.markdown("---")
    
    # Logout Button
    if st.sidebar.button("Logout", use_container_width=True):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()

    # Main Dashboard Title
    st.markdown("<h1>🎓 <span class='gradient-text'>Degree Leads Analysis</span></h1>", unsafe_allow_html=True)

# ==============================================================================
# STEP 5: DATA FETCHING FUNCTIONS (MySQL & Google Sheets)
# ==============================================================================
    
    # MySQL Database Connection & Query Execution
    @st.cache_data(ttl=600) 
    def load_data_from_mysql(uname):
        try:
            conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                port=st.secrets["mysql"]["port"],
                database=st.secrets["mysql"]["database"],
                user=st.secrets["mysql"]["username"],
                password=st.secrets["mysql"]["password"]
            )
            
            # User ke hisaab se unko unhi ka data dikhane ki condition
            if uname in ['hx1192', 'hx1464']:
                tags_condition = "('META INHOUSE', 'GOOGLE INHOUSE', 'LINKEDIN INHOUSE')"
            elif uname == 'hx0000':
                tags_condition = "('META-DEVENDER', 'GOOGLE-DEVENDER')"
            else:
                tags_condition = "('META INHOUSE', 'GOOGLE INHOUSE', 'LINKEDIN INHOUSE', 'META-DEVENDER', 'GOOGLE-DEVENDER')"
            
            # Main SQL Query jo database se Data fetch karegi
            query = f"""
            WITH T1 AS (
            SELECT DISTINCT
            c.id as ProspectID,
            cc.prospectstage_c as ProspectStage,
            DATE_FORMAT(DATE_ADD(DATE_ADD(c.date_entered, INTERVAL 5 HOUR), INTERVAL 30 MINUTE), '%Y-%m-%d') AS CreatedOn_Date,
            cc.mx_program_details_c  AS LP_Name,
            cc.lead_source_c  as Lead_Source,
            cc.sourcecampaign_c  as Source_Campaign,
            Case 
            When cc.lead_source_c LIKE '%FB%' Then 'FACEBOOK'
            When cc.lead_source_c LIKE '%Facebook%' Then 'FACEBOOK'
            When cc.lead_source_c LIKE '%Meta%' Then 'FACEBOOK'
            When cc.lead_source_c LIKE '%Google%' Then 'GOOGLE'
            When cc.lead_source_c LIKE '%fmc-website%' Then 'GOOGLE'
            When cc.lead_source_c LIKE '%Inbound Phone call%' Then 'GOOGLE'     
            When cc.lead_source_c LIKE '%Linked%' Then 'LINKEDIN'
            end As Lead_Type,
            DATE_FORMAT(DATE_ADD(DATE_ADD(cc.mx_transition_to_counselled_c , INTERVAL 5 HOUR), INTERVAL 30 MINUTE), '%Y-%m-%d') AS Counselled_DT,
            DATE_FORMAT(DATE_ADD(DATE_ADD(cc.mx_transition_to_offer_c , INTERVAL 5 HOUR), INTERVAL 30 MINUTE), '%Y-%m-%d') AS Offer_DT,
            DATE_FORMAT(DATE_ADD(DATE_ADD(cc.transition_to_converted_c , INTERVAL 5 HOUR), INTERVAL 30 MINUTE), '%Y-%m-%d') AS Converted_DT,
            DATE_FORMAT(DATE_ADD(DATE_ADD(cc.mx_contacted_timestamp_c , INTERVAL 5 HOUR), INTERVAL 30 MINUTE), '%Y-%m-%d') AS Connected_Thirty_sec,
            cc.mx_hyperlap_university_name_c as Hyperlap_University_Name,
            CASE
        WHEN cc.lead_source_c LIKE '%Meta-Devendar%' THEN 'META-DEVENDER'
        WHEN cc.lead_source_c LIKE '%Google-Devender%' THEN 'GOOGLE-DEVENDER'
        WHEN (cc.lead_source_c LIKE '%FB%' OR cc.lead_source_c LIKE '%Facebook%' OR cc.lead_source_c LIKE '%Clever%')
            AND cc.lead_source_c NOT LIKE '%Devender%' 
            AND cc.lead_source_c NOT LIKE '%Devendar%' 
            THEN 'META INHOUSE'
        WHEN (cc.lead_source_c LIKE '%Google%' OR cc.lead_source_c LIKE '%FMC-website%' OR cc.lead_source_c LIKE '%Inbound%')
            AND cc.lead_source_c NOT LIKE '%Devender%' 
            AND cc.lead_source_c NOT LIKE '%Devendar%' 
            THEN 'GOOGLE INHOUSE'
        WHEN cc.lead_source_c LIKE '%Edhike%' THEN 'EDHIKE'
        WHEN cc.lead_source_c LIKE '%LinkedIn%' THEN 'LINKEDIN INHOUSE'
        WHEN cc.lead_source_c LIKE '%Referral%' THEN 'REFERRAL'
        WHEN cc.lead_source_c LIKE '%Collegedunia%' THEN 'COLLEGE DUNIA'
        WHEN cc.lead_source_c LIKE '%Times_Internet%' OR cc.lead_source_c LIKE '%Times%' THEN 'TIMES INTERNET'
        WHEN cc.lead_source_c LIKE '%adovia%' THEN 'ADOVIA'
        WHEN cc.lead_source_c LIKE '%channel%' THEN 'CHANNEL PARTNER'
        ELSE 'OTHER' END AS Source_TAG
        FROM contacts c 
        LEFT JOIN contacts_cstm cc on c.id = cc.id_c 
        WHERE (
            DATE(DATE_ADD(DATE_ADD(c.date_entered, INTERVAL 5 HOUR), INTERVAL 30 MINUTE)) >= DATE_FORMAT(CURRENT_DATE - INTERVAL 1 MONTH, '%Y-%m-01')
            OR DATE(DATE_ADD(DATE_ADD(cc.mx_transition_to_counselled_c, INTERVAL 5 HOUR), INTERVAL 30 MINUTE)) >= DATE_FORMAT(CURRENT_DATE - INTERVAL 1 MONTH, '%Y-%m-01')
            OR DATE(DATE_ADD(DATE_ADD(cc.mx_transition_to_offer_c, INTERVAL 5 HOUR), INTERVAL 30 MINUTE)) >= DATE_FORMAT(CURRENT_DATE - INTERVAL 1 MONTH, '%Y-%m-01')
            OR DATE(DATE_ADD(DATE_ADD(cc.transition_to_converted_c, INTERVAL 5 HOUR), INTERVAL 30 MINUTE)) >= DATE_FORMAT(CURRENT_DATE - INTERVAL 1 MONTH, '%Y-%m-01')
            OR DATE(DATE_ADD(DATE_ADD(cc.mx_contacted_timestamp_c, INTERVAL 5 HOUR), INTERVAL 30 MINUTE)) >= DATE_FORMAT(CURRENT_DATE - INTERVAL 1 MONTH, '%Y-%m-01')
        )
        AND cc.lead_source_c NOT IN ('Bangalore_DataLead_Outsource','Degree_IT_Professionals_Outsource')
        AND NOT (
    CONCAT_WS(' ',  cc.emailaddress_c        , c.first_name , c.last_name) LIKE '%test%' 
    OR CONCAT_WS(' ',  cc.emailaddress_c      , c.first_name , c.last_name) LIKE '%vired%'
    )
    )
    SELECT 
        T1.ProspectID,
        T1.ProspectStage,
        T1.CreatedOn_Date,
        T1.Lead_Source,
        T1.Lead_Type,        
        T1.Source_Campaign,
        T1.Counselled_DT,
        T1.Offer_DT,
        T1.Converted_DT,
        T1.Connected_Thirty_sec,
        T1.Hyperlap_University_Name,
        T1.Source_TAG
    FROM T1
    Where T1.Source_TAG IN {tags_condition}
    AND T1.Lead_Type IN ('FACEBOOK', 'GOOGLE', 'LINKEDIN')
    ORDER BY T1.CreatedOn_Date
            """
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Database connection error: {e}")
            return pd.DataFrame()

    # Inhouse Spends Google Sheet Data Load
    @st.cache_data(ttl=600)
    def load_google_sheet():
        sheet_url = "https://docs.google.com/spreadsheets/d/1dD2DmVLAMOkdCe1dwUAO9eX5S5_31ikovd0UyoYDiZI/export?format=csv&gid=945195723"
        try:
            df = pd.read_csv(sheet_url)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Failed to load Overall Spends Google Sheet: {e}")
            return pd.DataFrame()

    # Devender Spends Google Sheet Data Load
    @st.cache_data(ttl=600)
    def load_devender_spends():
        sheet_url = "https://docs.google.com/spreadsheets/d/1KJ--JKXJqtP_yTiW-Ok0PpIADv9AXyagspFfZBiYChY/export?format=csv&gid=1016805741"
        try:
            df = pd.read_csv(sheet_url)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Failed to load Devender Spends Sheet: {e}")
            return pd.DataFrame()

    # Enrolled (Booked Amount) Data Google Sheet Data Load
    @st.cache_data(ttl=600)
    def load_enrolled_data():
        sheet_url = "https://docs.google.com/spreadsheets/d/1hMcaFk4l9xmOUK6lB0LgpWMbHZkLDrMzzQUi8oBX6J8/export?format=csv&gid=0"
        try:
            df = pd.read_csv(sheet_url)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Failed to load Enrolled Data Sheet: {e}")
            return pd.DataFrame()

    # Ek sath saare Data functions ko Call karna
    raw_data = load_data_from_mysql(current_username)
    gs_data = load_google_sheet()
    devender_data = load_devender_spends()
    enrolled_data = load_enrolled_data()

# ==============================================================================
# STEP 6: DATA PREPROCESSING & TABS GENERATION
# ==============================================================================
    # Streamlit me 5 TABS create karna
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Search & RAW Data", "📈 University Analytics", "📈 Campaign Analytics", "📊 Daily Leads", "💰 ROAS Dashboard"])

    if not raw_data.empty:
        # Saari Universities ko Alphabetical Sort kar lena
        all_universities = sorted(raw_data['Hyperlap_University_Name'].dropna().unique())
        
        # Sidebar ke 'Source' Filter ko Data par apply karna
        if source_filter != "All":
            filtered_data = raw_data[raw_data['Lead_Type'] == source_filter].copy()
        else:
            filtered_data = raw_data.copy()

        # Sidebar ke 'Owner' Filter ko Data par apply karna
        if owner_filter == "Vipin & Pramod":
            filtered_data = filtered_data[filtered_data['Source_TAG'].isin(['META INHOUSE', 'GOOGLE INHOUSE', 'LINKEDIN INHOUSE'])]
        elif owner_filter == "Devender":
            filtered_data = filtered_data[filtered_data['Source_TAG'].isin(['META-DEVENDER', 'GOOGLE-DEVENDER'])]

        # Data ke Andar sabhi Date Columns ko standard TimeStamp me badalna taaki filter kaam kare
        date_cols = ['CreatedOn_Date', 'Connected_Thirty_sec', 'Counselled_DT', 'Offer_DT', 'Converted_DT']
        for col in date_cols:
            filtered_data[col] = pd.to_datetime(filtered_data[col], errors='coerce')

        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)

    # -------------------------------------------------------------------------
    # TAB 1: SEARCH & RAW DATA
    # -------------------------------------------------------------------------
    with tab1:
        if not raw_data.empty:
            search_query = st.text_input("Search any keyword...")
            if search_query:
                # Agar search kiya hai, toh wo filter karega
                mask = filtered_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
                search_df = filtered_data[mask]
                display_df = search_df.copy()
                for col in date_cols: display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
            else:
                # Warna pura data dikhayega
                display_df = filtered_data.copy()
                for col in date_cols: display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
            
            # --- CSV DOWNLOAD BUTTON FOR TAB 1 ---
            colA, colB = st.columns([8, 2])
            with colB:
                st.download_button(label="📥 Download CSV", data=display_df.to_csv(index=False).encode('utf-8'), file_name="Raw_Data.csv", mime="text/csv", use_container_width=True)
            
            st.dataframe(display_df, use_container_width=True, height=min(750, (len(display_df) + 1) * 36 + 10))
            st.caption(f"Total Rows Fetched: {len(filtered_data)}")
        else:
            st.warning("Data failed to load. Please check your SQL Query or Database connection.")

    # -------------------------------------------------------------------------
    # TAB 2: UNIVERSITY ANALYTICS
    # -------------------------------------------------------------------------
    with tab2:
        if not raw_data.empty:
            if start_date <= end_date:
                # Date ke hisaab se basic data filter karna
                created_mask = (filtered_data['CreatedOn_Date'] >= start_ts) & (filtered_data['CreatedOn_Date'] <= end_ts)
                df_created = filtered_data[created_mask]

                # Booked Amount ka Data Google Sheet se nikalna (with crash safety)
                enrolled_filtered_tab2 = pd.DataFrame()
                if not enrolled_data.empty:
                    enr_data_safe = enrolled_data.copy()
                    date_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'CONVERTED DATE'), None)
                    uni_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'ENROLLED UNIVERSITY'), None)
                    acc_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'TOTAL ACCRUED AMOUNT'), None)
                    tag_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'CONVERTED SOURCE TAG'), None)
                    
                    if date_col and uni_col and acc_col and tag_col:
                        enr_data_safe[date_col] = pd.to_datetime(enr_data_safe[date_col], errors='coerce').dt.date
                        # Comma hata kar Number banana (Crash preventer)
                        enr_data_safe[acc_col] = pd.to_numeric(enr_data_safe[acc_col].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
                        
                        valid_tags = filtered_data['Source_TAG'].dropna().unique()
                        valid_tags_clean = [str(t).replace(' ', '').replace('-', '').upper() for t in valid_tags]
                        # Spelling Fixes for Devender
                        if 'METADEVENDER' in valid_tags_clean: valid_tags_clean.append('METADEVENDAR')
                        if 'GOOGLEDEVENDER' in valid_tags_clean: valid_tags_clean.append('GOOGLEDEVENDAR')
                        enr_tags_clean = enr_data_safe[tag_col].astype(str).str.replace(' ', '', regex=False).str.replace('-', '', regex=False).str.upper()
                        enrolled_filtered_tab2 = enr_data_safe[(enr_data_safe[date_col] >= start_date) & (enr_data_safe[date_col] <= end_date) & (enr_tags_clean.isin(valid_tags_clean))]

                # Har University ki Metrics count karna
                report_data = []
                for uni in all_universities:
                    df_uni_sm = df_created[df_created['Hyperlap_University_Name'] == uni]
                    df_uni_overall = filtered_data[filtered_data['Hyperlap_University_Name'] == uni]
                    lead_received = len(df_uni_sm)
                    
                    booked_amount = 0.0
                    if not enrolled_filtered_tab2.empty:
                        clean_enrolled_unis = enrolled_filtered_tab2[uni_col].astype(str).str.replace('_', ' ').str.strip().str.upper().str.replace(' ', '', regex=False)
                        clean_uni = str(uni).replace('_', ' ').strip().upper().replace(' ', '')
                        booked_amount = float(enrolled_filtered_tab2[clean_enrolled_unis == clean_uni][acc_col].sum())
                    
                    facebook_count = len(df_uni_sm[df_uni_sm['Lead_Type'] == 'FACEBOOK'])
                    google_count = len(df_uni_sm[df_uni_sm['Lead_Type'] == 'GOOGLE'])
                    linkedin_count = len(df_uni_sm[df_uni_sm['Lead_Type'] == 'LINKEDIN'])
                    junk_sm_mask = df_uni_sm['ProspectStage'].astype(str).str.lower().str.contains('l1_lost|l2_lost|l1 lost|l2 lost', regex=True, na=False)
                    junk_sm = len(df_uni_sm[junk_sm_mask])
                    junk_pct = junk_sm / lead_received if lead_received > 0 else 0
                    junk_overall_mask = df_uni_overall['ProspectStage'].astype(str).str.lower().str.contains('l1_lost|l2_lost|l1 lost|l2 lost', regex=True, na=False)
                    junk_overall = len(df_uni_overall[junk_overall_mask])
                    conn_30_sm_mask = (df_uni_sm['Connected_Thirty_sec'] >= start_ts) & (df_uni_sm['Connected_Thirty_sec'] <= end_ts)
                    conn_30_sm = len(df_uni_sm[conn_30_sm_mask])
                    conn_30_sm_pct = conn_30_sm / lead_received if lead_received > 0 else 0
                    conn_overall_mask = (df_uni_overall['Connected_Thirty_sec'] >= start_ts) & (df_uni_overall['Connected_Thirty_sec'] <= end_ts)
                    conn_30_overall = len(df_uni_overall[conn_overall_mask])
                    couns_sm_mask = (df_uni_sm['Counselled_DT'] >= start_ts) & (df_uni_sm['Counselled_DT'] <= end_ts)
                    couns_sm = len(df_uni_sm[couns_sm_mask])
                    couns_sm_pct = couns_sm / conn_30_sm if conn_30_sm > 0 else 0
                    couns_overall_mask = (df_uni_overall['Counselled_DT'] >= start_ts) & (df_uni_overall['Counselled_DT'] <= end_ts)
                    couns_overall = len(df_uni_overall[couns_overall_mask])
                    offer_sm_mask = (df_uni_sm['Offer_DT'] >= start_ts) & (df_uni_sm['Offer_DT'] <= end_ts)
                    offer_sm = len(df_uni_sm[offer_sm_mask])
                    offer_overall_mask = (df_uni_overall['Offer_DT'] >= start_ts) & (df_uni_overall['Offer_DT'] <= end_ts)
                    offer_overall = len(df_uni_overall[offer_overall_mask])
                    conv_sm_mask = (df_uni_sm['Converted_DT'] >= start_ts) & (df_uni_sm['Converted_DT'] <= end_ts)
                    conv_sm = len(df_uni_sm[conv_sm_mask])
                    conv_overall_mask = (df_uni_overall['Converted_DT'] >= start_ts) & (df_uni_overall['Converted_DT'] <= end_ts)
                    conv_overall = len(df_uni_overall[conv_overall_mask])

                    report_data.append({
                        "Hyperlap Universities": uni, "Lead Received": lead_received, "Facebook": facebook_count,
                        "Google": google_count, "LinkedIn": linkedin_count, "Junk SM": junk_sm, "Junk SM %": junk_pct,
                        "Junk Overall": junk_overall, "Connected 30 Sec SM": conn_30_sm, "Connected 30 Sec SM %": conn_30_sm_pct,
                        "Connected 30 Sec Overall": conn_30_overall, "Counselled SM": couns_sm, "Counselled SM %": couns_sm_pct,
                        "Counselled Overall": couns_overall, "Offer SM": offer_sm, "Offer Overall": offer_overall,
                        "Converted SM": conv_sm, "Converted Overall": conv_overall, "Booked Amount": booked_amount,
                        "Offer To Counselled % SM": offer_sm / couns_sm if couns_sm > 0 else 0,
                        "Offer To Converted % SM": conv_sm / offer_sm if offer_sm > 0 else 0,
                        "Counselled To Converted % SM": conv_sm / couns_sm if couns_sm > 0 else 0,
                        "Lead To Converted % SM": conv_sm / lead_received if lead_received > 0 else 0
                    })

                report_df = pd.DataFrame(report_data)
                
                # --- GRAND TOTAL ROW LOGIC ---
                total_row = {'Hyperlap Universities': 'Grand Total'}
                sum_columns = ['Lead Received', 'Facebook', 'Google', 'LinkedIn', 'Junk SM', 'Junk Overall', 'Connected 30 Sec SM', 'Connected 30 Sec Overall', 'Counselled SM', 'Counselled Overall', 'Offer SM', 'Offer Overall', 'Converted SM', 'Converted Overall', 'Booked Amount']
                for col in sum_columns: total_row[col] = report_df[col].sum()
                
                # Grand Total Row ko Dataframe ke TOP (Index 0) par jodna
                report_df = pd.concat([pd.DataFrame([total_row]), report_df], ignore_index=True)
                
                # Top Row par Division (Percentages) ko thik karna
                report_df.at[0, 'Junk SM %'] = report_df.at[0, 'Junk SM'] / report_df.at[0, 'Lead Received'] if report_df.at[0, 'Lead Received'] > 0 else 0
                report_df.at[0, 'Connected 30 Sec SM %'] = report_df.at[0, 'Connected 30 Sec SM'] / report_df.at[0, 'Lead Received'] if report_df.at[0, 'Lead Received'] > 0 else 0
                report_df.at[0, 'Counselled SM %'] = report_df.at[0, 'Counselled SM'] / report_df.at[0, 'Connected 30 Sec SM'] if report_df.at[0, 'Connected 30 Sec SM'] > 0 else 0
                report_df.at[0, 'Offer To Counselled % SM'] = report_df.at[0, 'Offer SM'] / report_df.at[0, 'Counselled SM'] if report_df.at[0, 'Counselled SM'] > 0 else 0
                report_df.at[0, 'Offer To Converted % SM'] = report_df.at[0, 'Converted SM'] / report_df.at[0, 'Offer SM'] if report_df.at[0, 'Offer SM'] > 0 else 0
                report_df.at[0, 'Counselled To Converted % SM'] = report_df.at[0, 'Converted SM'] / report_df.at[0, 'Counselled SM'] if report_df.at[0, 'Counselled SM'] > 0 else 0
                report_df.at[0, 'Lead To Converted % SM'] = report_df.at[0, 'Converted SM'] / report_df.at[0, 'Lead Received'] if report_df.at[0, 'Lead Received'] > 0 else 0
                
                # Formatting Dena (Decimal places % aur Float)
                styled_report = report_df.style.format({
                    "Booked Amount": "{:.2f}", "Junk SM %": "{:.2%}", "Connected 30 Sec SM %": "{:.2%}",
                    "Counselled SM %": "{:.2%}", "Offer To Counselled % SM": "{:.2%}", "Offer To Converted % SM": "{:.2%}",
                    "Counselled To Converted % SM": "{:.2%}", "Lead To Converted % SM": "{:.2%}"
                })
                
                # --- CSV DOWNLOAD BUTTON FOR TAB 2 ---
                colA, colB = st.columns([8, 2])
                with colB:
                    st.download_button(label="📥 Download CSV", data=report_df.to_csv(index=False).encode('utf-8'), file_name="University_Analytics.csv", mime="text/csv", use_container_width=True)
                
                st.dataframe(styled_report, use_container_width=True, height=min(750, (len(report_df) + 1) * 36 + 10))
            else:
                st.error("❌ End Date cannot be earlier than the Start Date!")

    # -------------------------------------------------------------------------
    # TAB 3: CAMPAIGN ANALYTICS
    # -------------------------------------------------------------------------
    with tab3:
        if not raw_data.empty:
            if start_date <= end_date:
                created_mask = (filtered_data['CreatedOn_Date'] >= start_ts) & (filtered_data['CreatedOn_Date'] <= end_ts)
                df_created = filtered_data[created_mask]
                
                # Google Sheet ka Spend Load Karna Safely
                if not gs_data.empty and all(col in gs_data.columns for col in ['Day', 'Cost', 'Campaign', 'Source']):
                    gs_data_safe = gs_data.copy()
                    gs_data_safe['Day'] = pd.to_datetime(gs_data_safe['Day'], errors='coerce').dt.date
                    
                    # Commas remove karna taaki float ban sake (prevent String crash)
                    gs_data_safe['Cost'] = pd.to_numeric(gs_data_safe['Cost'].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
                    
                    gs_mask = (gs_data_safe['Day'] >= start_date) & (gs_data_safe['Day'] <= end_date)
                    gs_filtered = gs_data_safe[gs_mask].copy()
                    
                    if source_filter != "All":
                        if source_filter == "GOOGLE": gs_filtered = gs_filtered[gs_filtered['Source'].astype(str).str.strip().str.upper() == 'GOOGLE INHOUSE']
                        elif source_filter == "FACEBOOK": gs_filtered = gs_filtered[gs_filtered['Source'].astype(str).str.strip().str.upper() == 'META INHOUSE']
                        elif source_filter == "LINKEDIN": gs_filtered = gs_filtered[gs_filtered['Source'].astype(str).str.strip().str.upper().str.contains('LINKEDIN', na=False)]
                    all_campaigns_gs = sorted(gs_filtered['Campaign'].dropna().unique())
                else:
                    gs_filtered = pd.DataFrame(); all_campaigns_gs = []

                # Har Campaign ki metrics count karna
                report_data_camp = []
                for camp in all_campaigns_gs:
                    camp_spend = float(gs_filtered[gs_filtered['Campaign'] == camp]['Cost'].sum())
                    df_camp_sm = df_created[df_created['Source_Campaign'] == camp]
                    df_camp_overall = filtered_data[filtered_data['Source_Campaign'] == camp]
                    lead_received = len(df_camp_sm)
                    facebook_count = len(df_camp_sm[df_camp_sm['Lead_Type'] == 'FACEBOOK'])
                    google_count = len(df_camp_sm[df_camp_sm['Lead_Type'] == 'GOOGLE'])
                    linkedin_count = len(df_camp_sm[df_camp_sm['Lead_Type'] == 'LINKEDIN'])
                    report_data_camp.append({
                        "Source Campaign": camp, "Spend": camp_spend, "Lead Received": lead_received,
                        "Facebook": facebook_count, "Google": google_count, "LinkedIn": linkedin_count,
                        "Junk SM": len(df_camp_sm[df_camp_sm['ProspectStage'].astype(str).str.lower().str.contains('l1_lost|l2_lost|l1 lost|l2 lost', regex=True, na=False)]),
                        "Connected 30 Sec SM": len(df_camp_sm[(df_camp_sm['Connected_Thirty_sec'] >= start_ts) & (df_camp_sm['Connected_Thirty_sec'] <= end_ts)]),
                        "Counselled SM": len(df_camp_sm[(df_camp_sm['Counselled_DT'] >= start_ts) & (df_camp_sm['Counselled_DT'] <= end_ts)]),
                        "Offer SM": len(df_camp_sm[(df_camp_sm['Offer_DT'] >= start_ts) & (df_camp_sm['Offer_DT'] <= end_ts)]),
                        "Converted SM": len(df_camp_sm[(df_camp_sm['Converted_DT'] >= start_ts) & (df_camp_sm['Converted_DT'] <= end_ts)])
                    })
                
                if report_data_camp:
                    report_df_camp = pd.DataFrame(report_data_camp)
                    
                    # --- GRAND TOTAL ROW AT THE TOP ---
                    total_row_camp = {'Source Campaign': 'Grand Total'}
                    sum_columns_camp = ['Spend', 'Lead Received', 'Facebook', 'Google', 'LinkedIn', 'Junk SM', 'Connected 30 Sec SM', 'Counselled SM', 'Offer SM', 'Converted SM']
                    for col in sum_columns_camp: total_row_camp[col] = report_df_camp[col].sum()
                    
                    report_df_camp = pd.concat([pd.DataFrame([total_row_camp]), report_df_camp], ignore_index=True)
                    
                    # --- CSV DOWNLOAD BUTTON FOR TAB 3 ---
                    colA, colB = st.columns([8, 2])
                    with colB:
                        st.download_button(label="📥 Download CSV", data=report_df_camp.to_csv(index=False).encode('utf-8'), file_name="Campaign_Analytics.csv", mime="text/csv", use_container_width=True)
                    
                    st.dataframe(report_df_camp, use_container_width=True, height=min(750, (len(report_df_camp) + 1) * 36 + 10))
                else: st.info("No Campaign Data found.")

    # -------------------------------------------------------------------------
    # TAB 4: DAILY LEAD RECEIVED (Present Day Only)
    # -------------------------------------------------------------------------
    with tab4:
        if not raw_data.empty:
            today_ts = pd.to_datetime(datetime.date.today())
            
            # Subheader aur Download Button ko arrange karna
            colA, colB = st.columns([8, 2])
            with colA:
                st.subheader(f"📅 Daily Leads Received (Today: {today_ts.strftime('%d %b %Y')})")
            
            # Sirf Aaj ka data filter karna
            df_today = filtered_data[filtered_data['CreatedOn_Date'] == today_ts]
            
            # Required Universities mapping
            uni_mapping = {"ALLIANCE UNIVERSITY": "alliance", "AMITY UNIVERSITY": "amity", "BHARATI VIDYAPEETH UNIVERSITY": "bharati", "DR. D Y PATIL UNIVERSITY": "patil", "GALGOTIAS UNIVERSITY": "galgotias", "GENERIC UNIVERSITY": "generic", "GLA UNIVERSITY": "gla", "LOVELY PROFESSIONAL UNIVERSITY": "lovely", "MANIPAL UNIVERSITY": "manipal", "NMIMS": "nmims", "SHOOLINI UNIVERSITY": "shoolini", "UTTARANCHAL UNIVERSITY": "uttaranchal"}
            
            daily_report_data = []
            for display_name, search_key in uni_mapping.items():
                df_uni_today = df_today[df_today['Hyperlap_University_Name'].astype(str).str.contains(search_key, case=False, na=False)]
                daily_report_data.append({"HYPERLAP_UNIVERSITY_NAME": display_name, "GOOGLE-DEVENDER": len(df_uni_today[df_uni_today['Source_TAG'] == 'GOOGLE-DEVENDER']), "META-DEVENDER": len(df_uni_today[df_uni_today['Source_TAG'] == 'META-DEVENDER']), "GOOGLE INHOUSE": len(df_uni_today[df_uni_today['Source_TAG'] == 'GOOGLE INHOUSE']), "META INHOUSE": len(df_uni_today[df_uni_today['Source_TAG'] == 'META INHOUSE']), "LINKEDIN INHOUSE": len(df_uni_today[df_uni_today['Source_TAG'] == 'LINKEDIN INHOUSE']), "TOTAL LEADS": len(df_uni_today)})
            
            df_daily = pd.DataFrame(daily_report_data)
            
            # --- GRAND TOTAL ROW AT THE TOP ---
            total_row_daily = {"HYPERLAP_UNIVERSITY_NAME": "GRAND TOTAL"}
            sum_cols_daily = ["GOOGLE-DEVENDER", "META-DEVENDER", "GOOGLE INHOUSE", "META INHOUSE", "LINKEDIN INHOUSE", "TOTAL LEADS"]
            for col in sum_cols_daily: total_row_daily[col] = df_daily[col].sum()
            
            df_daily = pd.concat([pd.DataFrame([total_row_daily]), df_daily], ignore_index=True)
            
            # --- CSV DOWNLOAD BUTTON FOR TAB 4 ---
            with colB:
                st.download_button(label="📥 Download CSV", data=df_daily.to_csv(index=False).encode('utf-8'), file_name="Daily_Leads.csv", mime="text/csv", use_container_width=True)
            
            st.dataframe(df_daily, use_container_width=True, height=min(750, (len(df_daily) + 1) * 36 + 10))

    # -------------------------------------------------------------------------
    # TAB 5: ROAS DASHBOARD
    # -------------------------------------------------------------------------
    with tab5:
        if not raw_data.empty:
            if start_date <= end_date:
                df_created = filtered_data[(filtered_data['CreatedOn_Date'] >= start_ts) & (filtered_data['CreatedOn_Date'] <= end_ts)]
                valid_unis_clean = [str(u).replace('_', ' ').strip().upper() for u in filtered_data['Hyperlap_University_Name'].dropna().unique()]
                unique_tags = sorted(filtered_data['Source_TAG'].dropna().unique())
                
                # --- CLEANING SPENDS DATA EXPLICITLY TO PREVENT STRING CRASHES ---
                gs_inhouse_filtered = pd.DataFrame()
                if not gs_data.empty and 'Day' in gs_data.columns and 'Cost' in gs_data.columns:
                    temp_gs = gs_data.copy()
                    temp_gs['Day'] = pd.to_datetime(temp_gs['Day'], errors='coerce').dt.date
                    temp_gs['Cost'] = pd.to_numeric(temp_gs['Cost'].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
                    gs_inhouse_filtered = temp_gs[(temp_gs['Day'] >= start_date) & (temp_gs['Day'] <= end_date)]

                gs_dev_filtered = pd.DataFrame()
                if not devender_data.empty and 'Date' in devender_data.columns:
                    temp_dev = devender_data.copy()
                    temp_dev['Date'] = pd.to_datetime(temp_dev['Date'], errors='coerce').dt.date
                    if 'Google Spend' in temp_dev.columns:
                        temp_dev['Google Spend'] = pd.to_numeric(temp_dev['Google Spend'].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
                    if 'Facebook Spend' in temp_dev.columns:
                        temp_dev['Facebook Spend'] = pd.to_numeric(temp_dev['Facebook Spend'].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
                    gs_dev_filtered = temp_dev[(temp_dev['Date'] >= start_date) & (temp_dev['Date'] <= end_date)]
                
                roas_data = []
                for tag in unique_tags:
                    spend = 0.0
                    booked_amount = 0.0
                    
                    # Spend logic map karna
                    if tag == 'META INHOUSE' and not gs_inhouse_filtered.empty:
                        spend = float(gs_inhouse_filtered[gs_inhouse_filtered['Source'].astype(str).str.strip().str.upper() == 'META INHOUSE']['Cost'].sum())
                    elif tag == 'GOOGLE INHOUSE' and not gs_inhouse_filtered.empty:
                        spend = float(gs_inhouse_filtered[gs_inhouse_filtered['Source'].astype(str).str.strip().str.upper() == 'GOOGLE INHOUSE']['Cost'].sum())
                    elif tag == 'LINKEDIN INHOUSE' and not gs_inhouse_filtered.empty:
                        spend = float(gs_inhouse_filtered[gs_inhouse_filtered['Source'].astype(str).str.strip().str.upper().str.contains('LINKEDIN', na=False)]['Cost'].sum())
                    elif tag == 'META-DEVENDER' and not gs_dev_filtered.empty and 'Facebook Spend' in gs_dev_filtered.columns:
                        spend = float(gs_dev_filtered['Facebook Spend'].sum())
                    elif tag == 'GOOGLE-DEVENDER' and not gs_dev_filtered.empty and 'Google Spend' in gs_dev_filtered.columns:
                        spend = float(gs_dev_filtered['Google Spend'].sum())

                    df_tag_sm = df_created[df_created['Source_TAG'] == tag]
                    lead_received = len(df_tag_sm)
                    conv_sm = len(df_tag_sm[(df_tag_sm['Converted_DT'] >= start_ts) & (df_tag_sm['Converted_DT'] <= end_ts)])
                    conv_ovr = len(filtered_data[(filtered_data['Source_TAG'] == tag) & (filtered_data['Converted_DT'] >= start_ts) & (filtered_data['Converted_DT'] <= end_ts)])
                    
                    # Booked amount map karna
                    if not enrolled_data.empty:
                        enr_data_safe = enrolled_data.copy()
                        date_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'CONVERTED DATE'), None)
                        conv_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'CONVERTED SOURCE TAG'), None)
                        acc_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'TOTAL ACCRUED AMOUNT'), None)
                        
                        if date_col and conv_col and acc_col:
                            enr_data_safe[date_col] = pd.to_datetime(enr_data_safe[date_col], errors='coerce').dt.date
                            enr_data_safe[acc_col] = pd.to_numeric(enr_data_safe[acc_col].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
                            
                            enrolled_filtered = enr_data_safe[(enr_data_safe[date_col] >= start_date) & (enr_data_safe[date_col] <= end_date)]
                            enrolled_tags = enrolled_filtered[conv_col].astype(str).str.strip().str.upper()
                            clean_enrolled = enrolled_tags.str.replace(' ', '', regex=False).str.replace('-', '', regex=False)
                            clean_tag = tag.upper().replace(' ', '').replace('-', '')
                            
                            if clean_tag in ['METADEVENDER', 'METADEVENDAR']: mask = clean_enrolled.isin(['METADEVENDER', 'METADEVENDAR'])
                            elif clean_tag in ['GOOGLEDEVENDER', 'GOOGLEDEVENDAR']: mask = clean_enrolled.isin(['GOOGLEDEVENDER', 'GOOGLEDEVENDAR'])
                            else: mask = clean_enrolled == clean_tag
                            
                            booked_amount = float(enrolled_filtered[mask][acc_col].sum())

                    # ROAS Dashboard Data Append karna
                    roas_data.append({"Source Tag": tag, "Spends": spend, "Lead Received": lead_received, "CPL": spend/lead_received if lead_received>0 else 0, "Converted SM": conv_sm, "Converted Overall": conv_ovr, "Booked Amount": booked_amount, "Booked ROAS": booked_amount/spend if spend>0 else 0, "CAC": spend/conv_ovr if conv_ovr>0 else 0, "Lead To Converted SM %": conv_sm/lead_received if lead_received>0 else 0, "Lead To Converted Overall %": conv_ovr/lead_received if lead_received>0 else 0})
                
                if roas_data:
                    roas_df = pd.DataFrame(roas_data)
                    
                    # --- GRAND TOTAL ROW AT THE TOP ---
                    total_row = {"Source Tag": "GRAND TOTAL"}
                    for col in ["Spends", "Lead Received", "Converted SM", "Converted Overall", "Booked Amount"]: total_row[col] = roas_df[col].sum()
                    
                    # Insert Total Row at index 0 (Top)
                    roas_df = pd.concat([pd.DataFrame([total_row]), roas_df], ignore_index=True)
                    
                    # Formula for Total Row
                    roas_df.at[0, "CPL"] = roas_df.at[0, "Spends"] / roas_df.at[0, "Lead Received"] if roas_df.at[0, "Lead Received"] > 0 else 0
                    roas_df.at[0, "Booked ROAS"] = roas_df.at[0, "Booked Amount"] / roas_df.at[0, "Spends"] if roas_df.at[0, "Spends"] > 0 else 0
                    roas_df.at[0, "CAC"] = roas_df.at[0, "Spends"] / roas_df.at[0, "Converted Overall"] if roas_df.at[0, "Converted Overall"] > 0 else 0
                    roas_df.at[0, "Lead To Converted SM %"] = roas_df.at[0, "Converted SM"] / roas_df.at[0, "Lead Received"] if roas_df.at[0, "Lead Received"] > 0 else 0
                    roas_df.at[0, "Lead To Converted Overall %"] = roas_df.at[0, "Converted Overall"] / roas_df.at[0, "Lead Received"] if roas_df.at[0, "Lead Received"] > 0 else 0
                    
                    # Final sequence user ki manga gayi list ke mutabik
                    col_order = ["Source Tag", "Spends", "Lead Received", "CPL", "Converted SM", "Converted Overall", "Booked Amount", "Booked ROAS", "CAC", "Lead To Converted SM %", "Lead To Converted Overall %"]
                    
                    # --- CSV DOWNLOAD BUTTON FOR TAB 5 ---
                    colA, colB = st.columns([8, 2])
                    with colB:
                        st.download_button(label="📥 Download CSV", data=roas_df[col_order].to_csv(index=False).encode('utf-8'), file_name="ROAS_Dashboard.csv", mime="text/csv", use_container_width=True)
                        
                    styled_roas = roas_df[col_order].style.format({"Spends": "{:.2f}", "CPL": "{:.2f}", "Booked Amount": "{:.2f}", "Booked ROAS": "{:.2f}", "CAC": "{:.2f}", "Lead To Converted SM %": "{:.2%}", "Lead To Converted Overall %": "{:.2%}"})
                    st.dataframe(styled_roas, use_container_width=True, height=min(750, (len(roas_df) + 1) * 36 + 10))
                else: st.info("No data available for ROAS Dashboard in the selected date range.")
