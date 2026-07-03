import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. Geminiの初期設定（ご自身のAPIキーに書き換えてください）
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)

# 2. AI（カナサ）の調律
SYSTEM_INSTRUCTION = """
あなたは、沖縄不動産無料相談窓口の公式AI「カナサ」です。沖縄の方言の「愛（かなさ）」と「AI」を掛け合わせて名付けられました。
沖縄の不動産や土地（軍用地含む）、相続、税金事情に日本一精通した、温厚で親身になって寄り添う「無料AI相談員」として振る舞ってください。

相談者は強引な営業や騙されること、そして親族間のトラブルに深く傷つき、不安を抱えています。あなたの目的は、相談者の不安を「愛（かなさ）」を持って優しく傾聴し、地元の心強いサポート企業（専門家）へ優しく橋渡し（バトンタッチ）をすることです。

以下の【絶対遵守ルール】と【沖縄不動産・独自知識データベース】を徹底的に読み込み、100%守って会話してください。

【絶対遵守ルール（法律の防衛線）】
1. 一人称は「不動産相談AIのカナサ」と名乗ってください。
2. 相談者のプライバシーを守るため、名前や電話番号、詳細な地番などは「絶対にこのチャットでは入力しないでくださいね」と最初に、あるいは自然に伝えてください。

3. 【★最重要：一般論の解説 ＋ 相談者の背中を押す現場感覚のアドバイス】
   相談者から税金や売却額の質問が出たら、一般的な数式や税率（長期譲渡約20%、短期譲渡約40%）を使って、大まかな概算（目安）を積極的に計算して提示してください。
   
   そして、数字を出した直後に、必ず以下の【経営者直伝の温かいアドバイス】をカナサの言葉（優しい口調）で伝えて、相談者の不安を和らげ、前向きな気持ちにさせてあげてください。

   【経営者直伝の温かいアドバイス】
   「実際に〇〇万円くらいかかりそう、と言われるとびっくりしますよね。普段の生活からすると本当にすごい出費に感じてしまうものです。
   でもね、一番大切なのは『最終的な手残り額』、つまり『自分がいくら手元に残したいか、いくらあれば何ができるか』という未来のワクワクするイメージをしてみることですよ。
   周りの人から『あのエリアだからこのくらいでしか売れないよ』とか『坪単価が低すぎるんじゃない？』なんて言われることもあるかもしれませんが、それは参考程度で大丈夫。誰のためでもない、あなた自身の『こうしたい』という考えを一番大切にしてくださいね！」

4. 【★重要：個別確定診断の禁止とサポート企業への橋渡し】
   上記のアドバイスで共感した後に、自然な流れで信頼できるプロへバトンを繋ぎます。
   「これはあくまで一般的な税率を当てはめた概算ですので、控除の特例を使ってさらに税金を減らすための細かい作戦や具体的なシミュレーションについては、カナサが太鼓判を押す地元の信頼できるサポート企業の先生たちと、細かい部分までとことん話し合ってみてくださいね。カナサがこれまでの相談内容をしっかり引き継いで、あなたとサポート企業との架け橋（バトンタッチ）をお手伝いしますよ」と優しく促してください。

【沖縄不動産・独自知識データベース】
■ 軍用地について
・売買の基準は「倍率」（年間借地料の何倍で取引されるか）。施設ごとに相場や将来の返還リスクが異なるため、知ったかぶりをせず地元の専門業者（サポート企業）への確認を促すこと。
■ 沖縄の相続と人間関係（門中・親族・トートーメー）について
・土地の名義人が戦前のままで、法定相続人が数十人に膨れ上がっているケースが非常に多い。
・AIは「沖縄の親族間の調整は、本当にエネルギーがいりますよね。まずは親族の中で一番話が通じるキーマンを特定し、登記や親族間調整のプロである地元の司法書士（サポート企業）に間に入ってもらうのが、実は一番揉めずに早く進む近道ですよ」と、沖縄の文化に寄り添ったアドバイスをすること。
"""

# 🏢 3. 業者（サポート企業）データの登録
VENDORS = [
    {"name": "那覇カチコミ司法書士事務所", "area": "那覇市", "type": "相続", "email": "test-legal@example.com", "pr": "戦前名義の複雑な相続登記、親族間の調整が得意です！"},
    {"name": "中部うちなー不動産", "area": "沖縄市", "type": "売買", "email": "test-estate@example.com", "pr": "軍用地（嘉手納・普天間）の売却・運用実績多数！高価買取します。"},
    {"name": "シーサー解体工業", "area": "宜野湾市", "type": "解体", "email": "test-demolition@example.com", "pr": "実家の中古住宅の解体、更地化を近隣対策バッチリで行います！"},
    {"name": "島んちゅ賃貸管理", "area": "浦添市", "type": "賃貸", "email": "test-rent@example.com", "pr": "移住者向けの物件紹介から、空き家の管理・賃貸運用までサポート！"}
]

TAKESHI_ADMIN_EMAIL = "takeshi-platform-admin@example.com"

# 🎨 4. デザインの設定
st.set_page_config(page_title="沖縄不動産無料相談窓口 カナサ", page_icon="🌴")

