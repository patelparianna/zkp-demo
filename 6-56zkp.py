import streamlit as st
import random
import time
import pandas as pd

# --- CRYPTO CONFIG ---
P, G = 1019, 2

st.set_page_config(page_title="Clover ZKP: Secure Ledger Demo", layout="wide")

# Persistent Storage
if "bank_ledger" not in st.session_state:
    st.session_state.bank_ledger = {} 
if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = []
if "hacker_sniffer" not in st.session_state:
    st.session_state.hacker_sniffer = []
if "step" not in st.session_state:
    st.session_state.step = "register"

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.header("⚙️ Admin Tools")
    if st.button("🗑️ Clear All History"):
        st.session_state.transaction_history = []
        st.session_state.hacker_sniffer = []
        st.rerun()

# --- PHASE 1: REGISTRATION ---
if st.session_state.step == "register":
    st.title("🛡️ Step 1: Secure Registration")
    st.info("The bank only stores a 'Public Fingerprint'. The password stays on the device.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📱 User Device")
        name = st.text_input("Name", placeholder="Alice")
        pwd = st.number_input("Create Secret Password", min_value=1, value=123)
        reg_btn = st.button("Register Account")

    with c2:
        st.subheader("🏦 Bank Server")
        if reg_btn and name:
            pub_id = pow(G, pwd, P)
            st.session_state.bank_ledger[name] = pub_id
            st.success(f"ACCOUNT CREATED\n\nUser: {name}\nPublic ID: {pub_id}")
            time.sleep(1.5)
            st.session_state.step = "transaction"
            st.rerun()

# --- PHASE 2: TRANSACTION & INTERCEPTION ---
elif st.session_state.step == "transaction":
    st.title("💳 Step 2: Live Handshake & Interception")
    
    u_col, h_col, b_col = st.columns([1, 1.2, 1])
    
    with u_col:
        st.subheader("📱 User Phone")
        if not st.session_state.bank_ledger:
            st.warning("No users registered.")
        else:
            user = st.selectbox("Account", list(st.session_state.bank_ledger.keys()))
            amount = st.number_input("Transaction Amount ($)", min_value=0.01, value=10.00, step=0.01)
            input_pwd = st.text_input("Enter Password", type="password")
            pay_btn = st.button("Authorize Payment")

    with h_col:
        st.subheader("🕵️ Hacker Sniffer")
        sniff_box = st.empty()
        sniff_box.code("📡 LISTENING FOR PACKETS...")

    with b_col:
        st.subheader("🏦 Bank Server")
        bank_live = st.empty()
        bank_live.info("📡 Awaiting Network Traffic...")
        term_status = st.empty()

    if pay_btn:
        # ZKP Calculations
        k = random.randint(1, P-1)
        r = pow(G, k, P)
        e = random.randint(1, P-1)
        try: p_int = int(input_pwd)
        except: p_int = 0
        s = (k - p_int * e) % (P - 1)
        
        # --- LIVE EXCHANGE ANIMATION ---
        # Part 1: Commitment
        sniff_box.error(f"⚠️ INTERCEPTED: Commitment (r)\nValue: {r}")
        bank_live.warning(f"📥 INCOMING: Commitment (r)\nValue: {r}")
        time.sleep(0.8)
        
        # Part 2: Challenge
        sniff_box.error(f"⚠️ INTERCEPTED: Challenge (e)\nValue: {e}")
        bank_live.warning(f"📤 OUTGOING: Challenge (e)\nValue: {e}")
        time.sleep(0.8)
        
        # Part 3: Response
        sniff_box.error(f"⚠️ INTERCEPTED: Response (s)\nValue: {s}")
        bank_live.warning(f"📥 INCOMING: Proof (s)\nValue: {s}")
        time.sleep(0.8)
        
        # --- VERIFICATION ---
        bank_live.info("⚙️ VERIFYING MATHEMATICAL PROOF...")
        time.sleep(0.5)
        
        pub_id = st.session_state.bank_ledger[user]
        is_valid = (pow(G, s, P) * pow(pub_id, e, P)) % P == r
        
        # Log Entry
        entry = {
            "Time": time.strftime("%H:%M:%S"),
            "User": user,
            "Amount": f"${amount:,.2f}",
            "Hint (r)": r,
            "Challenge (e)": e,
            "Proof (s)": s,
            "Result": "Approved" if is_valid else "Denied",
            "Attack Success?": "NO (Password hidden)"
        }
        st.session_state.transaction_history.append(entry)
        st.session_state.hacker_sniffer.append(entry)
        
        if is_valid:
            bank_live.success(f"✅ VERIFIED: G^s * y^e = {r}")
            term_status.success(f"PAYMENT APPROVED: ${amount:,.2f}")
        else:
            bank_live.error(f"❌ FAILED: Math Mismatch")
            term_status.error("PAYMENT DENIED: Invalid Proof")

    # --- THE DATA TABLES SECTION ---
    st.divider()
    tab_hack, tab_bank = st.tabs(["🕵️ Hacker's Database (Useless Intercepts)", "📜 Bank Audit Ledger (Verified Proofs)"])
    
    with tab_hack:
        if len(st.session_state.hacker_sniffer) > 0:
            df_hack = pd.DataFrame(st.session_state.hacker_sniffer)
            st.table(df_hack[["User", "Hint (r)", "Challenge (e)", "Proof (s)", "Attack Success?"]])
        else:
            st.info("No network traffic captured.")

    with tab_bank:
        if len(st.session_state.transaction_history) > 0:
            df_bank = pd.DataFrame(st.session_state.transaction_history)
            st.table(df_bank[["Time", "User", "Amount", "Hint (r)", "Challenge (e)", "Proof (s)", "Result"]])
        else:
            st.info("Bank ledger is empty.")

    if st.button("← Add New User"):
        st.session_state.step = "register"
        st.rerun()
