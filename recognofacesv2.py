import streamlit as st
import pandas as pd
import openai

# Configuração da chave da API (requer secrets.toml)
openai.api_key = st.secrets["openai"]["api_key"]

# Página e layout
st.set_page_config(
    page_title="RecognoFaces",
    page_icon="😃",
    layout="wide"
)

# Tabs para análise e chatbot
aba = st.sidebar.radio("Escolha a aba", ["📊 Análise de Desempenho", "💬 Chat com GPT"])

# =========================================================
# === ABA 1: Análise de desempenho no reconhecimento facial
# =========================================================
if aba == "📊 Análise de Desempenho":
    s1, s2 = st.columns([0.2, 1])

    with s1:
        st.image('icon.png')
    with s2:
        st.markdown("""
            <div style="background-color:#f0f2f6;padding:10px;border-radius:10px;margin-bottom:20px">
                <h1 style="color:#262730;">Análise de Reconhecimento de Expressões Faciais</h1>
                <p style="color:#404040;font-size:16px">
                    Esta página analisa o desempenho em tarefas de reconhecimento de expressões faciais usando o aplicativo <strong>RecognoFaces</strong>.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Dados via URL ou arquivo
    try:
        vp_qs = int(st.query_params["vp"])
        vn_qs = int(st.query_params["vn"])
        fp_qs = int(st.query_params["fp"])
        fn_qs = int(st.query_params["fn"])
    except:
        vp_qs = vn_qs = fp_qs = fn_qs = 0

    st.header("1. Importar dados do teste:")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])

    if vp_qs + vn_qs + fp_qs + fn_qs > 0:
        st.success("✅ Dados recebidos automaticamente via link!")
        vp, vn, fp, fn = vp_qs, vn_qs, fp_qs, fn_qs

    elif uploaded_file:
        df = pd.read_csv(uploaded_file)
        categorias = df['Categoria'].value_counts()
        vp = categorias.get("VP", 0)
        vn = categorias.get("VN", 0)
        fp = categorias.get("FP", 0)
        fn = categorias.get("FN", 0)
        st.dataframe(df)
    else:
        st.info("Aguardando dados via link ou arquivo.")
        st.stop()

    total = vp + vn + fp + fn
    acuracia = (vp + vn) / total if total > 0 else 0.0
    precisao = vp / (vp + fp) if (vp + fp) > 0 else 0.0
    recall = vp / (vp + fn) if (vp + fn) > 0 else 0.0
    f1 = 2 * (precisao * recall) / (precisao + recall) if (precisao + recall) > 0 else 0.0

    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("2. Totais extraídos")
        st.write(f"- VP: {vp}")
        st.write(f"- VN: {vn}")
        st.write(f"- FP: {fp}")
        st.write(f"- FN: {fn}")

    with c2:
        st.subheader("3. Resultados das métricas")
        st.markdown(f"**Acurácia**: `{acuracia:.3f}`")
        st.markdown(f"**Precisão**: `{precisao:.3f}`")
        st.markdown(f"**Recall (Sensibilidade)**: `{recall:.3f}`")
        st.markdown(f"**F1-score**: `{f1:.3f}`")

    with c3:
        st.subheader("4. Conceitos")
        st.image('acuracia.png', width=160)
        st.image('precisao.png', width=150)
        st.image('recall.png', width=150)
        st.image('f1score.png', width=150)

# ==============================
# === ABA 2: Chat com o GPT ====
# ==============================
elif aba == "💬 Chat com GPT":
    st.title("💬 Chat com o GPT")
    st.info("Converse com o modelo sobre qualquer tema ou peça ajuda com análise de resultados.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "assistant", "content": "Olá! Como posso ajudar hoje?"}]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Digite sua pergunta...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=st.session_state.chat_history
                    )
                    reply = response.choices[0].message["content"]
                except Exception as e:
                    reply = f"Erro: {e}"

            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
