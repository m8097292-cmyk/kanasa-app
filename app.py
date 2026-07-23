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
        border: 1.5px solid #005A9C !important; 
        border-radius: 10px !important; 
        font-size: clamp(11px, 2.8vw, 13px) !important; 
        font-weight: bold !important;
        width: 100% !important; 
        min-height: 48px !important; 
        padding: 6px 8px !important; 
        margin-bottom: 6px !important; 
        line-height: 1.3 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
        <div class="main-logo">Okisapo+</div>
        <p class="catch-phrase">〜 おきサポプラス 〜</p>
        <p class="catch-phrase">不動産の分からないをサポート</p>
        <p class="sub-text">匿名で安心🌞名前や住所の入力不要</p>
        <p class="sub-text">営業電話は一切なし</p>
        <p class="sub-text">あなたと地元のサポート企業を繋ぐパートナー</p>
        <p class="sub-text">お悩みはAIカナサに気軽に相談</p>
    </div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 🎯 ボタンツリー管理構造（編集しやすく整理したエリア）
# --------------------------------------------------
BUTTON_STAGES = {
    # 🏠【初期画面】最初に表示されるボタン一覧（自由に追加できます）
    "initial": [
        {"label": "💡 相続が発生した（何からすべき？）", "query": "相続が発生したけれど、何からしたらいいか分からないさぁ", "next_stage": "souzoku"},
        {"label": "🔰 軍用地の仕組み・売買について", "query": "軍用地を相続したけれど、仕組みや相場が全然分からないさぁ", "next_stage": "gunyou"},
        {"label": "🏚️ 古い実家の解体・活用費用", "query": "古い実家を処分したいけれど、解体費用ってどのくらい？", "next_stage": "kaitai"},
        {"label": "📜 登記・名義変更の手続き", "query": "不動産や土地の名義変更（登記）の手続き方法を知りたいさぁ", "next_stage": "touki"},
        {"label": "💰 土地・建物の売却手順と相場", "query": "土地や建物を売却する手順や高く売るための注意点を教えて", "next_stage": "baikyaku"},
        {"label": "🚜 農地・山林の活用や権利調整", "query": "複雑な農地や山林、放置された土地の使い道について相談したい", "next_stage": "nouchi"},
    ],

    # 👨‍👩‍👧【相続】を押した後の深掘り質問ボタン
    "souzoku": [
        {"label": "👨‍👩‍👧‍👦 相続人の確認方法", "query": "相続の手続きをするにあたって、法定相続人が何人いるかを確認する仕組みを教えて", "next_stage": "souzoku"},
        {"label": "💰 相続税の不安・基礎控除", "query": "相続税の計算の仕組みや、基礎控除額がいくらになるのか目安を教えてほしいさぁ", "next_stage": "souzoku"},
        {"label": "📄 遺産分割協議書の進め方", "query": "遺産分割協議書は誰とどのように作成すれば良いですか？", "next_stage": "souzoku"},
        {"label": "↩️ 最初のメニューに戻る", "query": None, "next_stage": "initial"},
    ],

    # 🎖️【軍用地】を押した後の深掘り質問ボタン
    "gunyou": [
        {"label": "📈 相場の調べ方（倍率とは？）", "query": "軍用地の価値を決める『倍率』って何？どうやって相場を調べたらいいか教えて", "next_stage": "gunyou"},
        {"label": "⏳ 将来の返還リスク", "query": "軍用地って将来国から返還されたらどうなるの？リスクについて教えて", "next_stage": "gunyou"},
        {"label": "💵 借地料（年間分配金）の仕組み", "query": "軍用地の借地料はどのように振り込まれ、増額される仕組みですか？", "next_stage": "gunyou"},
        {"label": "↩️ 最初のメニューに戻る", "query": None, "next_stage": "initial"},
    ],

    # 🏚️【解体】を押した後の深掘り質問ボタン
    "kaitai": [
        {"label": "💸 解体の坪単価相場（沖縄）", "query": "沖縄で木造やRCの実家を解体する場合、大まかな坪単価の目安ってどのくらい？", "next_stage": "kaitai"},
        {"label": "🤝 売るか貸すか（更地 vs 古家付き）", "query": "古い家を解体して更地にした後、売却するのと賃貸で運用するの、どっちがいいかな？", "next_stage": "kaitai"},
        {"label": "🗑️ 残置物・家具の処分方法", "query": "実家の中にある大量の不用品や仏壇の処分はどう手配すれば良いですか？", "next_stage": "kaitai"},
        {"label": "↩️ 最初のメニューに戻る", "query": None, "next_stage": "initial"},
    ],

    # 📜【登記】を押した後の深掘り質問ボタン
    "touki": [
        {"label": "⏳ 相続登記の義務化について", "query": "相続登記の義務化の期限や、放置した場合の罰則について教えて", "next_stage": "touki"},
        {"label": "📝 自分でできる？費用はどのくらい？", "query": "自分で登記申請する場合と、司法書士に頼む場合の費用相場を比較したい", "next_stage": "touki"},
        {"label": "↩️ 最初のメニューに戻る", "query": None, "next_stage": "initial"},
    ],

    # 💰【売却】を押した後の深掘り質問ボタン
    "baikyaku": [
        {"label": "🔍 良い不動産会社の選び方", "query": "地元の信頼できる不動産会社を見分けるポイントを教えて", "next_stage": "baikyaku"},
        {"label": "💸 仲介手数料や税金の計算方法", "query": "不動産を売却したときにかかる費用（税金・手数料）の目安は？", "next_stage": "baikyaku"},
        {"label": "↩️ 最初のメニューに戻る", "query": None, "next_stage": "initial"},
    ],

    # 🚜【農地】を押した後の深掘り質問ボタン
    "nouchi": [
        {"label": "🌾 農業委員会への「農地転用」申請", "query": "農地を駐車場や住宅地に変更する手続きの流れを教えて", "next_stage": "nouchi"},
        {"label": "🤝 地権者との共同開発パートナーシップ", "query": "権利関係が複雑な土地や山林をバリューアップして売却する相談", "next_stage": "nouchi"},
        {"label": "↩️ 最初のメニューに戻る", "query": None, "next_stage": "initial"},
    ],
}

