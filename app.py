import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import requests
import json

# ==========================================
# 0. 全域與版面設定
# ==========================================
st.set_page_config(page_title="動態數位投資者輪廓系統", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    header[data-testid="stHeader"] { background: transparent !important; }
    .hero-banner { background: linear-gradient(135deg, #0b1f3a, #164e63) !important; padding: 3rem 2.5rem !important; border-radius: 1.5rem !important; margin-bottom: 2.5rem !important; box-shadow: 0 10px 30px rgba(11, 31, 58, 0.15) !important; }
    .hero-banner h1 { color: #FFFFFF !important; font-size: 2.5rem !important; font-weight: 900 !important; margin: 0 0 1rem 0 !important; line-height: 1.2 !important; }
    .hero-banner p.desc { color: #cbd5e1 !important; font-size: 1rem !important; margin: 0 !important; line-height: 1.6 !important; }
    .hero-banner .tag-badge { background: rgba(45, 212, 191, 0.1) !important; border: 1px solid rgba(45, 212, 191, 0.3) !important; color: #99f6e4 !important; padding: 0.25rem 0.75rem !important; border-radius: 999px !important; font-size: 0.8rem !important; font-weight: bold !important; }
    .hero-banner .tag-text { color: #99f6e4 !important; font-size: 0.8rem !important; font-weight: bold !important; }
    .hero-banner .tag-slash { color: #94a3b8 !important; }
    .hero-banner .sub-title { color: #a5f3fc !important; font-size: 0.75rem !important; font-weight: 800 !important; letter-spacing: 0.25em !important; text-transform: uppercase !important; margin-bottom: 0.5rem !important; }
    [data-testid="stExpander"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 18px !important; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04) !important; margin-bottom: 15px !important; overflow: hidden !important; }
    [data-testid="stExpander"] details summary { background: linear-gradient(to right, #EFF6FF, #FFFFFF) !important; padding: 15px 20px !important; border-bottom: 1px solid #E2E8F0 !important; }
    [data-testid="stExpander"] details summary p { color: #1D4ED8 !important; font-weight: 900 !important; font-size: 1.15rem !important; letter-spacing: 0.05em !important; }
    [data-testid="stExpander"] details summary svg { fill: #1D4ED8 !important; }
    [data-testid="stExpander"] details > div { padding: 20px !important; background-color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div, .stTextArea>div>div>textarea { background-color: #F8FAFC !important; border: 1px solid #DBE3EA !important; border-radius: 12px !important; padding: 8px 12px !important; }
    .stRadio label p { font-weight: 600 !important; color: #1e293b !important; }
    .stButton > button { background-color: #0B1F3A !important; color: #FFFFFF !important; border-radius: 16px !important; padding: 0.8rem 2rem !important; font-weight: 900 !important; font-size: 1.1rem !important; border: none !important; box-shadow: 0 10px 20px rgba(11, 31, 58, 0.15) !important; width: 100% !important; transition: all 0.3s ease !important; }
    .stButton > button:hover { background-color: #164E63 !important; transform: translateY(-2px) !important; }
    .stButton > button p { color: #FFFFFF !important; }
    [data-testid="stMetric"] { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 16px !important; padding: 15px !important; box-shadow: 0 3px 12px rgba(15, 23, 42, 0.03) !important; }
    [data-testid="stMetricLabel"] p { color: #64748B !important; font-weight: 800 !important; font-size: 0.85rem !important; }
    [data-testid="stMetricValue"] div { color: #0F172A !important; font-weight: 900 !important; font-size: 1.8rem !important; }
    
    /* 回饋卡片專屬樣式 */
    .feedback-card { padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem; border: 1px solid #E2E8F0; background: #FFFFFF; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .feedback-card h4 { display: flex; align-items: center; gap: 0.5rem; margin-top: 0; font-size: 1.1rem; font-weight: 900; }
    .feedback-card.glow-green { border-color: #6EE7B7; box-shadow: 0 0 15px rgba(16, 185, 129, 0.1); }
    .feedback-card.glow-yellow { border-color: #FCD34D; box-shadow: 0 0 15px rgba(245, 158, 11, 0.1); }
    .feedback-card.glow-red { border-color: #FCA5A5; box-shadow: 0 0 15px rgba(239, 68, 68, 0.1); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 0.5 側邊欄：系統進階設定 (API 與自訂標的)
# ==========================================
with st.sidebar:
    st.header("⚙️ 系統進階設定")
    
    st.subheader("1. 投資宇宙 (Investment Universe)")
    st.markdown("請輸入美股代碼，以半形逗號分隔。建議包含**股、債、原物料**以發揮 MPT 分散效果。")
    custom_tickers_input = st.text_input("自訂候選標的清單", value="AAPL, SPY, TLT, GLD, VNQ")
    raw_tickers = [t.strip().upper() for t in custom_tickers_input.replace("，", ",").split(",") if t.strip()]
    
    if len(raw_tickers) < 3:
        st.warning("⚠️ 標的數量過少，已恢復預設配置。請至少輸入 3 檔不同屬性的標的。")
        TICKERS = ["AAPL", "SPY", "TLT", "GLD", "VNQ"]
    else:
        TICKERS = raw_tickers

    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    st.subheader("2. AI 語意分析連線")
    st.markdown("若使用**開放式問答模式**，請務必填寫長庚 LLM 資訊。")
    api_base_url = st.text_input("API Base URL", value="https://air.cgu.edu.tw/cgullmapi/v1/chat/completions")
    model_name = st.text_input("模型名稱", value="gpt-5.6-luna")
    api_key = st.text_input("API Key", type="password", placeholder="請輸入您的 API 金鑰")

# ==========================================
# 1. 頂部看板與常數定義
# ==========================================
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
        <span class="tag-badge">長庚大學</span><span class="tag-slash">/</span><span class="tag-text">數位金融科技系</span>
    </div>
    <div class="sub-title">Dynamic Digital Investor Profiling System</div>
    <h1>動態數位投資者輪廓系統</h1>
    <p class="desc">結合傳統風險評估、財務硬限制與行為金融分析，建立您的個人化動態投資人風險圖像。</p>
</div>
""", unsafe_allow_html=True)

EXTENDED_COLORS = ["#2563EB", "#0F766E", "#D97706", "#64748B", "#8B5CF6", "#DC2626", "#059669", "#EA580C", "#4F46E5", "#DB2777"]
TRADING_DAYS = 252
N_PORTFOLIOS = 10_000
RISK_FREE_RATE = 0.02
RISK_TO_KEY = {"保守型": "conservative", "穩健型": "moderate", "積極型": "aggressive"}
PREF_TO_BUCKET = {"極度保守": 0, "保守型": 0, "穩健型": 1, "積極型": 2, "極度積極": 2}

# ==========================================
# 2. 核心 MPT 演算法與 AI 處理函數
# ==========================================
@st.cache_data(show_spinner="正在下載市場資料並進行蒙地卡羅模擬…", ttl=3600)
def run_monte_carlo_mpt(tickers: tuple, n_portfolios: int = N_PORTFOLIOS, seed: int = 42):
    raw_data = yf.download(tickers=list(tickers), period="5y", interval="1d", auto_adjust=False, progress=False)
    
    if isinstance(raw_data.columns, pd.MultiIndex):
        prices = raw_data["Adj Close"].copy() if "Adj Close" in raw_data.columns.get_level_values(0) else raw_data.xs("Adj Close", axis=1, level=1).copy()
    else:
        prices = raw_data[["Adj Close"]].copy()
        if len(list(tickers)) == 1:
            prices.columns = list(tickers)

    prices = prices.dropna(axis=1, how='all')
    prices = prices.apply(pd.to_numeric, errors="coerce").dropna(how="any")
    
    valid_tickers = list(prices.columns)
    if len(valid_tickers) < 2:
        raise ValueError("有效的標的數量不足（至少需 2 檔），請檢查輸入的代碼是否正確。")

    return_matrix = prices.pct_change(fill_method=None).dropna(how="any")
    
    # === 新增：計算相關係數矩陣 ===
    corr_matrix = return_matrix.corr()
    
    n_obs = len(return_matrix)
    expected_returns = ((1 + return_matrix).prod() ** (TRADING_DAYS / n_obs) - 1).to_numpy()
    annualized_cov_matrix = (return_matrix.cov() * TRADING_DAYS).to_numpy()
    
    rng = np.random.default_rng(seed)
    weights = rng.dirichlet(alpha=np.ones(len(valid_tickers)), size=n_portfolios)
    
    portfolio_returns = weights @ expected_returns
    portfolio_variances = np.maximum(np.einsum("ij,jk,ik->i", weights, annualized_cov_matrix, weights), 0)
    
    results = pd.DataFrame({"Expected Annual Return": portfolio_returns, "Annualized Volatility": np.sqrt(portfolio_variances)})
    return pd.concat([pd.DataFrame(weights, columns=valid_tickers), results], axis=1), valid_tickers, corr_matrix

def pick_representative_portfolios(results):
    vol, ret = results["Annualized Volatility"], results["Expected Annual Return"]
    mvp_idx = vol.idxmin()
    agg_idx = ((ret - RISK_FREE_RATE) / vol.replace(0, np.nan)).idxmax()
    mod_idx = (vol - 0.5 * (results.loc[mvp_idx, "Annualized Volatility"] + results.loc[agg_idx, "Annualized Volatility"])).abs().idxmin()
    return {"conservative": results.loc[mvp_idx], "moderate": results.loc[mod_idx], "aggressive": results.loc[agg_idx]}

def call_cgu_llm(answers, api_key, model_name, api_url):
    system_prompt = """你是一位專業的行為金融學專家。請閱讀使用者的開放式回答與財務限制，在五個維度給出 0~100 的數字評分，並提供三段具體的文字回饋。
    嚴格只回傳 JSON，格式必須完全符合：
    {
      "radar_scores": {"calmness": 0, "risk_acceptance": 0, "independent_thinking": 0, "rational_confidence": 0, "discipline": 0},
      "feedback": {
        "current_emotional_state": "精確點出情緒盲點",
        "behavioral_alert": "指出可能觸發危險的投資行為",
        "personalized_advice": "給出具體數字或資產類別的執行建議"
      }
    }
    """
    user_prompt = f"Q1:{answers['q1_text']}\nQ2:{answers['q2_text']}\nQ3:{answers['q3_text']}\nQ4:{answers['q4_text']}\n負債:{answers['debt_status']}\n流動性:{answers['liquidity_need']}"
    try:
        response = requests.post(api_url, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}, json={"model": model_name, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}, timeout=15)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        st.error(f"API 連線或解析失敗: {str(e)}")
        return None

def classify_investor(answers, radar_scores):
    level = PREF_TO_BUCKET[answers["risk_pref"]]
    if answers["mode"] == "選擇題":
        b_avg = sum(answers["q_scores"]) / 10.0 
    else:
        ai_avg = sum(radar_scores.values()) / 5
        b_avg = 0.0 if ai_avg < 40 else 2.0 if ai_avg > 70 else 1.0
        
    if b_avg <= 0.6 and level > 0: level -= 1
    elif b_avg >= 1.4 and level < 2: level += 1
    
    debt_text, liq_text = answers["debt_status"].replace(" ", ""), answers["liquidity_need"].replace(" ", "")
    is_red_debt = any(k in debt_text for k in ["信貸", "卡債", "高利", "重", "壓力大", "還不起"])
    is_yellow_debt = any(k in debt_text for k in ["房貸", "車貸", "學貸", "貸款"])
    is_red_liq = any(k in liq_text for k in ["急用", "醫療", "結婚", "買房", "購屋", "頭期款", "一年", "半年", "近期"])
    
    status_color, status_title, status_msg = "green", "綠燈 · 整體條件吻合", "基礎風險需求與客觀財務條件整體符合，可依計畫執行。"
    if answers["horizon_years"] < 5 or is_red_liq or is_red_debt:
        level, status_color, status_title, status_msg = 0, "red", "紅燈 · 觸發財務硬限制", "偵測到投資期限過短或有沉重負債/近期大額開銷，系統已強制降級為保守型以保護本金。"
    elif answers["investable_pct"] < 20 or is_yellow_debt:
        if level > 1: level = 1
        if status_color != "red":
            status_color, status_title, status_msg = "yellow", "黃燈 · 需留意現金流", "偵測到財務空間較緊繃 (或背負中長天期貸款)，系統建議最高配置為穩健型。"
            
    return {0: "保守型", 1: "穩健型", 2: "積極型"}[level], status_color, status_title, status_msg

# ==========================================
# 3. 圖表繪製
# ==========================================
def plot_scatter(results, selected, final_label, reps):
    sharpe = (results["Expected Annual Return"] - RISK_FREE_RATE) / results["Annualized Volatility"].replace(0, np.nan)
    fig = go.Figure(go.Scatter(x=results["Annualized Volatility"] * 100, y=results["Expected Annual Return"] * 100, mode="markers", marker=dict(size=4, color=sharpe, colorscale="Tealgrn", opacity=0.3, colorbar=dict(title="夏普比率", thickness=10))))
    for key, name, color, symbol in [("conservative", "保守型", "#1D4ED8", "diamond"), ("moderate", "穩健型", "#D97706", "square"), ("aggressive", "積極型", "#B91C1C", "triangle-up")]:
        fig.add_trace(go.Scatter(x=[reps[key]["Annualized Volatility"] * 100], y=[reps[key]["Expected Annual Return"] * 100], mode="markers+text", name=name, text=[name], textposition="top center", marker=dict(size=12, color=color, symbol=symbol, line=dict(width=1, color="#FFF"))))
    fig.add_trace(go.Scatter(x=[selected["Annualized Volatility"] * 100], y=[selected["Expected Annual Return"] * 100], mode="markers+text", name=f"您的最適組合", text=["⭐ 您的最適組合"], textposition="bottom center", marker=dict(size=18, color="#F59E0B", symbol="star", line=dict(width=1.5, color="#000"))))
    fig.update_layout(title="蒙地卡羅機會集合", xaxis_title="年化波動率 (%)", yaxis_title="預期年化報酬 (%)", template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,250,252,0.5)")
    return fig

def plot_radar(scores):
    categories, values = list(scores.keys()), list(scores.values())
    fig = go.Figure(go.Scatterpolar(r=values + values[:1], theta=categories + categories[:1], fill="toself", line=dict(color="#0F766E", width=3), fillcolor="rgba(15, 118, 110, 0.15)", marker=dict(color="#2563EB", size=8, line=dict(color="#FFFFFF", width=2))))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#E2E8F0"), bgcolor="#F8FAFC"), showlegend=False, margin=dict(l=40, r=40, t=30, b=30), height=320, paper_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_donut(selected, valid_tickers):
    weights = [float(selected[t]) for t in valid_tickers]
    dynamic_colors = [EXTENDED_COLORS[i % len(EXTENDED_COLORS)] for i in range(len(valid_tickers))]
    fig = go.Figure(go.Pie(labels=valid_tickers, values=weights, hole=0.6, marker=dict(colors=dynamic_colors, line=dict(color="#ffffff", width=3)), textinfo="percent"))
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=320, paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="v", y=0.5, font=dict(color="#1F2937", size=13)))
    return fig

# === 新增：繪製相關係數熱力圖 ===
def plot_correlation_heatmap(corr_matrix):
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        colorscale="RdBu_r", # 使用與 seabon 相同的紅藍漸層
        zmin=-1, zmax=1,
        hovertemplate="資產 X: %{x}<br>資產 Y: %{y}<br>相關係數: %{z:.2f}<extra></extra>"
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_yaxes(autorange="reversed") # 讓矩陣的排列方向更符合視覺習慣
    return fig

# ==========================================
# 4. 介面佈局
# ==========================================
col_input, right_col = st.columns([1, 1.25], gap="large")

with col_input:
    with st.expander("📌 STAGE 01：傳統風險評估", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("年齡", min_value=18, max_value=120, value=32)
            liquid_assets = st.number_input("流動資產 (萬)", min_value=0, value=80)
            horizon_value = st.number_input("投資期限", min_value=1, value=8)
        with col2:
            income = st.number_input("年收入 (萬)", min_value=0, value=120)
            real_estate = st.number_input("不動產 (萬)", min_value=0, value=0)
            horizon_unit = st.selectbox("期限單位", ["年", "月"])
        risk_pref = st.select_slider("主觀風險偏好", options=["極度保守", "保守型", "穩健型", "積極型", "極度積極"], value="穩健型")

    with st.expander("🧠 STAGE 02：行為與情緒評估", expanded=True):
        mode = st.radio("請選擇問卷填寫模式", ["選擇題 (快速適配)", "開放式問答 (AI 深度分析)"], horizontal=True)
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        
        MCQ_LIST = [
            ("Q1 損失規避：投資單月下跌20%，您的第一反應是？", ["全數認賠殺出，換回現金", "不動作，觀望基本面", "視為買點，逢低加碼"]),
            ("Q2 從眾傾向：新聞與朋友都在瘋狂討論熱門股，您會？", ["完全不碰，堅守原有配置", "研究財報，合理才少量買進", "怕錯過行情，立刻跟進買入"]),
            ("Q3 過度自信：您認為自己挑選標的的能力如何？", ["無法預測，只買大盤指數", "能挑選好股，也搭配大盤分散", "絕對有信心能擊敗大盤績效"]),
            ("Q4 心理帳戶：拿到一筆10萬元的意外獎金，您會？", ["全部存入銀行或買保本定存", "一半儲蓄、一半投入穩健資產", "全部投入股市追求高報酬"]),
            ("Q5 後悔厭惡：發現之前錯賣的股票後來大漲，您會？", ["不再碰該檔股票避免心痛", "重新評估目前的合理價位", "為了賺回來，立刻追高買回"]),
            ("Q6 近期偏誤：如果股市連續大漲三個月，您對未來預期是？", ["覺得快崩盤了，全面獲利了結", "保持既有投資節奏，不改變", "認為牛市確立，借錢或加碼"]),
            ("Q7 波動忍受：能忍受資產一年內最大縮水多少而不影響睡眠？", ["5% 以內", "10% ~ 15%", "20% 以上"]),
            ("Q8 熟悉度偏誤：選擇投資標的時，您傾向？", ["只買最熟悉的本土定存/金融股", "國內外知名大型股及ETF", "積極尋找爆發力新興科技小股"]),
            ("Q9 耐心與短視：投資的股票三個月沒漲但大盤在漲，您會？", ["覺得不安心，賣掉換現金", "耐心等待，相信自己的研究", "覺得太慢，立刻換成熱門飆股"]),
            ("Q10 紀律自制力：每個月發薪水時，您的投資紀律是？", ["嚴格執行先儲蓄投資，剩下消費", "偶爾會因當月開銷大停止扣款", "常憑感覺隨意挪用投資金消費"])
        ]
        
        q_scores = [0] * 10
        q1_text = q2_text = q3_text = q4_text = None
        
        if mode == "選擇題 (快速適配)":
            c1, c2 = st.columns(2)
            for i, (q_title, opts) in enumerate(MCQ_LIST):
                with c1 if i < 5 else c2:
                    ans = st.radio(q_title, opts)
                    q_scores[i] = opts.index(ans)
        else:
            q1_text = st.text_area("Q1 損失規避：若市場下跌 20%，您會立刻停損還是繼續加碼？為什麼？", placeholder="請描述您的真實感受...")
            q2_text = st.text_area("Q2 從眾傾向：看到朋友買熱門股大賺，您會改變策略跟進嗎？", placeholder="請描述您的應對方式...")
            q3_text = st.text_area("Q3 過度自信：您認為自己過去的投資績效是靠實力還是運氣？", placeholder="請簡述您的過往經驗...")
            q4_text = st.text_area("Q4 自制力：拿到意外獎金，您會立刻消費還是依計畫投資？", placeholder="請描述您處理意外收入的方式...")

    with st.expander("💼 STAGE 03：財務條件與極限", expanded=True):
        col3, col4 = st.columns(2)
        with col3: expenses = st.number_input("每月支出 (萬)", min_value=0.0, value=4.5)
        with col4: inv_method = st.selectbox("預計投入方式", ["每月定期定額", "單筆現金 All-in", "單筆打底 + 定期定額"])
        inv_percent = st.slider("可投資資金佔淨資產比例 (%)", min_value=0, max_value=100, value=40)
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        debt_status = st.text_input("4. 負債狀況與結構", value="無負債", placeholder="例如：每月房貸3萬，無信貸")
        liquidity_need = st.text_input("5. 短期流動性需求 (一年內)", value="無需求", placeholder="例如：預計兩年後需要一筆結婚基金，或目前無需求")

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🚀 產出最佳化投資組合配置", use_container_width=True)

with right_col:
    if not analyze_btn and "profile_ready" not in st.session_state:
        st.info("👈 請在左側完成問卷或在左側邊欄自訂候選標的後，按下分析按鈕。")
    else:
        answers = {
            "mode": "選擇題" if "選擇題" in mode else "開放式",
            "horizon_years": horizon_value if horizon_unit == "年" else horizon_value / 12, 
            "risk_pref": risk_pref, "q_scores": q_scores,
            "q1_text": q1_text, "q2_text": q2_text, "q3_text": q3_text, "q4_text": q4_text,
            "investable_pct": inv_percent, "debt_status": debt_status, "liquidity_need": liquidity_need
        }
        
        ai_feedback = None
        if answers["mode"] == "選擇題":
            v = answers["q_scores"]
            radar_scores = {
                "損失承受力": (v[0] + v[6]) * 25, "獨立判斷力": ((2-v[1]) + (2-v[4])) * 25,
                "適度自信度": (v[2] + v[7]) * 25, "紀律自制力": ((2-v[8]) + (2-v[9])) * 25,
                "抗焦慮沉著": ((2-v[3]) + (2-v[5])) * 25
            }
        else:
            if not api_key:
                st.error("⚠️ 請先在左上方隱藏選單「>」中輸入 API Key，才能執行開放式分析！")
                st.stop()
            with st.spinner("🧠 正在將您的問答送交長庚 LLM 分析深層心理特徵與具體建議..."):
                ai_result = call_cgu_llm(answers, api_key, model_name, api_base_url)
                if not ai_result: st.stop()
                
                radar_scores = ai_result.get("radar_scores", {})
                ai_feedback = ai_result.get("feedback", {})
                if not radar_scores:
                    radar_scores = {"損失承受力":50, "獨立判斷力":50, "適度自信度":50, "紀律自制力":50, "抗焦慮沉著":50}

        st.session_state["profile_ready"] = True
        final_label, status_color, status_title, status_msg = classify_investor(answers, radar_scores)
        
        try:
            results, valid_tickers, corr_matrix = run_monte_carlo_mpt(tuple(TICKERS))
        except Exception as e:
            st.error(f"獲取市場資料或計算最佳化時發生錯誤: {e}")
            st.stop()
            
        reps = pick_representative_portfolios(results)
        selected = reps[RISK_TO_KEY[final_label]]

        # 渲染狀態燈號
        color_map = {
            "green": {"bg": "#ECFDF5", "border": "#A7F3D0", "dot": "#10B981", "shadow": "rgba(16, 185, 129, 0.12)", "text": "#047857", "glow": "glow-green"},
            "yellow": {"bg": "#FFFBEB", "border": "#FDE68A", "dot": "#F59E0B", "shadow": "rgba(245, 158, 11, 0.12)", "text": "#B45309", "glow": "glow-yellow"},
            "red": {"bg": "#FFF1F2", "border": "#FECACA", "dot": "#EF4444", "shadow": "rgba(239, 68, 68, 0.12)", "text": "#BE123C", "glow": "glow-red"}
        }
        c = color_map[status_color]
        
        st.markdown(f"""
        <div style="background: {c['bg']}; border: 1px solid {c['border']}; padding: 1.5rem 2rem; border-radius: 1.5rem; display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem; box-shadow: 0 4px 14px rgba(0,0,0,0.02);">
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="width: 18px; height: 18px; border-radius: 50%; background: {c['dot']}; box-shadow: 0 0 0 6px {c['shadow']}; flex-shrink: 0;"></div>
                <div>
                    <h3 style="margin: 0; color: #1F2937 !important; font-size: 1.4rem; font-weight: 900;">{status_title}</h3>
                    <p style="margin: 0; color: {c['text']} !important; margin-top: 0.5rem; font-weight: 600;">{status_msg}</p>
                </div>
            </div>
            <div style="background: white; padding: 1rem 1.5rem; border-radius: 1rem; text-align: center; border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                <div style="font-size: 0.75rem; color: #64748b; font-weight: 800; letter-spacing: 0.1em; margin-bottom: 0.25rem;">最終風險類型</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #0F172A;">{final_label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        met1, met2, met3 = st.columns(3)
        sharpe_val = (selected["Expected Annual Return"] - RISK_FREE_RATE) / selected["Annualized Volatility"]
        met1.metric("預期年化報酬", f"{selected['Expected Annual Return']*100:.2f}%")
        met2.metric("年化波動率", f"{selected['Annualized Volatility']*100:.2f}%")
        met3.metric("夏普比率 (Rf=2%)", f"{sharpe_val:.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_scatter(results, selected, final_label, reps), use_container_width=True, config={'displayModeBar': False})

        # === AI 與本地動態文字回饋卡片 ===
        st.markdown(f"<h4 style='color:#1e293b; font-weight:900; margin-top:1.5rem; margin-bottom:1rem;'>🤖 系統深度回饋與建議</h4>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns(3)
        
        if answers["mode"] == "開放式" and ai_feedback:
            emo_text = ai_feedback.get("current_emotional_state", "無資料")
            alert_text = ai_feedback.get("behavioral_alert", "無資料")
            adv_text = ai_feedback.get("personalized_advice", "無資料")
        else:
            if radar_scores["抗焦慮沉著"] >= 60 and radar_scores["損失承受力"] >= 60:
                emo_text = "目前情緒狀態穩定且具備良好的風險承受力，面對市場波動應能保持客觀理性。"
            elif radar_scores["抗焦慮沉著"] < 50:
                emo_text = "對市場波動的焦慮感較高，容易因為短期虧損而產生恐慌情緒或不安全感。"
            else:
                emo_text = "情緒狀態偏向保守防禦，可能對潛在的資金回撤感到一定程度的心理壓力。"
            
            lowest_dim = min(radar_scores, key=radar_scores.get)
            if lowest_dim == "獨立判斷力": alert_text = "從眾傾向較高，請避免因為市場熱潮或身邊親友的推薦而盲目追高熱門股。"
            elif lowest_dim == "紀律自制力": alert_text = "財務紀律可能較為鬆散，建議設定自動扣款與定期定額機制來避免隨意挪用資金。"
            elif lowest_dim == "適度自信度": alert_text = "可能有過度自信的傾向，請避免單筆重押單一標的，務必落實資產的多元分散。"
            else: alert_text = "面對突發的市場下跌，請避免因短線恐慌而輕易改變原先設定好的長期投資計畫。"
                
            if status_color == "red": adv_text = "財務硬限制亮紅燈。首要任務為降低負債或補足緊急預備金，目前請以絕對保本的定存或貨幣型基金為主。"
            elif status_color == "yellow": adv_text = "現金流略顯緊繃。請確保擁有 6 個月的生活預備金，投資部位應以穩健收息資產 (如高評級債券) 為重。"
            else:
                if final_label == "積極型": adv_text = f"可承受較高風險，系統已根據您提供的投資宇宙，為您挑選出夏普比率最高的積極配置。"
                elif final_label == "穩健型": adv_text = f"追求股債平衡與波動控制，系統已在您的候選標的池中找出最適中的配置比例。"
                else: adv_text = f"防禦優先，系統已在您提供的資產池中，為您找出歷史波動度最低的 MVP 投資組合。"

        with col_f1:
            st.markdown(f"""
            <div class="feedback-card {c['glow']}">
                <h4 style="color: #0F766E;">🧠 當下情緒狀態</h4>
                <p style="color: #334155; font-size: 0.95rem; line-height: 1.6; margin-top: 10px;">{emo_text}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_f2:
            st.markdown(f"""
            <div class="feedback-card {c['glow']}">
                <h4 style="color: #D97706;">⚠️ 行為與偏誤提醒</h4>
                <p style="color: #334155; font-size: 0.95rem; line-height: 1.6; margin-top: 10px;">{alert_text}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_f3:
            st.markdown(f"""
            <div class="feedback-card {c['glow']}">
                <h4 style="color: #2563EB;">🎯 專屬即時建議</h4>
                <p style="color: #334155; font-size: 0.95rem; line-height: 1.6; margin-top: 10px;">{adv_text}</p>
            </div>
            """, unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            title = "◆ 傳統行為心理分析" if answers["mode"] == "選擇題" else "◆ AI 深度語意分析結果"
            st.markdown(f"<h4 style='color:#0F766E; font-weight:800; margin-bottom:0;'>{title}</h4>", unsafe_allow_html=True)
            st.plotly_chart(plot_radar(radar_scores), use_container_width=True, config={'displayModeBar': False})
            
        with col_r2:
            st.markdown("<h4 style='color:#2563EB; font-weight:800; margin-bottom:0;'>◆ MPT 資產配置建議</h4>", unsafe_allow_html=True)
            st.plotly_chart(plot_donut(selected, valid_tickers), use_container_width=True, config={'displayModeBar': False})

        # === 新增：資產相關性熱力圖 (風險分散證據) ===
        st.markdown("<hr style='margin: 20px 0; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='color:#D97706; font-weight:800; margin-bottom:0;'>◆ 資產相關性熱力圖 (風險分散證據)</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.9rem; color:#64748b;'>深藍色代表高度正相關（同漲同跌），紅色代表負相關（互補）。好的資產配置應包含低相關或負相關的標的以降低波動。</p>", unsafe_allow_html=True)
        st.plotly_chart(plot_correlation_heatmap(corr_matrix), use_container_width=True, config={'displayModeBar': False})