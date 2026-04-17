import streamlit as st
import pandas as pd
import mysql.connector
import datetime
import base64

# --- 1. PAGE CONFIGURATION & PROFESSIONAL UI ---
st.set_page_config(page_title="Degree Leads Analysis", page_icon="🎓", layout="wide")

st.markdown("""
<style>
    /* Main Title Styling */
    h1 {
        background: -webkit-linear-gradient(#4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    /* Highlight/Glow Effect on Mouse Hover */
    .stTextInput>div>div>input:hover, 
    .stDateInput>div>div>input:hover, 
    .stSelectbox>div>div>div:hover {
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.6) !important;
        transition: 0.3s ease-in-out;
    }
    
    /* Highlight effect for Dataframes */
    .stDataFrame:hover {
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.4);
        border-radius: 10px;
        transition: 0.3s ease-in-out;
    }
    
    /* Stylish Buttons */
    .stButton>button {
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
        transform: scale(1.02);
    }
    
    /* Remove Empty Space at the Top to Shift Content Up */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ADVANCED LOGIN SYSTEM (Till Midnight Persistence) ---
USERS = {
    "hx1001": {"pwd": "hx1001", "name": "Vipul Bhatnagar"},
    "hx1192": {"pwd": "hx1192", "name": "Vipin Rawat"},
    "hx1464": {"pwd": "hx1464", "name": "Pramod Kumar"},
    "hx0000": {"pwd": "hx0000", "name": "Devender"},
    "hx0335": {"pwd": "hx0335", "name": "Vinay Solanki"} # ADMIN
}

def generate_token(uname):
    """Generates a token valid only for today"""
    raw = f"{uname}|{datetime.date.today()}"
    return base64.b64encode(raw.encode()).decode()

def verify_token(token):
    """Checks if token is valid and belongs to today"""
    try:
        raw = base64.b64decode(token).decode()
        uname, date_str = raw.split("|")
        if date_str == str(datetime.date.today()) and uname in USERS:
            return uname
    except:
        pass
    return None

def check_password():
    # Check if a valid token already exists in URL (for browser refresh)
    if "token" in st.query_params:
        valid_user = verify_token(st.query_params["token"])
        if valid_user:
            st.session_state["password_correct"] = True
            st.session_state["username"] = valid_user
            st.session_state["current_user"] = USERS[valid_user]["name"]

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    def password_entered():
        uname = st.session_state["username_input"].strip().lower()
        pwd = st.session_state["password_input"].strip().lower()
        
        if uname in USERS and USERS[uname]["pwd"] == pwd:
            st.session_state["password_correct"] = True
            st.session_state["username"] = uname
            st.session_state["current_user"] = USERS[uname]["name"]
            # Set Token in URL
            st.query_params["token"] = generate_token(uname)
            del st.session_state["password_input"]  
        else:
            st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Login to Degree Leads Analysis")
        st.text_input("Username", key="username_input")
        st.text_input("Password", type="password", key="password_input")
        st.button("Login", on_click=password_entered)
        
        if "password_correct" in st.session_state and st.session_state["password_correct"] == False:
            st.error("😕 Invalid Username or Password")
        return False
    return True

# --- 3. MAIN DASHBOARD ---
if check_password():
    
    # Security Rule: Hide Top Cloud Menu for non-admins (anyone except hx0335)
    if st.session_state["username"] != "hx0335":
        st.markdown("""
            <style>
                /* Hides ONLY the Streamlit top right menu (Manage App, GitHub, etc.), keeping Sidebar Toggle safe */
                [data-testid="stToolbar"] {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
    
    # --- SIDEBAR ---
    st.sidebar.title("Navigations")
    st.sidebar.success(f"Welcome {st.session_state['current_user']}")
    st.sidebar.markdown("---")
    
    # Explicit Refresh Button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
        
    st.sidebar.markdown("---")
    
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    
    start_date = st.sidebar.date_input("Start Date", value=first_day_of_month)
    end_date = st.sidebar.date_input("End Date", value=today)
    
    source_filter = st.sidebar.selectbox("Source", ["All", "FACEBOOK", "GOOGLE", "LINKEDIN"])
    
    # OWNER FILTER (Dynamic rule implementation)
    owner_filter = "All"
    current_username = st.session_state["username"]
    
    if current_username not in ["hx1192", "hx1464", "hx0000"]:
        owner_filter = st.sidebar.selectbox("Owner", ["All", "Vipin & Pramod", "Devender"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()

    st.title("🎓 Degree Leads Analysis")

    # --- DATABASE & GOOGLE SHEET CONNECTION ---
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
            
            # Decide SQL tags dynamically based on exact user mapping
            if uname in ['hx1192', 'hx1464']:
                tags_condition = "('META INHOUSE', 'GOOGLE INHOUSE', 'LINKEDIN INHOUSE')"
            elif uname == 'hx0000':
                tags_condition = "('META-DEVENDER', 'GOOGLE-DEVENDER')"
            else:
                tags_condition = "('META INHOUSE', 'GOOGLE INHOUSE', 'LINKEDIN INHOUSE', 'META-DEVENDER', 'GOOGLE-DEVENDER')"
            
            query = f"""
            WITH T1 AS (
            SELECT DISTINCT
            c.id as ProspectID,
            cc.prospectstage_c as ProspectStage,
            DATE_FORMAT(DATE_ADD(DATE_ADD(c.date_entered, INTERVAL 5 HOUR), INTERVAL 30 MINUTE), '%Y-%m-%d') AS CreatedOn_Date,
            cc.mx_program_details_c  AS LP_Name,
            cc.lead_source_c  as Lead_Source,
            cc.sourcecampaign_c  as Source_Campaign,
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
    CONCAT_WS(' ',  cc.emailaddress_c        , c.first_name , c.last_name) LIKE '%test%' 
    OR CONCAT_WS(' ',  cc.emailaddress_c      , c.first_name , c.last_name) LIKE '%vired%'
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

    @st.cache_data(ttl=600)
    def load_google_sheet():
        sheet_url = "https://docs.google.com/spreadsheets/d/1dD2DmVLAMOkdCe1dwUAO9eX5S5_31ikovd0UyoYDiZI/export?format=csv&gid=945195723"
        try:
            df = pd.read_csv(sheet_url)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Failed to load Overall Spends Google Sheet. Please check if the link is accessible to anyone: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=600)
    def load_devender_spends():
        sheet_url = "https://docs.google.com/spreadsheets/d/1KJ--JKXJqtP_yTiW-Ok0PpIADv9AXyagspFfZBiYChY/export?format=csv&gid=1016805741"
        try:
            df = pd.read_csv(sheet_url)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Failed to load Devender Spends Sheet. Please check permissions: {e}")
            return pd.DataFrame()

    @st.cache_data(ttl=600)
    def load_enrolled_data():
        sheet_url = "https://docs.google.com/spreadsheets/d/1hMcaFk4l9xmOUK6lB0LgpWMbHZkLDrMzzQUi8oBX6J8/export?format=csv&gid=0"
        try:
            df = pd.read_csv(sheet_url)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Failed to load Enrolled Data Sheet. Please check permissions: {e}")
            return pd.DataFrame()

    # Call functions with current user to maintain strict DB rules
    raw_data = load_data_from_mysql(current_username)
    gs_data = load_google_sheet()
    devender_data = load_devender_spends()
    enrolled_data = load_enrolled_data()

    # --- TABS (NOW WITH 5 TABS INCLUDING ROAS) ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Search & RAW Data", "📈 University Analytics Report", "📈 Campaign Analytics Report", "📊 Daily Lead Received", "💰 ROAS Dashboard"])

    if not raw_data.empty:
        # Master list of universities
        all_universities = sorted(raw_data['Hyperlap_University_Name'].dropna().unique())
        
        # Apply Source Filter (Facebook, Google, LinkedIn)
        if source_filter != "All":
            filtered_data = raw_data[raw_data['Lead_Type'] == source_filter].copy()
        else:
            filtered_data = raw_data.copy()

        # Apply Additional Owner Filter (For Admins/Others)
        if owner_filter == "Vipin & Pramod":
            filtered_data = filtered_data[filtered_data['Source_TAG'].isin(['META INHOUSE', 'GOOGLE INHOUSE', 'LINKEDIN INHOUSE'])]
        elif owner_filter == "Devender":
            filtered_data = filtered_data[filtered_data['Source_TAG'].isin(['META-DEVENDER', 'GOOGLE-DEVENDER'])]

        # SAFE PANDAS NATIVE DATETIME CONVERSION
        date_cols = ['CreatedOn_Date', 'Connected_Thirty_sec', 'Counselled_DT', 'Offer_DT', 'Converted_DT']
        for col in date_cols:
            filtered_data[col] = pd.to_datetime(filtered_data[col], errors='coerce')

        # Convert Streamlit inputs to Pandas Timestamps for safe comparison
        start_ts = pd.to_datetime(start_date)
        end_ts = pd.to_datetime(end_date)

    # --- TAB 1 ---
    with tab1:
        if not raw_data.empty:
            search_query = st.text_input("Search any keyword...")
            if search_query:
                mask = filtered_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
                search_df = filtered_data[mask]
                
                # Format dates back to string for clean display
                display_df = search_df.copy()
                for col in date_cols:
                    display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
                # Dynamic Height logic
                st.dataframe(display_df, use_container_width=True, height=min(750, (len(display_df) + 1) * 36 + 10))
            else:
                display_df = filtered_data.copy()
                for col in date_cols:
                    display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
                st.dataframe(display_df, use_container_width=True, height=min(750, (len(display_df) + 1) * 36 + 10))
                
            st.caption(f"Total Rows Fetched: {len(filtered_data)}")
        else:
            st.warning("Data failed to load. Please check your SQL Query or Database connection.")

    # --- TAB 2: UNIVERSITY ANALYTICS ---
    with tab2:
        if not raw_data.empty:
            if start_date <= end_date:
                
                created_mask = (filtered_data['CreatedOn_Date'] >= start_ts) & (filtered_data['CreatedOn_Date'] <= end_ts)
                df_created = filtered_data[created_mask]

                # --- ENROLLED DATA LOGIC FOR TAB 2 (Respecting Filters) ---
                enrolled_filtered_tab2 = pd.DataFrame()
                if not enrolled_data.empty:
                    enr_data_safe = enrolled_data.copy()
                    
                    date_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'CONVERTED DATE'), None)
                    uni_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'ENROLLED UNIVERSITY'), None)
                    acc_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'TOTAL ACCRUED AMOUNT'), None)
                    tag_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'CONVERTED SOURCE TAG'), None)
                    
                    if date_col and uni_col and acc_col and tag_col:
                        enr_data_safe[date_col] = pd.to_datetime(enr_data_safe[date_col], errors='coerce').dt.date
                        enr_data_safe[acc_col] = pd.to_numeric(enr_data_safe[acc_col], errors='coerce').fillna(0)
                        
                        # Apply currently active Source and Owner filters
                        valid_tags = filtered_data['Source_TAG'].dropna().unique()
                        valid_tags_clean = [str(t).replace(' ', '').replace('-', '').upper() for t in valid_tags]
                        if 'METADEVENDER' in valid_tags_clean: valid_tags_clean.append('METADEVENDAR')
                        if 'GOOGLEDEVENDER' in valid_tags_clean: valid_tags_clean.append('GOOGLEDEVENDAR')
                            
                        enr_tags_clean = enr_data_safe[tag_col].astype(str).str.replace(' ', '', regex=False).str.replace('-', '', regex=False).str.upper()
                        
                        enrolled_filtered_tab2 = enr_data_safe[
                            (enr_data_safe[date_col] >= start_date) & 
                            (enr_data_safe[date_col] <= end_date) &
                            (enr_tags_clean.isin(valid_tags_clean))
                        ]
                # ------------------------------------------------------------

                report_data = []

                for uni in all_universities:
                    df_uni_sm = df_created[df_created['Hyperlap_University_Name'] == uni]
                    df_uni_overall = filtered_data[filtered_data['Hyperlap_University_Name'] == uni]
                    
                    lead_received = len(df_uni_sm)
                    
                    # --- CALCULATE BOOKED AMOUNT ---
                    booked_amount = 0
                    if not enrolled_filtered_tab2.empty:
                        clean_enrolled_unis = enrolled_filtered_tab2[uni_col].astype(str).str.replace('_', ' ').str.strip().str.upper().str.replace(' ', '', regex=False)
                        clean_uni = str(uni).replace('_', ' ').strip().upper().replace(' ', '')
                        mask = clean_enrolled_unis == clean_uni
                        booked_amount = enrolled_filtered_tab2[mask][acc_col].sum()
                    # -------------------------------
                    
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

                    offer_to_couns_pct_sm = offer_sm / couns_sm if couns_sm > 0 else 0
                    conv_to_offer_pct_sm = conv_sm / offer_sm if offer_sm > 0 else 0
                    conv_to_couns_pct_sm = conv_sm / couns_sm if couns_sm > 0 else 0
                    conv_to_lead_pct_sm = conv_sm / lead_received if lead_received > 0 else 0

                    report_data.append({
                        "Hyperlap Universities": uni,
                        "Lead Received": lead_received,
                        "Facebook": facebook_count,
                        "Google": google_count,
                        "LinkedIn": linkedin_count,
                        "Junk SM": junk_sm,
                        "Junk SM %": junk_pct,
                        "Junk Overall": junk_overall,
                        "Connected 30 Sec SM": conn_30_sm,
                        "Connected 30 Sec SM %": conn_30_sm_pct,
                        "Connected 30 Sec Overall": conn_30_overall,
                        "Counselled SM": couns_sm,
                        "Counselled SM %": couns_sm_pct,
                        "Counselled Overall": couns_overall,
                        "Offer SM": offer_sm,
                        "Offer Overall": offer_overall,
                        "Converted SM": conv_sm,
                        "Converted Overall": conv_overall,
                        "Booked Amount": booked_amount,  # <--- MOVED HERE
                        "Offer To Counselled % SM": offer_to_couns_pct_sm,
                        "Offer To Converted % SM": conv_to_offer_pct_sm,
                        "Counselled To Converted % SM": conv_to_couns_pct_sm,
                        "Lead To Converted % SM": conv_to_lead_pct_sm
                    })

                report_df = pd.DataFrame(report_data)
                
                # --- GRAND TOTAL ROW LOGIC ---
                total_row = {'Hyperlap Universities': 'Grand Total'}
                sum_columns = ['Lead Received', 'Facebook', 'Google', 'LinkedIn', 'Junk SM', 'Junk Overall',
                                'Connected 30 Sec SM', 'Connected 30 Sec Overall', 'Counselled SM', 'Counselled Overall',
                                'Offer SM', 'Offer Overall', 'Converted SM', 'Converted Overall', 'Booked Amount']
                
                for col in sum_columns:
                    total_row[col] = report_df[col].sum()
                    
                total_row['Junk SM %'] = total_row['Junk SM'] / total_row['Lead Received'] if total_row['Lead Received'] > 0 else 0
                total_row['Connected 30 Sec SM %'] = total_row['Connected 30 Sec SM'] / total_row['Lead Received'] if total_row['Lead Received'] > 0 else 0
                total_row['Counselled SM %'] = total_row['Counselled SM'] / total_row['Connected 30 Sec SM'] if total_row['Connected 30 Sec SM'] > 0 else 0
                total_row['Offer To Counselled % SM'] = total_row['Offer SM'] / total_row['Counselled SM'] if total_row['Counselled SM'] > 0 else 0
                total_row['Offer To Converted % SM'] = total_row['Converted SM'] / total_row['Offer SM'] if total_row['Offer SM'] > 0 else 0
                total_row['Counselled To Converted % SM'] = total_row['Converted SM'] / total_row['Counselled SM'] if total_row['Counselled SM'] > 0 else 0
                total_row['Lead To Converted % SM'] = total_row['Converted SM'] / total_row['Lead Received'] if total_row['Lead Received'] > 0 else 0

                report_df = pd.concat([pd.DataFrame([total_row]), report_df], ignore_index=True)
                
                styled_report = report_df.style.format({
                    "Booked Amount": "{:.2f}",
                    "Junk SM %": "{:.2%}",
                    "Connected 30 Sec SM %": "{:.2%}",
                    "Counselled SM %": "{:.2%}",
                    "Offer To Counselled % SM": "{:.2%}",
                    "Offer To Converted % SM": "{:.2%}",
                    "Counselled To Converted % SM": "{:.2%}",
                    "Lead To Converted % SM": "{:.2%}"
                })
                
                # Dynamic Height logic
                st.dataframe(styled_report, use_container_width=True, height=min(750, (len(report_df) + 1) * 36 + 10))
            else:
                st.error("❌ End Date cannot be earlier than the Start Date!")

    # --- TAB 3: CAMPAIGN ANALYTICS (WITH GOOGLE SHEET INTEGRATION) ---
    with tab3:
        if not raw_data.empty:
            if start_date <= end_date:
                
                created_mask = (filtered_data['CreatedOn_Date'] >= start_ts) & (filtered_data['CreatedOn_Date'] <= end_ts)
                df_created = filtered_data[created_mask]

                # Google Sheet filtering logic (Safe check for columns)
                if not gs_data.empty and all(col in gs_data.columns for col in ['Day', 'Cost', 'Campaign', 'Source']):
                    gs_data_safe = gs_data.copy()
                    gs_data_safe['Day'] = pd.to_datetime(gs_data_safe['Day'], errors='coerce').dt.date
                    gs_data_safe['Cost'] = pd.to_numeric(gs_data_safe['Cost'], errors='coerce').fillna(0)
                    
                    gs_mask = (gs_data_safe['Day'] >= start_date) & (gs_data_safe['Day'] <= end_date)
                    gs_filtered = gs_data_safe[gs_mask].copy()
                    
                    # --- NEW LOGIC: Map Dashboard Source to Google Sheet Source ---
                    if source_filter != "All":
                        if source_filter == "GOOGLE":
                            gs_filtered = gs_filtered[gs_filtered['Source'].astype(str).str.strip().str.upper() == 'GOOGLE INHOUSE']
                        elif source_filter == "FACEBOOK":
                            gs_filtered = gs_filtered[gs_filtered['Source'].astype(str).str.strip().str.upper() == 'META INHOUSE']
                        elif source_filter == "LINKEDIN":
                            gs_filtered = gs_filtered[gs_filtered['Source'].astype(str).str.strip().str.upper().str.contains('LINKEDIN', na=False)]
                    
                    # Extract unique campaigns directly from the dynamically filtered Google Sheet
                    all_campaigns_gs = sorted(gs_filtered['Campaign'].dropna().unique())
                else:
                    gs_filtered = pd.DataFrame()
                    all_campaigns_gs = []

                report_data_camp = []

                for camp in all_campaigns_gs:
                    # Spend Calculation from appropriately filtered Google Sheet
                    camp_spend = gs_filtered[gs_filtered['Campaign'] == camp]['Cost'].sum()
                    
                    # Lead metrics from MySQL Dashboard Data
                    df_camp_sm = df_created[df_created['Source_Campaign'] == camp]
                    df_camp_overall = filtered_data[filtered_data['Source_Campaign'] == camp]
                    
                    lead_received = len(df_camp_sm)
                    
                    facebook_count = len(df_camp_sm[df_camp_sm['Lead_Type'] == 'FACEBOOK'])
                    google_count = len(df_camp_sm[df_camp_sm['Lead_Type'] == 'GOOGLE'])
                    linkedin_count = len(df_camp_sm[df_camp_sm['Lead_Type'] == 'LINKEDIN'])
                    
                    junk_sm_mask = df_camp_sm['ProspectStage'].astype(str).str.lower().str.contains('l1_lost|l2_lost|l1 lost|l2 lost', regex=True, na=False)
                    junk_sm = len(df_camp_sm[junk_sm_mask])
                    junk_pct = junk_sm / lead_received if lead_received > 0 else 0
                    
                    junk_overall_mask = df_camp_overall['ProspectStage'].astype(str).str.lower().str.contains('l1_lost|l2_lost|l1 lost|l2 lost', regex=True, na=False)
                    junk_overall = len(df_camp_overall[junk_overall_mask])
                    
                    conn_30_sm_mask = (df_camp_sm['Connected_Thirty_sec'] >= start_ts) & (df_camp_sm['Connected_Thirty_sec'] <= end_ts)
                    conn_30_sm = len(df_camp_sm[conn_30_sm_mask])
                    conn_30_sm_pct = conn_30_sm / lead_received if lead_received > 0 else 0
                    
                    conn_overall_mask = (df_camp_overall['Connected_Thirty_sec'] >= start_ts) & (df_camp_overall['Connected_Thirty_sec'] <= end_ts)
                    conn_30_overall = len(df_camp_overall[conn_overall_mask])

                    couns_sm_mask = (df_camp_sm['Counselled_DT'] >= start_ts) & (df_camp_sm['Counselled_DT'] <= end_ts)
                    couns_sm = len(df_camp_sm[couns_sm_mask])
                    couns_sm_pct = couns_sm / conn_30_sm if conn_30_sm > 0 else 0

                    couns_overall_mask = (df_camp_overall['Counselled_DT'] >= start_ts) & (df_camp_overall['Counselled_DT'] <= end_ts)
                    couns_overall = len(df_camp_overall[couns_overall_mask])

                    offer_sm_mask = (df_camp_sm['Offer_DT'] >= start_ts) & (df_camp_sm['Offer_DT'] <= end_ts)
                    offer_sm = len(df_camp_sm[offer_sm_mask])

                    offer_overall_mask = (df_camp_overall['Offer_DT'] >= start_ts) & (df_camp_overall['Offer_DT'] <= end_ts)
                    offer_overall = len(df_camp_overall[offer_overall_mask])

                    conv_sm_mask = (df_camp_sm['Converted_DT'] >= start_ts) & (df_camp_sm['Converted_DT'] <= end_ts)
                    conv_sm = len(df_camp_sm[conv_sm_mask])

                    conv_overall_mask = (df_camp_overall['Converted_DT'] >= start_ts) & (df_camp_overall['Converted_DT'] <= end_ts)
                    conv_overall = len(df_camp_overall[conv_overall_mask])

                    offer_to_couns_pct_sm = offer_sm / couns_sm if couns_sm > 0 else 0
                    conv_to_offer_pct_sm = conv_sm / offer_sm if offer_sm > 0 else 0
                    conv_to_couns_pct_sm = conv_sm / couns_sm if couns_sm > 0 else 0
                    conv_to_lead_pct_sm = conv_sm / lead_received if lead_received > 0 else 0

                    report_data_camp.append({
                        "Source Campaign": camp,
                        "Spend": camp_spend,
                        "Lead Received": lead_received,
                        "Facebook": facebook_count,
                        "Google": google_count,
                        "LinkedIn": linkedin_count,
                        "Junk SM": junk_sm,
                        "Junk SM %": junk_pct,
                        "Junk Overall": junk_overall,
                        "Connected 30 Sec SM": conn_30_sm,
                        "Connected 30 Sec SM %": conn_30_sm_pct,
                        "Connected 30 Sec Overall": conn_30_overall,
                        "Counselled SM": couns_sm,
                        "Counselled SM %": couns_sm_pct,
                        "Counselled Overall": couns_overall,
                        "Offer SM": offer_sm,
                        "Offer Overall": offer_overall,
                        "Converted SM": conv_sm,
                        "Converted Overall": conv_overall,
                        "Offer To Counselled % SM": offer_to_couns_pct_sm,
                        "Offer To Converted % SM": conv_to_offer_pct_sm,
                        "Counselled To Converted % SM": conv_to_couns_pct_sm,
                        "Lead To Converted % SM": conv_to_lead_pct_sm
                    })

                if report_data_camp:
                    report_df_camp = pd.DataFrame(report_data_camp)
                    
                    # --- GRAND TOTAL ROW LOGIC FOR CAMPAIGN ---
                    total_row_camp = {'Source Campaign': 'Grand Total'}
                    sum_columns_camp = ['Spend', 'Lead Received', 'Facebook', 'Google', 'LinkedIn', 'Junk SM', 'Junk Overall',
                                    'Connected 30 Sec SM', 'Connected 30 Sec Overall', 'Counselled SM', 'Counselled Overall',
                                    'Offer SM', 'Offer Overall', 'Converted SM', 'Converted Overall']
                    
                    for col in sum_columns_camp:
                        total_row_camp[col] = report_df_camp[col].sum()
                        
                    total_row_camp['Junk SM %'] = total_row_camp['Junk SM'] / total_row_camp['Lead Received'] if total_row_camp['Lead Received'] > 0 else 0
                    total_row_camp['Connected 30 Sec SM %'] = total_row_camp['Connected 30 Sec SM'] / total_row_camp['Lead Received'] if total_row_camp['Lead Received'] > 0 else 0
                    total_row_camp['Counselled SM %'] = total_row_camp['Counselled SM'] / total_row_camp['Connected 30 Sec SM'] if total_row_camp['Connected 30 Sec SM'] > 0 else 0
                    total_row_camp['Offer To Counselled % SM'] = total_row_camp['Offer SM'] / total_row_camp['Counselled SM'] if total_row_camp['Counselled SM'] > 0 else 0
                    total_row_camp['Offer To Converted % SM'] = total_row_camp['Converted SM'] / total_row_camp['Offer SM'] if total_row_camp['Offer SM'] > 0 else 0
                    total_row_camp['Counselled To Converted % SM'] = total_row_camp['Converted SM'] / total_row_camp['Counselled SM'] if total_row_camp['Counselled SM'] > 0 else 0
                    total_row_camp['Lead To Converted % SM'] = total_row_camp['Converted SM'] / total_row_camp['Lead Received'] if total_row_camp['Lead Received'] > 0 else 0

                    report_df_camp = pd.concat([pd.DataFrame([total_row_camp]), report_df_camp], ignore_index=True)
                    
                    styled_report_camp = report_df_camp.style.format({
                        "Spend": "{:.2f}",
                        "Junk SM %": "{:.2%}",
                        "Connected 30 Sec SM %": "{:.2%}",
                        "Counselled SM %": "{:.2%}",
                        "Offer To Counselled % SM": "{:.2%}",
                        "Offer To Converted % SM": "{:.2%}",
                        "Counselled To Converted % SM": "{:.2%}",
                        "Lead To Converted % SM": "{:.2%}"
                    })
                    
                    # Dynamic Height logic
                    st.dataframe(styled_report_camp, use_container_width=True, height=min(750, (len(report_df_camp) + 1) * 36 + 10))
                else:
                    st.info("No Campaign Data found for the selected date range. Please verify the Google Sheet.")

    # --- TAB 4: DAILY LEAD RECEIVED (PRESENT DAY ONLY) ---
    with tab4:
        if not raw_data.empty:
            # Explicitly force this tab to strictly use 'Today's date only.
            today_ts = pd.to_datetime(datetime.date.today())
            st.subheader(f"📅 Daily Leads Received (Today: {today_ts.strftime('%d %b %Y')})")
            
            # Filter strictly for today
            df_today = filtered_data[filtered_data['CreatedOn_Date'] == today_ts]
            
            # Master list of requested universities with their display names and search keywords
            uni_mapping = {
                "ALLIANCE UNIVERSITY": "alliance",
                "AMITY UNIVERSITY": "amity",
                "BHARATI VIDYAPEETH UNIVERSITY": "bharati",
                "DR. D Y PATIL UNIVERSITY": "patil",
                "GALGOTIAS UNIVERSITY": "galgotias",
                "GENERIC UNIVERSITY": "generic",
                "GLA UNIVERSITY": "gla",
                "LOVELY PROFESSIONAL UNIVERSITY": "lovely",
                "MANIPAL UNIVERSITY": "manipal",
                "NMIMS": "nmims",
                "SHOOLINI UNIVERSITY": "shoolini",
                "UTTARANCHAL UNIVERSITY": "uttaranchal"
            }
            
            daily_report_data = []
            
            for display_name, search_key in uni_mapping.items():
                # Case-insensitive search for university
                mask = df_today['Hyperlap_University_Name'].astype(str).str.contains(search_key, case=False, na=False)
                df_uni_today = df_today[mask]
                
                # Fetch counts per requested source tags
                google_dev = len(df_uni_today[df_uni_today['Source_TAG'] == 'GOOGLE-DEVENDER'])
                meta_dev = len(df_uni_today[df_uni_today['Source_TAG'] == 'META-DEVENDER'])
                google_inhouse = len(df_uni_today[df_uni_today['Source_TAG'] == 'GOOGLE INHOUSE'])
                meta_inhouse = len(df_uni_today[df_uni_today['Source_TAG'] == 'META INHOUSE'])
                linkedin_inhouse = len(df_uni_today[df_uni_today['Source_TAG'] == 'LINKEDIN INHOUSE'])
                
                total_leads = google_dev + meta_dev + google_inhouse + meta_inhouse + linkedin_inhouse
                
                daily_report_data.append({
                    "HYPERLAP_UNIVERSITY_NAME": display_name,
                    "GOOGLE-DEVENDER": google_dev,
                    "META-DEVENDER": meta_dev, 
                    "GOOGLE INHOUSE": google_inhouse,
                    "META INHOUSE": meta_inhouse,
                    "LINKEDIN INHOUSE": linkedin_inhouse,
                    "TOTAL LEADS": total_leads
                })
                
            df_daily = pd.DataFrame(daily_report_data)
            
            # Add Grand Total Row (Bottom White Arrow Location)
            total_row_daily = {"HYPERLAP_UNIVERSITY_NAME": "GRAND TOTAL"}
            sum_cols_daily = ["GOOGLE-DEVENDER", "META-DEVENDER", "GOOGLE INHOUSE", "META INHOUSE", "LINKEDIN INHOUSE", "TOTAL LEADS"]
            
            for col in sum_cols_daily:
                total_row_daily[col] = df_daily[col].sum()
                
            df_daily = pd.concat([df_daily, pd.DataFrame([total_row_daily])], ignore_index=True)
            
            # Dynamic Height logic
            st.dataframe(df_daily, use_container_width=True, height=min(750, (len(df_daily) + 1) * 36 + 10))

    # --- TAB 5: ROAS DASHBOARD ---
    with tab5:
        if not raw_data.empty:
            if start_date <= end_date:
                # 1. Filter Main MySQL Data
                created_mask = (filtered_data['CreatedOn_Date'] >= start_ts) & (filtered_data['CreatedOn_Date'] <= end_ts)
                df_created = filtered_data[created_mask]
                
                # Fetch dynamically valid universities from filtered dataset
                valid_unis = filtered_data['Hyperlap_University_Name'].dropna().unique()
                
                # Clean valid universities list (remove underscores, spaces, make uppercase for perfect matching)
                valid_unis_clean = [str(u).replace('_', ' ').strip().upper() for u in valid_unis]

                # 2. Setup Google Sheet 1 (Inhouse Spends) safely with Column Checks
                gs_inhouse_filtered = pd.DataFrame()
                if not gs_data.empty and 'Day' in gs_data.columns:
                    gs_data_safe = gs_data.copy()
                    gs_data_safe['Day'] = pd.to_datetime(gs_data_safe['Day'], errors='coerce').dt.date
                    if 'Cost' in gs_data_safe.columns:
                        gs_data_safe['Cost'] = pd.to_numeric(gs_data_safe['Cost'], errors='coerce').fillna(0)
                    gs_inhouse_filtered = gs_data_safe[(gs_data_safe['Day'] >= start_date) & (gs_data_safe['Day'] <= end_date)]

                # 3. Setup Google Sheet 2 (Devender Spends) safely with Column Checks
                gs_dev_filtered = pd.DataFrame()
                if not devender_data.empty and 'Date' in devender_data.columns:
                    dev_data_safe = devender_data.copy()
                    dev_data_safe['Date'] = pd.to_datetime(dev_data_safe['Date'], errors='coerce').dt.date
                    if 'Google Spend' in dev_data_safe.columns:
                        dev_data_safe['Google Spend'] = pd.to_numeric(dev_data_safe['Google Spend'], errors='coerce').fillna(0)
                    if 'Facebook Spend' in dev_data_safe.columns:
                        dev_data_safe['Facebook Spend'] = pd.to_numeric(dev_data_safe['Facebook Spend'], errors='coerce').fillna(0)
                    gs_dev_filtered = dev_data_safe[(dev_data_safe['Date'] >= start_date) & (dev_data_safe['Date'] <= end_date)]

                # 4. Setup Google Sheet 3 (Enrolled Data) safely with Column Checks and Robust University Matching
                enrolled_filtered = pd.DataFrame()
                if not enrolled_data.empty:
                    enr_data_safe = enrolled_data.copy()
                    
                    # Ensure flexible extraction for "Converted Date"
                    date_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'CONVERTED DATE'), None)
                    if date_col:
                        enr_data_safe[date_col] = pd.to_datetime(enr_data_safe[date_col], errors='coerce').dt.date
                        
                        uni_col = next((c for c in enr_data_safe.columns if str(c).strip().upper() == 'ENROLLED UNIVERSITY'), None)
                        
                        if uni_col:
                            enr_unis_clean = enr_data_safe[uni_col].astype(str).str.replace('_', ' ').str.strip().str.upper()
                            enrolled_filtered = enr_data_safe[
                                (enr_data_safe[date_col] >= start_date) & 
                                (enr_data_safe[date_col] <= end_date) & 
                                (enr_unis_clean.isin(valid_unis_clean))
                            ]
                        else:
                            enrolled_filtered = enr_data_safe[(enr_data_safe[date_col] >= start_date) & (enr_data_safe[date_col] <= end_date)]

                # Get unique Source TAGs to iterate through
                unique_tags = sorted(filtered_data['Source_TAG'].dropna().unique())
                
                roas_data = []

                for tag in unique_tags:
                    # Calculate Individual Spends based on TAG safely
                    spend = 0
                    if tag == 'META INHOUSE' and not gs_inhouse_filtered.empty and 'Source' in gs_inhouse_filtered.columns and 'Cost' in gs_inhouse_filtered.columns:
                        spend = gs_inhouse_filtered[gs_inhouse_filtered['Source'].astype(str).str.strip().str.upper() == 'META INHOUSE']['Cost'].sum()
                    elif tag == 'GOOGLE INHOUSE' and not gs_inhouse_filtered.empty and 'Source' in gs_inhouse_filtered.columns and 'Cost' in gs_inhouse_filtered.columns:
                        spend = gs_inhouse_filtered[gs_inhouse_filtered['Source'].astype(str).str.strip().str.upper() == 'GOOGLE INHOUSE']['Cost'].sum()
                    elif tag == 'LINKEDIN INHOUSE' and not gs_inhouse_filtered.empty and 'Source' in gs_inhouse_filtered.columns and 'Cost' in gs_inhouse_filtered.columns:
                        spend = gs_inhouse_filtered[gs_inhouse_filtered['Source'].astype(str).str.strip().str.upper().str.contains('LINKEDIN', na=False)]['Cost'].sum()
                    elif tag == 'META-DEVENDER' and not gs_dev_filtered.empty and 'Facebook Spend' in gs_dev_filtered.columns:
                        spend = gs_dev_filtered['Facebook Spend'].sum()
                    elif tag == 'GOOGLE-DEVENDER' and not gs_dev_filtered.empty and 'Google Spend' in gs_dev_filtered.columns:
                        spend = gs_dev_filtered['Google Spend'].sum()

                    # Calculate MySQL Lead Metrics
                    df_tag_sm = df_created[df_created['Source_TAG'] == tag]
                    df_tag_overall = filtered_data[filtered_data['Source_TAG'] == tag]
                    
                    lead_received = len(df_tag_sm)
                    
                    conv_sm_mask = (df_tag_sm['Converted_DT'] >= start_ts) & (df_tag_sm['Converted_DT'] <= end_ts)
                    conv_sm = len(df_tag_sm[conv_sm_mask])
                    
                    conv_overall_mask = (df_tag_overall['Converted_DT'] >= start_ts) & (df_tag_overall['Converted_DT'] <= end_ts)
                    conv_overall = len(df_tag_overall[conv_overall_mask])

                    # Calculate Booked Amount from Enrolled Data Sheet safely (Fixing Spelling Mismatches)
                    booked_amount = 0
                    if not enrolled_filtered.empty:
                        # Find exactly matched column names ignoring spaces or case sensitivity
                        conv_col = next((c for c in enrolled_filtered.columns if str(c).strip().upper() == 'CONVERTED SOURCE TAG'), None)
                        acc_col = next((c for c in enrolled_filtered.columns if str(c).strip().upper() == 'TOTAL ACCRUED AMOUNT'), None)
                        
                        if conv_col and acc_col:
                            enrolled_tags = enrolled_filtered[conv_col].astype(str).str.strip().str.upper()
                            
                            # Extreme robust matching ignoring spaces, hyphens and A/E typos
                            clean_enrolled = enrolled_tags.str.replace(' ', '', regex=False).str.replace('-', '', regex=False)
                            clean_tag = tag.upper().replace(' ', '').replace('-', '')
                            
                            if clean_tag in ['METADEVENDER', 'METADEVENDAR']:
                                mask = clean_enrolled.isin(['METADEVENDER', 'METADEVENDAR'])
                            elif clean_tag in ['GOOGLEDEVENDER', 'GOOGLEDEVENDAR']:
                                mask = clean_enrolled.isin(['GOOGLEDEVENDER', 'GOOGLEDEVENDAR'])
                            else:
                                mask = clean_enrolled == clean_tag
                                
                            booked_amount = pd.to_numeric(enrolled_filtered[mask][acc_col], errors='coerce').fillna(0).sum()

                    # Derived ROAS Formulas
                    booked_roas = booked_amount / spend if spend > 0 else 0
                    cpl = spend / lead_received if lead_received > 0 else 0
                    ltc_pct = conv_overall / lead_received if lead_received > 0 else 0
                    cac = spend / conv_overall if conv_overall > 0 else 0

                    roas_data.append({
                        "Source Tag": tag,
                        "Spends": spend,
                        "Booked Amount": booked_amount,
                        "Booked ROAS": booked_roas,
                        "Lead Received": lead_received,
                        "CPL": cpl,
                        "Converted SM": conv_sm,
                        "Converted Overall": conv_overall,
                        "Lead To Converted Overall %": ltc_pct,
                        "CAC": cac
                    })

                if roas_data:
                    roas_df = pd.DataFrame(roas_data)
                    
                    # Grand Total Row for ROAS
                    total_row = {"Source Tag": "GRAND TOTAL"}
                    sum_cols = ["Spends", "Booked Amount", "Lead Received", "Converted SM", "Converted Overall"]
                    for col in sum_cols:
                        total_row[col] = roas_df[col].sum()
                        
                    # Re-calculate ratios for Grand Total
                    total_row["Booked ROAS"] = total_row["Booked Amount"] / total_row["Spends"] if total_row["Spends"] > 0 else 0
                    total_row["CPL"] = total_row["Spends"] / total_row["Lead Received"] if total_row["Lead Received"] > 0 else 0
                    total_row["Lead To Converted Overall %"] = total_row["Converted Overall"] / total_row["Lead Received"] if total_row["Lead Received"] > 0 else 0
                    total_row["CAC"] = total_row["Spends"] / total_row["Converted Overall"] if total_row["Converted Overall"] > 0 else 0
                    
                    roas_df = pd.concat([roas_df, pd.DataFrame([total_row])], ignore_index=True)
                    
                    # Number Formatting
                    styled_roas = roas_df.style.format({
                        "Spends": "{:.2f}",
                        "Booked Amount": "{:.2f}",
                        "Booked ROAS": "{:.2f}",
                        "CPL": "{:.2f}",
                        "Lead To Converted Overall %": "{:.2%}",
                        "CAC": "{:.2f}"
                    })
                    
                    # Dynamic Height logic
                    st.dataframe(styled_roas, use_container_width=True, height=min(750, (len(roas_df) + 1) * 36 + 10))
                else:
                    st.info("No data available for ROAS Dashboard in the selected date range.")
            else:
                st.error("❌ End Date cannot be earlier than the Start Date!")