# セッション状態の初期化
if "messages" not in st.session_state:
    welcome_text = """めんそーれ！AI相談員の「カナサ」です。  
不動産や相続でお悩みを無料サポート！

⚠️ **安心のためのお願い** ⚠️  
名前や電話番号は**チャット内に入力不要** 匿名で安心してご相談してください！"""
    st.session_state.messages = [{"role": "assistant", "content": welcome_text}]
    st.session_state.current_stage = "initial"

if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
    st.session_state.chat = model.start_chat(history=[])

# チャット履歴の表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --------------------------------------------------
# 🔘 動的質問ボタン表示エリア（2列レスポンシブ配置）
# --------------------------------------------------
st.markdown("""
    <p style="
        color: #000000; 
        font-weight: bold; 
        font-size: clamp(12px, 3.2vw, 15px); 
        margin-top: 15px;
        margin-bottom: 8px; 
        white-space: nowrap; 
        overflow: hidden; 
        text-overflow: ellipsis;
    ">
        ▼ 当てはまるボタンを押すか、下の入力欄からメッセージを入力
    </p>
""", unsafe_allow_html=True)

click_input = None
current_buttons = BUTTON_STAGES.get(st.session_state.current_stage, BUTTON_STAGES["initial"])

# スマホ・PCで2列にボタンを綺麗に配置
cols = st.columns(2)
for idx, btn_info in enumerate(current_buttons):
    col = cols[idx % 2]
    with col:
        if st.button(btn_info["label"], key=f"btn_{st.session_state.current_stage}_{idx}"):
            if btn_info["query"]:
                click_input = btn_info["query"]
            st.session_state.current_stage = btn_info["next_stage"]
            if not btn_info["query"]:  # 「戻る」ボタンが押された時
                st.rerun()

user_input = st.chat_input("お気軽にカナサにご相談ください...")
final_input = user_input if user_input else click_input

# --------------------------------------------------
# メッセージ送信時 & 業者自動マッチング処理
# --------------------------------------------------
if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        # 1. AIからの回答を取得
        response = st.session_state.chat.send_message(final_input)
        ai_reply = response.text
        
        # 2. 相談内容に合わせてマッチする業者を自動選出する処理
        matched_vendors_html = ""
        for vendor in VENDORS:
            if (vendor["type"] in final_input) or (vendor["type"] in ai_reply) or \
               (st.session_state.current_stage == "souzoku" and vendor["type"] == "相続") or \
               (st.session_state.current_stage == "kaitai" and vendor["type"] == "解体") or \
               (st.session_state.current_stage in ["gunyou", "baikyaku"] and vendor["type"] == "売買"):
                
                # メール問い合わせ用のURLを作成
                subject = urllib.parse.quote(f"【Okisapo+】{vendor['name']}様への相談")
                body = urllib.parse.quote(f"相談内容：\n{final_input}\n\nご回答よろしくお願いします。")
                mailto_link = f"mailto:{vendor['email']}?cc={TAKESHI_ADMIN_EMAIL}&subject={subject}&body={body}"
                
                # 業者カードのHTMLを作成
                matched_vendors_html += f"""
                <div class="vendor-card">
                    <img src="{vendor['image_url']}" class="vendor-img">
                    <div class="vendor-info">
                        <h4 style="margin:0 0 5px 0; color:#333;">🤝 {vendor['name']}（{vendor['area']}）</h4>
                        <p style="margin:0 0 8px 0; font-size:13px; color:#555;">{vendor['pr']}</p>
                        <a href="{mailto_link}" target="_blank" style="
                            display: inline-block;
                            background-color: #FF8C00;
                            color: white !important;
                            padding: 8px 16px;
                            border-radius: 20px;
                            text-decoration: none;
                            font-weight: bold;
                            font-size: 13px;
                        ">✉️ この企業に匿名相談・見積もり</a>
                    </div>
                </div>
                """

        # 3. AIの回答テキストを表示
        st.markdown(ai_reply, unsafe_allow_html=True)
        
        # 4. マッチした業者があれば、回答の下に業者カードを表示！
        if matched_vendors_html:
            st.markdown("### 💡 このお悩みをサポートできる地元の専門企業")
            st.markdown(matched_vendors_html, unsafe_allow_html=True)
            ai_reply += "\n\n### 💡 このお悩みをサポートできる地元の専門企業\n" + matched_vendors_html

    # セッション履歴に保存して画面更新
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.rerun()

# --------------------------------------------------
# フッターエリア
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
