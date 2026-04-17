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
                /* Hides the Streamlit top right menu (Manage App, GitHub, etc.) */
                header[data-testid="stHeader"] {
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
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()

    st.title("🎓 Degree Leads Analysis")

    # --- DATABASE CONNECTION ---
    @st.cache_data(ttl=600) 
    def load_data_from_mysql():
        try:
            conn = mysql.connector.connect(
                host=st.secrets["mysql"]["host"],
                port=st.secrets["mysql"]["port"],
                database=st.secrets["mysql"]["database"],
                user=st.secrets["mysql"]["username"],
                password=st.secrets["mysql"]["password"]
            )
            
            query = """
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
        WHEN cc.lead_source_c LIKE '%Meta-Devendar%' THEN 'META-DEVENDAR'
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
    Where T1.Source_TAG IN ('META INHOUSE', 'GOOGLE INHOUSE', 'LINKEDIN INHOUSE')
    AND T1.Lead_Type IN ('FACEBOOK', 'GOOGLE', 'LINKEDIN')
    ORDER BY T1.CreatedOn_Date
            """
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Database connect error: {e}")
            return pd.DataFrame()

    raw_data = load_data_from_mysql()

    tab1, tab2 = st.tabs(["🔍 Search & RAW Data", "📈 University Analytics Report"])

    if not raw_data.empty:
        # Master list of universities
        all_universities = sorted(raw_data['Hyperlap_University_Name'].dropna().unique())
        
        # Apply Source Filter
        if source_filter != "All":
            filtered_data = raw_data[raw_data['Lead_Type'] == source_filter].copy()
        else:
            filtered_data = raw_data.copy()

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
                st.dataframe(display_df, use_container_width=True)
            else:
                display_df = filtered_data.copy()
                for col in date_cols:
                    display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
                st.dataframe(display_df, use_container_width=True)
                
            st.caption(f"Total Rows Fetched: {len(filtered_data)}")
        else:
            st.warning("Data load nahi hua. Kripya apni SQL Query check karein.")

    # --- TAB 2 ---
    with tab2:
        if not raw_data.empty:
            if start_date <= end_date:
                
                # Safely mask data using Pandas native datetime checks
                created_mask = (filtered_data['CreatedOn_Date'] >= start_ts) & (filtered_data['CreatedOn_Date'] <= end_ts)
                df_created = filtered_data[created_mask]

                report_data = []

                for uni in all_universities:
                    df_uni_sm = df_created[df_created['Hyperlap_University_Name'] == uni]
                    df_uni_overall = filtered_data[filtered_data['Hyperlap_University_Name'] == uni]
                    
                    lead_received = len(df_uni_sm)
                    
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
                                'Offer SM', 'Offer Overall', 'Converted SM', 'Converted Overall']
                
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
                    "Junk SM %": "{:.2%}",
                    "Connected 30 Sec SM %": "{:.2%}",
                    "Counselled SM %": "{:.2%}",
                    "Offer To Counselled % SM": "{:.2%}",
                    "Offer To Converted % SM": "{:.2%}",
                    "Counselled To Converted % SM": "{:.2%}",
                    "Lead To Converted % SM": "{:.2%}"
                })
                
                st.dataframe(styled_report, use_container_width=True)
            else:
                st.error("❌ End Date kabhi bhi Start Date se pehle ki nahi ho sakti!")
