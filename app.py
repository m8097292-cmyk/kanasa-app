import streamlit as st
import google.generativeai as genai
import urllib.parse
import csv
import os

# 1. Geminiの初期設定（ご自身のAPIキーに書き換えてください）
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)

# 📂 外部ファイルからプロンプトを読み込む
def load_prompt():
    if os.path.exists("prompt.txt"):
        with open("prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "あなたは優秀なAIアシスタントです。"

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
        # 💡 テスト用（csvがない場合の保険。image_url列を追加しています）
        vendors = [
            {"name": "那覇カチコミ司法書士事務所", "area": "那覇市", "type": "相続", "email": "test-legal@example.com", "pr": "戦前名義の複雑な相続登記、親族間の調整が得意です！", "image_url": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=150"},
            {"name": "中部うちなー不動産", "area": "沖縄市", "type": "売買", "email": "test-estate@example.com", "pr": "軍用地の売却・運用実績多数！高価買取します。", "image_url": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=150"},
            {"name": "シーサー解体工業", "area": "宜野湾市", "type": "解体", "email": "test-demolition@example.com", "pr": "実家の中古住宅の解体を近隣対策バッチリで行います！", "image_url": "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=150"}
        ]
    return vendors

VENDORS = load_vendors()
TAKESHI_ADMIN_EMAIL = "takeshi-platform-admin@example.com"

# 🎨 2. デザインの設定（見切れ対策版・メイン画面集中型）
st.set_page_config(page_title="沖縄不動産無料相談窓口 カナサ", page_icon="🌴", layout="wide")

# 🎨 デザインCSSの st.markdown 内に以下を追加（文字を中央揃えにしたり、WIXの雰囲気を再現）
st.markdown("""
    <style>
    /* （既存のCSSコードはそのまま残し、以下を追記してください） */
    .main-title-container {
        text-align: center;
        padding: 20px 10px;
        background: linear-gradient(135px, #FFF5F5 0%, #FFEAEE 100%);
        border-radius: 16px;
        margin-bottom: 25px;
        border: 1px solid #FFE0E6;
    }
    .main-logo {
        font-size: 54px !important;
        font-weight: bold;
        color: #333333;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        letter-spacing: 2px;
        margin: 10px 0;
    }
    .sub-text {
        color: #FFD700 !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        margin-bottom: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)


# 🛠️ 以前の st.title や st.subheader があった部分を、以下に丸ごと差し替え
st.markdown("""
    <div class="main-title-container">
        <p style="color: #666; font-size: 14px; font-weight: bold; margin: 0;">沖縄の匿名で安心 🌴 不動産・相続相談窓口</p>
        <div class="main-logo">KANASA</div>
        <p style="color: #FF5A76; font-size: 15px; font-weight: bold; margin: 5px 0 15px 0;">〜 沖縄AI（カナサ）が、あなたの悩みに寄り添いサポートします 〜</p>
        <p class="sub-text">名前や住所の入力は不要</p>
        <p class="sub-text">後からしつこい営業電話が鳴り響く心配は一切ありません</p>
        <p class="sub-text"><b>愛（かなさ）</b>を込めて、あなたと地元の優良サポート企業を繋ぐパートナー</p>
        <p class="sub-text">複雑なお悩みはAIカナサにすべてお任せください</p>
        <p class="sub-text">あなたの想いに寄り添いながら、次の確かなステップへと優しくバトンタッチいたします。</p>
    </div>
""", unsafe_allow_html=True)

# セッション状態の初期化
if "messages" not in st.session_state:
    welcome_text = """    めんそーれ！AI相談員の「カナサ」です。🌴
    不動産や相続のモヤモヤを優しく紐解き、地元の安心なサポート企業へそっとバトンをお繋ぎします。

    ⚠️ **安心のためのお願い**
    名前や電話番号は**ここには入力せず**、匿名で安心して相談してくださいね。
    すぐ下のボタンを押すだけで相談を始められますよ！👇"""
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
    # 💡 無限ループ防止のため st.rerun() はここから削除しました

# --------------------------------------------------
# 💡【大進化】チャットルーム内・ボタン起動型マッチング
# --------------------------------------------------
st.write("---")
st.write("### 🤝 相談がひと段落したら")

# 会話履歴の集計（最初のウェルカムメッセージは除外）
conversation_summary = ""
for m in st.session_state.messages[1:]:
    role_name = "相談者" if m["role"] == "user" else "AIカナサ"
    conversation_summary += f"{role_name}: {m['content']}\n"

# 会話が1往復以上あったら、メイン画面にデカデカと診断ボタンを表示
if conversation_summary and VENDORS:
    st.markdown('<div class="diagnose-btn">', unsafe_allow_html=True)
    diagnose_clicked = st.button("🎁 あなたにピッタリの地元のサポート企業を診断する")
    st.markdown('</div>', unsafe_allow_html=True)

    if diagnose_clicked:
        with st.spinner("カナサがこれまでの内容から最適なプロを厳選中..."):
            judge_model = genai.GenerativeModel('gemini-2.5-flash')
            judge_prompt = f"以下の相談内容を読み、この相談者が最も求めている専門家のカテゴリを【相続、売買、解体、賃貸】の中から漢字またはカタカナで1つだけ答えてください。\n\n相談内容：\n{conversation_summary}"
            
            try:
                detected_type = judge_model.generate_content(judge_prompt).text.strip()
                matched_vendors = [v for v in VENDORS if v["type"] in detected_type]
                
                if matched_vendors:
                    st.success(f"🎉 あなたの相談タイプ【{detected_type}】に最適な企業が見つかりました！")
                    
                    for vendor in matched_vendors:
                        # 📦 画面中央にリッチなカード形式で業者を表示（写真付き）
                        st.markdown(f"""
                        <div class="vendor-card">
                            <table style="width:100%; border:none; background:none;">
                                <tr>
                                    <td style="width:160px; vertical-align:top; border:none;">
                                        <img src="{vendor.get('image_url', 'https://via.placeholder.com/150')}" style="width:150px; border-radius:8px; object-fit:cover;">
                                    </td>
                                    <td style="vertical-align:top; border:none; padding-left:15px;">
                                        <h4 style="color:#005A9C; margin:0 0 8px 0;">🏢 {vendor['name']}</h4>
                                        <p style="margin:0 0 5px 0; font-size:13px; color:#555;">🎯 <b>専門分野:</b> {vendor['type']}</p>
                                        <p style="margin:0; font-size:14px; color:#333;">📢 {vendor['pr']}</p>
                                    </td>
                                </tr>
                            </table>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # メール送信リンク
                        mail_subject = f"【AIカナサ窓口経由】新規ご相談（カテゴリ：{vendor['type']}）"
                        mail_body = f"{vendor['name']} 御中\n\n「沖縄不動産無料相談窓口 カナサ」より引き継ぎです。\n\n【対話リポート】\n{conversation_summary}\n\n■ お名前：【 】\n■ お電話番号：【 】\n※確認用CC: {TAKESHI_ADMIN_EMAIL}"
                        
                        encoded_subject = urllib.parse.quote(mail_subject)
                        encoded_body = urllib.parse.quote(mail_body)
                        mailto_url = f"mailto:{vendor['email']}?cc={TAKESHI_ADMIN_EMAIL}&subject={encoded_subject}&body={encoded_body}"
                        
                        st.page_link(mailto_url, label=f"👉 {vendor['name']}にこの内容で無料相談のバトンを繋ぐ", icon="✉️")
                else:
                    st.warning("現在、該当するカテゴリのサポート企業が準備中です。そのままカナサにご相談を続けてください。")
            except Exception as e:
                st.error("診断中にエラーが発生しました。もう一度お試しください。")
