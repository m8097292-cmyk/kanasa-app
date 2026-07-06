import streamlit as st
import google.generativeai as genai
import urllib.parse
import csv
import os

# 1. Geminiの初期設定（ご自身のAPIキーに書き換えてください）
GOOGLE_API_KEY = "AQ.Ab8RN6LbTNW5CFttCGZtEgJ7RN7X4bGvg3nXLzO_IorhU6DNPg"
genai.configure(api_key=GOOGLE_API_KEY)

# 📂 外部ファイル（prompt.txt）からカナサの性格を読み込む仕組み
def load_prompt():
    if os.path.exists("prompt.txt"):
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "あなたは優秀なAIアシスタントです。" # 万が一ファイルがない場合の保険

SYSTEM_INSTRUCTION = load_prompt()

# 📊 外部ファイル（vendors.csv）から業者リストを読み込む仕組み
def load_vendors():
    vendors = []
    if os.path.exists("vendors.csv"):
        with open("vendors.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vendors.append(row)
    return vendors

VENDORS = load_vendors()
TAKESHI_ADMIN_EMAIL = "takeshi-platform-admin@example.com"

# 🎨 2. デザインの設定（スマホ・PC完全適正化版）
st.set_page_config(page_title="沖縄不動産無料相談窓口 カナサ", page_icon="🌴", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 40px !important; padding-bottom: 5px !important; padding-left: 10px !important; padding-right: 10px !important; }
    .stApp { background-color: #FFFFFF; }
    [data-testid="stChatMessage"] { background-color: #F8FAFC !important; border: 1px solid #E2E8F0 !important; border-radius: 12px !important; padding: 10px !important; margin-bottom: 8px !important; }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span { color: #000000 !important; font-size: 14px !important; line-height: 1.5 !important; }
    .stChatInputContainer { border-radius: 20px; background-color: #FFFFFF !important; }
    .stChatInputContainer input { color: #000000 !important; font-size: 14px !important; }
    .stButton button { background-color: #FFFFFF !important; color: #005A9C !important; border: 1px solid #005A9C !important; border-radius: 8px !important; font-size: 12px !important; width: 100% !important; min-height: 40px !important; padding: 4px 8px !important; margin-bottom: 4px !important; }
    .stButton button:hover { background-color: #005A9C !important; color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div style="margin-top: 5px;"></div>', unsafe_allow_html=True)

# セッション状態の初期化
if "messages" not in st.session_state:
    welcome_text = """めんそーれ！AI相談員の「カナサ」です。🌴
不動産や相続のモヤモヤを優しく紐解き、地元の安心なサポート企業へそっとバトンをお繋ぎします。

⚠️ **安心のためのお願い**
名前や電話番号は**ここには入力せず**、匿名で安心して相談してくださいね。

すぐ下のボタンを押すだけで相談を始められますよ！👇"""
    st.session_state.messages = [{"role": "assistant", "content": welcome_text}]
    st.session_state.current_stage = "initial"

if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
    st.session_state.chat = model.start_chat(history=[])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.write("▼ 当てはまるボタンを押すか、下の入力欄からメッセージを送ってね")
col1, col2, col3 = st.columns(3)
click_input = None

if st.session_state.current_stage == "initial":
    with col1:
        if st.button("💡 相続が不明"):
            click_input = "相続が発生したけれど、何からしたらいいか分からないさぁ"
            st.session_state.current_stage = "souzoku"
    with col2:
        if st.button("🔰 軍用地の仕組み"):
            click_input = "軍用地を相続したけれど、仕組みが全然分からない"
            st.session_state.current_stage = "gunyou"
    with col3:
        if st.button("🏚️ 実家の処分・解体"):
            click_input = "古い実家を処分したいけれど、解体費用ってどのくらい？"
            st.session_state.current_stage = "kaitai"

elif st.session_state.current_stage == "souzoku":
    with col1:
        if st.button("👨‍👩‍👧‍👦 相続人の確認"):
            click_input = "相続の手続きをするにあたって、法定相続人が何人いるかを確認する数式や仕組みを教えて"
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
            click_input = "沖縄で木造やRC（鉄筋コンクリート）の実家を解体する場合、大まかな坪単価の目安ってどのくらい？"
    with col2:
        if st.button("🤝 売るか貸すか"):
            click_input = "古い家を解体して更地にした後、売却するのと賃賃で運用するの、どっちが手残り多くなるかな？"
    with col3:
        if st.button("↩️ 戻る"):
            st.session_state.current_stage = "initial"
            st.rerun()

user_input = st.chat_input("お気軽にカナサにご相談ください...")
final_input = user_input if user_input else click_input

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(final_input)
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.rerun()

# 💡 自動業者仕分け ＆ メールテンプレート連携システム
st.sidebar.markdown("### 🤝 おススメのサポート企業")
st.sidebar.write("これまでの相談内容を引き継いで、地元の信頼できるプロの先生方に安全に直接問い合わせができます。")

conversation_summary = ""
for m in st.session_state.messages[1:]:
    role_name = "相談者" if m["role"] == "user" else "AIカナサ"
    conversation_summary += f"{role_name}: {m['content']}\n"

if conversation_summary and VENDORS:
    judge_model = genai.GenerativeModel('gemini-2.5-flash')
    judge_prompt = f"以下の相談内容を読み、この相談者が最も求めている専門家のカテゴリを【相続、売買、解体、賃貸】の中から漢字またはカタカナで1つだけ答えてください。\n\n相談内容：\n{conversation_summary}"
    
    try:
        detected_type = judge_model.generate_content(judge_prompt).text.strip()
        matched_vendors = [v for v in VENDORS if v["type"] in detected_type]
        
        if matched_vendors:
            for vendor in matched_vendors:
                st.sidebar.info(f"🏢 **{vendor['name']}**\n\n🎯 **専門分野:** {vendor['type']}\n\n📢 **特徴:** {vendor['pr']}")
                
                mail_subject = f"【AIカナサ窓口経由】新規ご相談（カテゴリ：{vendor['type']}）"
                mail_body = f"""{vendor['name']} 御中

お世話になっております。
こちらは「沖縄不動産無料相談窓口 カナサ」自動バトンタッチシステムです。

当サイトのAI相談員「カナサ」によるカウンセリングを終え、御社の強みに深く共感された相談者様より、以下の通り相談内容の引き継ぎがございました。

ご対応のほど、よろしくお願い申し上げます。

--------------------------------------------------
【AIカナサによる対話リポート】
{conversation_summary}
--------------------------------------------------

⚠️【相談者様へ：サポート企業様へ直接届く連絡先記入欄】
スムーズなご連絡をご希望の場合は、お手数ですが以下の【 】の中に
お名前やご連絡先をご記入の上、送信ボタンを押してください。
（※この情報は運営側には一切保存されず、{vendor['name']}様にのみ直接バトンタッチされます）

■ お名前：【 】
■ お電話番号：【 】
■ ご希望の連絡時間帯：【 】

--------------------------------------------------
※運営事務局確認用CC: {TAKESHI_ADMIN_EMAIL}
"""
                encoded_subject = urllib.parse.quote(mail_subject)
                encoded_body = urllib.parse.quote(mail_body)
                mailto_url = f"mailto:{vendor['email']}?cc={TAKESHI_ADMIN_EMAIL}&subject={encoded_subject}&body={encoded_body}"
                st.sidebar.page_link(mailto_url, label=f"📩 {vendor['name']}へバトンを繋ぐ", icon="✉️")
        else:
            st.sidebar.write("会話を進めると、あなたに最適なサポート企業がここに自動で表示されます。")
    except Exception as e:
        st.sidebar.write("カナサがニーズを分析中...")
elif not VENDORS:
    st.sidebar.write("現在、サポート企業リストを読み込み中です。")
