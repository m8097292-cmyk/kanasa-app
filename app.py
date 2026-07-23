import streamlit as st
import google.generativeai as genai
import urllib.parse
import csv
import os

# 1. Geminiの初期設定
GOOGLE_API_KEY = "AQ.Ab8RN6LbTNW5CFttCGZtEgJ7RN7X4bGvg3nXLzO_IorhU6DNPg"
genai.configure(api_key=GOOGLE_API_KEY)

# 📂 外部ファイルからプロンプトを読み込む
def load_prompt():
    if os.path.exists("prompt.txt"):
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "あなたは沖縄の不動産・相続・税金・土地活用・風習に特化した優秀なAIアシスタントです。"

SYSTEM_INSTRUCTION = load_prompt()

# 📊 外部ファイルから業者リストを読み込む
def load_vendors():
    vendors = []
    if os.path.exists("vendors.csv"):
        with open("vendors.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vendors.append(row)
    else:
        vendors = [
            {"name": "那覇カチコミ司法書士事務所", "area": "那覇市", "type": "相続", "email": "test-legal@example.com", "pr": "戦前名義の複雑な相続登記、親族間の調整が得意です！", "image_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=150"},
            {"name": "中部うちなー不動産", "area": "沖縄市", "type": "売買", "email": "test-estate@example.com", "pr": "軍用地の売却・運用実績多数！高価買取します。", "image_url": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=150"},
            {"name": "シーサー解体工業", "area": "宜野湾市", "type": "解体", "email": "test-demolition@example.com", "pr": "実家の中古住宅の解体を近隣対策バッチリで行います！", "image_url": "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=150"}
        ]
    return vendors

VENDORS = load_vendors()
TAKESHI_ADMIN_EMAIL = "takeshi-platform-admin@example.com"

# 🎨 2. デザインの設定（PC＆スマホ・レスポンシブ完全最適化版）
st.set_page_config(page_title="沖縄不動産無料相談窓口 カナサ", page_icon="🌴", layout="wide")

st.markdown("""
    <style>
    /* 🌊 画面全体にWIX風の明るいグラデーションを敷きます */
    .stApp { 
        background: linear-gradient(135deg, #FFFBEC 0%, #FFEFF2 50%, #FFFFFF 100%) !important;
        background-attachment: fixed;
    }
    
    /* 💡 チャットの背景設定 */
    [data-testid="stChatMessage"] { 
        background-color: rgba(255, 255, 255, 0.85) !important; 
        border: 1px solid rgba(226, 232, 240, 0.5) !important; 
        border-radius: 12px !important; 
        padding: 10px !important; 
        margin-bottom: 8px !important; 
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }

    /* 余白の見切れ防止 */
    .block-container { 
        padding-top: 35px !important; 
        padding-bottom: 5px !important; 
        padding-left: 10px !important; 
        padding-right: 10px !important; 
    }

    /* 📱 WIX風ヘッダーコンテナ（レスポンシブ対応） */
    .main-title-container {
        text-align: center;
        padding: 20px 12px;
        background: linear-gradient(135deg, rgba(255, 245, 245, 0.9) 0%, rgba(255, 234, 238, 0.9) 100%);
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #FFE0E6;
        backdrop-filter: blur(4px);
    }
    
    /* ロゴ（可変サイズ：36px〜54px） */
    .main-logo {
        font-size: clamp(36px, 8vw, 54px) !important;
        font-weight: bold;
        color: #333333;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        letter-spacing: 2px;
        margin: 8px 0;
    }
    
    /* 説明テキスト（可変サイズ・文字折り返し最適化） */
    .sub-text {
        color: #555555 !important;
        font-size: clamp(12px, 3.2vw, 15px) !important;
        line-height: 1.6 !important;
        margin-bottom: 6px !important;
        word-break: normal;
        overflow-wrap: break-word;
    }

    .top-sub-title {
        color: #666666;
        font-size: clamp(12px, 3vw, 14px);
        font-weight: bold;
        margin: 0;
    }

    .catch-phrase {
        color: #FF5A76;
        font-size: clamp(13px, 3.5vw, 16px);
        font-weight: bold;
        margin: 5px 0 12px 0;
    }

    /* ⭕ 箇条書き（リスト）の文字色を強制的に黒にする設定 */
    [data-testid="stChatMessage"] ul, 
    [data-testid="stChatMessage"] li { 
        color: #000000 !important; 
    }
    
    /* 入力欄やボタンの設定（スマホで潰れないように調整） */
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span { color: #000000 !important; font-size: 14px !important; line-height: 1.5 !important; }
    .stChatInputContainer { border-radius: 20px; background-color: #FFFFFF !important; }
    .stChatInputContainer input { color: #000000 !important; font-size: 14px !important; }
    
    .diagnose-btn button { background-color: #FF8C00 !important; color: #FFFFFF !important; border: none !important; font-weight: bold !important; font-size: 16px !important; height: 50px !important; border-radius: 25px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    
    /* 選択肢ボタン（文字がはみ出さないサイズ感に調整） */
    .stButton button { 
        background-color: #FFFFFF !important; 
        color: #005A9C !important; 
        border: 1px solid #005A9C !important; 
        border-radius: 8px !important; 
        font-size: clamp(11px, 2.8vw, 13px) !important; 
        width: 100% !important; 
        min-height: 44px !important; 
        padding: 4px 6px !important; 
        margin-bottom: 4px !important; 
        line-height: 1.3 !important;
    }
    .stButton button:hover { background-color: #005A9C !important; color: #FFFFFF !important; }
    
    /* 📦 業者カード（スマホで縦並びに崩れないレスポンシブカード） */
    .vendor-card { 
        background-color: rgba(255, 248, 238, 0.95) !important; 
        border: 2px solid #F28C28; 
        border-radius: 12px; 
        padding: 15px; 
        margin-top: 10px; 
        margin-bottom: 15px; 
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        align-items: flex-start;
    }
    .vendor-img {
        width: 140px;
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        object-fit: cover;
    }
    .vendor-info {
        flex: 1;
        min-width: 200px;
    }
    </style>
""", unsafe_allow_html=True)


# 🌴 ヘッダー部分（自動折り返し＆文字サイズレスポンシブ対応）
st.markdown("""
    <div class="main-title-container">
        <p class="top-sub-title">完全無料の不動産相談窓口</p>
        <p class="top-sub-title">相続・売買・不動産活用</p>
        <div class="main-logo">KANASA</div>
        <p class="catch-phrase">〜 不動産の分からないをサポート 〜</p>
        <p class="sub-text">匿名で安心🌞名前や住所の入力不要</p>
        <p class="sub-text">営業電話は一切なし</p>
        <p class="sub-text">あなたと地元のサポート企業を繋ぐパートナー</p>
        <p class="sub-text">お悩みはAIカナサに気軽に相談</p>
    </div>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "messages" not in st.session_state:
    welcome_text = """めんそーれ！AI相談員の「カナサ」です。🌴
不動産や相続でお悩みのウチなんちゅを無料サポート！

⚠️ **安心のためのお願い**
名前や電話番号は**チャット内に入力せず**、匿名で安心してご相談してください！"""
    st.session_state.messages = [{"role": "assistant", "content": welcome_text}]
    st.session_state.current_stage = "initial"

if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
    st.session_state.chat = model.start_chat(history=[])

# チャット履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 選択肢ボタンの表示
st.markdown("""
    <p style="
        color: #000000; 
        font-weight: bold; 
        font-size: clamp(11px, 3.2vw, 14px); 
        margin-bottom: 8px; 
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis;
    ">
        ▼ 当てはまるボタンを押すか、下の入力欄からメッセージを入力
    </p>
""", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
click_input = None

if st.session_state.current_stage == "initial":
    with col1:
        if st.button("💡 相続が発生したけれど何からすれば良い？"):
            click_input = "相続が発生したけれど、何からしたらいいか分からないさぁ"
            st.session_state.current_stage = "souzoku"
    with col2:
        if st.button("🔰 軍用地の仕組みが良く分からない"):
            click_input = "軍用地を相続したけれど、仕組みが全然分からない"
            st.session_state.current_stage = "gunyou"
    with col3:
        if st.button("🏚️ 古家を活用または解体したい"):
            click_input = "古い実家を処分したいけれど、解体費用ってどのくらい？"
            st.session_state.current_stage = "kaitai"

elif st.session_state.current_stage == "souzoku":
    with col1:
        if st.button("👨‍👩‍👧‍👦 相続人の確認"):
            click_input = "相続の手続きをするにあたって、法定相続人が何人いるかを確認する仕組みを教えて"
    with col2:
        if st.button("💰 相続税の不安"):
            click_input = "相続税の計算の仕組みや、基礎控除額がいくらになるのか目安を教えてほしいさぁ"
    with col3:
        if st.button("↩️ 戻る"):
            st.session_state.current_stage = "initial"
            st.rerun()

elif st.session_state.current_stage == "gunyou":
    with col1:
        if st.button("📈 相場の調べ方"):
            click_input = "軍用地の価値を決める『倍率』って何？どうやって相場を調べたらいいか教えて"
    with col2:
        if st.button("⏳ 将来のリスク"):
            click_input = "軍用地って将来国から返還されたらどうなるの？リスクについて教えて"
    with col3:
        if st.button("↩️ 戻る"):
            st.session_state.current_stage = "initial"
            st.rerun()

elif st.session_state.current_stage == "kaitai":
    with col1:
        if st.button("💸 解体の坪単価"):
            click_input = "沖縄で木造やRCの実家を解体する場合、大まかな坪単価の目安ってどのくらい？"
    with col2:
        if st.button("🤝 売るか貸すか"):
            click_input = "古い家を解体して更地にした後、売却するのと賃貸で運用するの、どっちがいいかな？"
    with col3:
        if st.button("↩️ 戻る"):
            st.session_state.current_stage = "initial"
            st.rerun()

user_input = st.chat_input("お気軽にカナサにご相談ください...")
final_input = user_input if user_input else click_input

# メッセージ送信時の処理
if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(final_input)
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})

# --------------------------------------------------
# 💡【大進化】チャットルーム内・ボタン起動型マッチング
# --------------------------------------------------
st.write("---")
st.markdown("""
    <p style="
        color: #000000; 
        font-weight: bold; 
        font-size: clamp(11px, 3.2vw, 14px); 
        margin-bottom: 8px; 
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis;
    ">
        🤝相談者にマッチするサポート企業
    </p>
""", unsafe_allow_html=True)