st.markdown("""
    <style>
    /* WIXに埋め込むため、背景を透明感のある白ベースに微調整 */
    .stApp { background-color: #FFFFFF; }
    [data-testid="stChatMessage"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span, [data-testid="stChatMessage"] div, [data-testid="stChatMessage"] a {
        color: #000000 !important;
    }
    .stChatInputContainer { border-radius: 20px; }
    .stChatInputContainer input { color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #FFF0D4; border-right: 3px solid #F28C28; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] h3 { color: #000000 !important; }
    
    /* 質問例ボタンのデザイン調整 */
    .stButton button {
        background-color: #FFFFFF !important;
        color: #005A9C !important;
        border: 1px solid #005A9C !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        width: 100% !important;
        min-height: 45px !important;
        margin-bottom: 5px !important;
    }
    .stButton button:hover {
        background-color: #005A9C !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# 💡 5. ヘッダー表示（WIX側でタイトルを作るため、AI側は空白（マージン）だけに徹底排除！）
st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)

# セッション状態の初期化
if "messages" not in st.session_state:
    # 💡 最初の案内文言も「バトンタッチ」「サポート企業」の優しい表現にブラッシュアップ
    welcome_text = """めんそーれ！不動産相談AIの「カナサ」です。🌴
あなたの大切な不動産や相続、税金などのモヤモヤしたお悩みを、愛（かなさ）を持って優しく紐解き、地元の頼れるサポート企業への安心な橋渡し（バトンタッチ）をお手伝いする窓口ですよ。

⚠️ **安心のためのお願い**
あなたのプライバシーを守るため、お名前や電話番号、詳しい住所などは**ここには絶対に入力しないで**、匿名で安心して相談してくださいね。

何から話していいか分からないときは、すぐ下のボタンを押すだけでも相談を始められますよ！👇"""
    st.session_state.messages = [{"role": "assistant", "content": welcome_text}]
    st.session_state.current_stage = "initial"

if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_INSTRUCTION)
    st.session_state.chat = model.start_chat(history=[])

# 過去の会話履歴を画面に表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 💡 6. 進捗に応じた「連動型」質問例ボタン
st.write("▼ 当てはまるボタンを押すか、下の入力欄からメッセージを送ってね")
col1, col2, col3 = st.columns(3)
click_input = None

if st.session_state.current_stage == "initial":
    with col1:
        if st.button("💡 相続が何からか分からない"):
            click_input = "相続が発生したけれど、何からしたらいいか分からないさぁ"
            st.session_state.current_stage = "souzoku"
    with col2:
        if st.button("🔰 軍用地の仕組みを知りたい"):
            click_input = "軍用地を相続したけれど、仕組みが全然分からない"
            st.session_state.current_stage = "gunyou"
    with col3:
        if st.button("🏚️ 古い実家を処分・解体したい"):
            click_input = "古い実家を処分したいけれど、解体費用ってどのくらい？"
            st.session_state.current_stage = "kaitai"

elif st.session_state.current_stage == "souzoku":
    with col1:
        if st.button("👨‍👩‍👧‍👦 相続人が何人いるか確認したい"):
            click_input = "相続の手続きをするにあたって、法定相続人が何人いるかを確認する数式や仕組みを教えて"
    with col2:
        if st.button("💰 相続税がいくらかかるか不安"):
            click_input = "相続税の計算の仕組みや、基礎控除額がいくらになるのか目安を教えてほしいさぁ"
    with col3:
        if st.button("↩️ 最初の質問に戻る"):
            st.session_state.current_stage = "initial"
            st.rerun()

elif st.session_state.current_stage == "gunyou":
    with col1:
        if st.button("📈 倍率や相場の調べ方を知りたい"):
            click_input = "軍用地の価値を決める『倍率』って何？どうやって相場を調べたらいいか教えて"
    with col2:
        if st.button("⏳ 将来の返還リスクが心配"):
            click_input = "軍用地って将来国から返還されたらどうなるの？リスクについて教えて"
    with col3:
        if st.button("↩️ 最初の質問に戻る"):
            st.session_state.current_stage = "initial"
            st.rerun()

elif st.session_state.current_stage == "kaitai":
    with col1:
        if st.button("💸 解体にかかる大まかな坪単価"):
            click_input = "沖縄で木造やRC（鉄筋コンクリート）の実家を解体する場合、大まかな坪単価の目安ってどのくらい？"
    with col2:
        if st.button("🤝 解体後に売るか貸すか迷う"):
            click_input = "古い家を解体して更地にした後、売却するのと賃貸で運用するの、どっちが手残り多くなるかな？"
    with col3:
        if st.button("↩️ 最初の質問に戻る"):
            st.session_state.current_stage = "initial"
            st.rerun()

# ユーザーからの入力処理
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

# ---- 💡 自動業者仕分け ＆ メールテンプレート連携システム ----
st.sidebar.markdown("### 🤝 カナサ厳選のサポート企業")
st.sidebar.write("これまでの相談内容を引き継いで、地元の信頼できるプロの先生方に安全に直接問い合わせができます。")

conversation_summary = ""
for m in st.session_state.messages[1:]:
    role_name = "相談者" if m["role"] == "user" else "AIカナサ"
    conversation_summary += f"{role_name}: {m['content']}\n"

if conversation_summary:
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
