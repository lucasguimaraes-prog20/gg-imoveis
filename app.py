import base64
import hashlib
import json
import os
import re
import streamlit as st


def hash_senha(senha: str) -> str:
    """Gera o hash SHA-256 de uma senha para não gravá-la em texto puro."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

# --- CONFIGURAÇÃO DE CAMINHOS ---
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_BANCO_CLIENTES = os.path.join(DIRETORIO_ATUAL, "banco_clientes.json")

CAMINHO_LOGO = os.path.join(DIRETORIO_ATUAL, "logo.png")
LOGO_EXISTE = os.path.exists(CAMINHO_LOGO)
if not LOGO_EXISTE:
    CAMINHO_LOGO = "logo.png"
    LOGO_EXISTE = True

URL_SIDEBAR = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400&q=80"

URL_BANNER = "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=1200&q=80"

URL_BOSQUE = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600&q=80"
URL_PALMEIRAS = "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=600&q=80"
URL_VISTA = "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=600&q=80"


# --- PERSISTÊNCIA DE DADOS EM ARQUIVO LOCAL (JSON) ---
def carregar_clientes_disco():
    if os.path.exists(ARQUIVO_BANCO_CLIENTES):
        try:
            with open(ARQUIVO_BANCO_CLIENTES, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "12345678900": {
            "cpf": "12345678900",
            "nome": "Cliente Exemplo",
            "email": "cliente@email.com",
            "telefone": "(82) 99999-9999",
            "nascimento": "1990-01-01",
            "renda": 3000.0,
            "senha": hash_senha("Senha@123")
        }
    }

def salvar_cliente_disco(cpf, dados_cliente):
    clientes = carregar_clientes_disco()
    clientes[cpf] = dados_cliente
    with open(ARQUIVO_BANCO_CLIENTES, "w", encoding="utf-8") as f:
        json.dump(clientes, f, ensure_ascii=False, indent=4)
    st.session_state["banco_clientes"] = clientes


@st.cache_data
def get_image_base64(path):
    if path and os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
    return ""


def validar_senha(senha: str) -> bool:
    if len(senha) < 6:
        return False
    tem_maiuscula = bool(re.search(r"[A-Z]", senha))
    tem_especial = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", senha))
    return tem_maiuscula and tem_especial


# --- BANCOS DE DADOS NA MEMÓRIA E DISCO ---
if "banco_clientes" not in st.session_state:
    st.session_state["banco_clientes"] = carregar_clientes_disco()

if "banco_corretores" not in st.session_state:
    st.session_state["banco_corretores"] = {}

if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

if "imovel_selecionado" not in st.session_state:
    st.session_state["imovel_selecionado"] = None

if "etapa_fluxo" not in st.session_state:
    st.session_state["etapa_fluxo"] = "login"

IMOVEIS_OPCOES = {
    "Residencial Bosque Imperial - R$ 350.000,00": 350000.0,
    "Condomínio Jardim das Palmeiras - R$ 220.000,00": 220000.0,
    "Residencial Vista Verde - R$ 185.000,00": 185000.0,
}

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="G&G Imóveis",
    layout="wide",
)

sidebar_bg_base64 = URL_SIDEBAR
eh_tela_inicial = st.session_state["etapa_fluxo"] in ["login", "cadastro_inicial"]

if eh_tela_inicial:
    bg_app = "#0E1726"
    text_color = "#FFFFFF"
    card_bg = "#1A2638"
    card_border = "1px solid #2D3748"
    sub_color = "#A0AEC0"
    btn_bg = "#2B6CB0"
    btn_hover = "#3182CE"
    btn_text_color = "#FFFFFF"
    disabled_text_color = "#FFFFFF"
else:
    bg_app = "#F8F9FA"
    text_color = "#0E1D2F"
    card_bg = "#FFFFFF"
    card_border = "none"
    sub_color = "#556070"
    btn_bg = "#FF9F1C"
    btn_hover = "#FF8800"
    btn_text_color = "#FFFFFF"
    disabled_text_color = "#000000"

st.markdown(
    f"""
    <style>
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
        }}

        .stApp {{
            background-color: {bg_app} !important;
            color: {text_color} !important;
        }}
        
        h1 {{
            margin-bottom: 0.5rem !important;
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            color: {text_color} !important;
        }}

        h3 {{
            margin-top: 1.5rem !important;
            margin-bottom: 1rem !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: {text_color} !important;
        }}

        h2, h4, h5, h6, p, span, label {{
            color: {text_color} !important;
        }}
        
        .subtitulo-cinza {{
            color: {sub_color} !important;
            margin-bottom: 0.3rem !important;
        }}

        [data-testid="stSidebar"] {{
            display: {"none" if eh_tela_inicial else "block"} !important;
            background-image: url("{sidebar_bg_base64}");
            background-size: cover !important;
            background-position: top center !important;
            background-repeat: no-repeat !important;
            min-width: 320px !important;
            max-width: 320px !important;
        }}
        
        [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
        }}

        /* Card Original do Print */
        .card-imovel {{
            background-color: {card_bg} !important;
            padding: 16px;
            border-radius: 12px;
            border: {card_border};
            box-shadow: {"0px 4px 12px rgba(0, 0, 0, 0.05)" if not eh_tela_inicial else "none"};
        }}

        input {{
            background-color: {"#263345" if eh_tela_inicial else "#FFFFFF"} !important;
            color: {text_color} !important;
            border: 1px solid {"#4A5568" if eh_tela_inicial else "#CED4DA"} !important;
            border-radius: 6px !important;
        }}
        
        input:disabled {{
            color: {disabled_text_color} !important;
            -webkit-text-fill-color: {disabled_text_color} !important;
            font-weight: 600 !important;
            opacity: 1 !important;
            background-color: {"#1A2638" if eh_tela_inicial else "#E9ECEF"} !important;
        }}
        
        input::placeholder {{
            color: {sub_color} !important;
        }}

        .stButton>button, 
        button[data-testid="stFormSubmitButton"], 
        div[data-testid="stFormSubmitButton"] > button {{
            background-color: {btn_bg} !important;
            color: {btn_text_color} !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: bold !important;
            font-size: 1rem !important;
            padding: 10px 16px !important;
            opacity: 1 !important;
            box-shadow: 0px 3px 6px rgba(0,0,0,0.1) !important;
        }}
        
        .stButton>button:hover, 
        button[data-testid="stFormSubmitButton"]:hover, 
        div[data-testid="stFormSubmitButton"] > button:hover {{
            background-color: {btn_hover} !important;
            color: #FFFFFF !important;
        }}

        button[data-testid="stFormSubmitButton"] p {{
            color: #FFFFFF !important;
            font-weight: bold !important;
        }}

        div[data-testid="stFormSubmitHelp"] {{
            display: none !important;
        }}

        .stFormSubmitButton + p {{
            display: none !important;
        }}

        div[data-baseweb="form"]::after {{
            content: "Pressione Enter para enviar" !important;
            display: block !important;
            color: {sub_color} !important;
            font-size: 0.8rem !important;
            text-align: right !important;
            margin-top: 4px !important;
        }}

        small, .stMarkdown small {{
            display: none !important;
        }}

        [data-testid="stForm"] small {{
            display: none !important;
        }}

        [data-testid="stForm"] p:last-child {{
            display: none !important;
        }}

        [data-testid="stFormSubmitHelp"] p {{
            display: none !important;
        }}

        div[data-testid="stForm"] > div:last-child > div:last-child {{
            display: none !important;
        }}

        p:has(> span[style]) {{
            display: none !important;
        }}

        .stForm [data-testid="stMarkdownContainer"] p {{
            font-size: 0px !important;
        }}

        .stForm [data-testid="stMarkdownContainer"] p::after {{
            content: "Pressione Enter para enviar" !important;
            font-size: 0.8rem !important;
            color: {sub_color} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <script>
        function traduzirForm() {
            var allElements = document.querySelectorAll('span, p, small, div');
            for (var i = 0; i < allElements.length; i++) {
                var el = allElements[i];
                if (el.textContent.includes('Press Enter to submit form')) {
                    el.textContent = el.textContent.replace('Press Enter to submit form', 'Pressione Enter para enviar');
                }
                if (el.textContent.includes('Press Enter')) {
                    el.textContent = el.textContent.replace('Press Enter', 'Pressione Enter');
                }
                if (el.textContent.includes('Submit form')) {
                    el.textContent = el.textContent.replace('Submit form', 'Enviar');
                }
            }
        }
        traduzirForm();
        setTimeout(traduzirForm, 1000);
        setTimeout(traduzirForm, 3000);
        setTimeout(traduzirForm, 5000);
        setInterval(traduzirForm, 2000);
    </script>
    """,
    unsafe_allow_html=True,
)

if not eh_tela_inicial:
    with st.sidebar:
        if LOGO_EXISTE:
            st.image(CAMINHO_LOGO, use_container_width=True)
        st.markdown("<div style='height: 160px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Sair da Conta", key="btn_logout", use_container_width=True):
            st.session_state["usuario_logado"] = None
            st.session_state["imovel_selecionado"] = None
            st.session_state["etapa_fluxo"] = "login"
            st.rerun()

# --- 2. TELA INICIAL: LOGIN ---
if st.session_state["etapa_fluxo"] == "login":
    st.session_state["banco_clientes"] = carregar_clientes_disco()
    
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if LOGO_EXISTE:
            img_col1, img_col2, img_col3 = st.columns([1, 1, 1])
            with img_col2:
                st.image(CAMINHO_LOGO, use_container_width=True)

        st.markdown(
            "<h2 style='text-align: center;'>Acesso ao Sistema</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p class='subtitulo-cinza' style='text-align: center; margin-bottom: 1.5rem;'>Entre com seus dados para acessar o painel</p>",
            unsafe_allow_html=True,
        )

        with st.form("form_login"):
            cpf = st.text_input("CPF do Cliente", placeholder="Digite apenas os 11 números do seu CPF", key="login_cpf")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha", key="login_senha")

            submit_login = st.form_submit_button("Entrar", use_container_width=True)

        esq_col1, esq_col2 = st.columns([2, 1])
        with esq_col2:
            if st.button("Esqueceu a senha?", key="btn_esqueci_senha"):
                st.session_state["etapa_fluxo"] = "recuperar_senha"
                st.rerun()

        if st.button("Preciso de Ajuda", key="btn_ajuda_login"):
            st.info("Use seu CPF (11 dígitos) e a senha cadastrada para acessar. Se esqueceu a senha, clique em 'Esqueceu a senha?'.")

        if submit_login:
            cpf_limpo = re.sub(r"\D", "", cpf)

            if not cpf_limpo or len(cpf_limpo) != 11:
                st.error("Acesso permitido apenas via CPF! Digite um CPF válido com 11 números.")
            elif cpf_limpo in st.session_state["banco_clientes"]:
                usuario = st.session_state["banco_clientes"][cpf_limpo]
                if usuario["senha"] == hash_senha(senha):
                    st.session_state["usuario_logado"] = cpf_limpo
                    st.session_state["etapa_fluxo"] = "painel_geral"
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
            else:
                st.error("CPF não cadastrado no sistema!")

        st.divider()

        st.markdown("<p style='text-align: center;'>Não possui conta?</p>", unsafe_allow_html=True)

        btn_cad_col1, btn_cad_col2, btn_cad_col3 = st.columns([1, 2, 1])
        with btn_cad_col2:
            if st.button("Criar Minha Conta", use_container_width=True):
                st.session_state["etapa_fluxo"] = "cadastro_inicial"
                st.rerun()

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        st.markdown("<p style='text-align: center; font-size: 0.85rem;'>Ou acesse como visitante</p>", unsafe_allow_html=True)
        btn_vis_col1, btn_vis_col2, btn_vis_col3 = st.columns([1, 2, 1])
        with btn_vis_col2:
            if st.button("Entrar como Visitante", use_container_width=True):
                st.session_state["etapa_fluxo"] = "painel_geral"
                st.rerun()

# --- 3. TELA DE CADASTRO INICIAL DO CLIENTE ---
elif st.session_state["etapa_fluxo"] == "cadastro_inicial":
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if LOGO_EXISTE:
            img_col1, img_col2, img_col3 = st.columns([1, 1, 1])
            with img_col2:
                st.image(CAMINHO_LOGO, use_container_width=True)

        st.markdown(
            "<h2 style='text-align: center;'>Cadastro de Novo Cliente</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p class='subtitulo-cinza' style='text-align: center; margin-bottom: 1.5rem;'>Preencha seus dados para criar sua conta</p>",
            unsafe_allow_html=True,
        )

        with st.form("form_cadastro"):
            nome = st.text_input("Nome Completo", placeholder="Ex: João da Silva")
            cpf = st.text_input("CPF", placeholder="Apenas os 11 números do CPF")
            email = st.text_input("E-mail", placeholder="seuemail@exemplo.com")

            senha = st.text_input("Senha", type="password", placeholder="Crie uma senha")
            confirmar_senha = st.text_input("Confirmar Senha", type="password", placeholder="Repita a senha")

            st.caption("Requisitos da senha: mínimo de 6 caracteres, 1 caractere especial e 1 letra maiúscula.")
            submit_cadastrar = st.form_submit_button("Criar Minha Conta", use_container_width=True)

        if st.button("Preciso de Ajuda", key="btn_ajuda_cadastro"):
            st.info("Preencha todos os campos. O CPF deve ter 11 dígitos. A senha precisa de no mínimo 6 caracteres, 1 letra maiúscula e 1 caractere especial (!@#$%...).")

        if submit_cadastrar:
            cpf_limpo = re.sub(r"\D", "", cpf)

            if not nome or not cpf_limpo or not email or not senha:
                st.error("Por favor, preencha todos os campos obrigatórios.")
            elif len(cpf_limpo) != 11:
                st.error("O CPF deve conter exatamente 11 dígitos numéricos.")
            elif cpf_limpo in st.session_state["banco_clientes"]:
                st.error("Este CPF já está cadastrado na plataforma! Faça login com seu CPF e senha.")
            elif not validar_senha(senha):
                st.error("A senha não atende aos requisitos mínimos (6+ caracteres, 1 maiúscula e 1 caractere especial).")
            elif senha != confirmar_senha:
                st.error("As senhas digitadas não coincidem.")
            else:
                novo_cliente = {
                    "cpf": cpf_limpo,
                    "nome": nome,
                    "email": email,
                    "telefone": "",
                    "nascimento": "",
                    "renda": 0.0,
                    "senha": hash_senha(senha),
                }
                salvar_cliente_disco(cpf_limpo, novo_cliente)
                
                st.success("Cadastro efetuado com sucesso! Faça seu login utilizando seu CPF.")
                st.session_state["etapa_fluxo"] = "login"
                st.rerun()

        if st.button("Voltar para o Login", use_container_width=True):
            st.session_state["etapa_fluxo"] = "login"
            st.rerun()

# --- 3.1 TELA DE RECUPERAÇÃO DE SENHA ---
elif st.session_state["etapa_fluxo"] == "recuperar_senha":
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if LOGO_EXISTE:
            img_col1, img_col2, img_col3 = st.columns([1, 1, 1])
            with img_col2:
                st.image(CAMINHO_LOGO, use_container_width=True)

        st.markdown(
            "<h2 style='text-align: center;'>Recuperar Senha</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p class='subtitulo-cinza' style='text-align: center; margin-bottom: 1.5rem;'>Informe seu CPF e e-mail para redefinir sua senha</p>",
            unsafe_allow_html=True,
        )

        with st.form("form_recuperar_senha"):
            cpf_rec = st.text_input("CPF", placeholder="Digite apenas os 11 números do CPF")
            email_rec = st.text_input("E-mail", placeholder="seuemail@exemplo.com")
            submit_recuperar = st.form_submit_button("Enviar Link de Redefinição", use_container_width=True)

        if submit_recuperar:
            cpf_rec_limpo = re.sub(r"\D", "", cpf_rec)
            if not cpf_rec_limpo or len(cpf_rec_limpo) != 11:
                st.error("Digite um CPF válido com 11 dígitos.")
            elif cpf_rec_limpo not in st.session_state["banco_clientes"]:
                st.error("CPF não encontrado no sistema.")
            else:
                usuario = st.session_state["banco_clientes"][cpf_rec_limpo]
                if usuario.get("email", "") != email_rec:
                    st.error("O e-mail informado não corresponde ao cadastrado.")
                else:
                    st.success("Um link de redefinição de senha foi enviado para seu e-mail!")
                    st.info("Para esta demonstração, sua senha padrão é: **Senha@123**")

        if st.button("Voltar para o Login", use_container_width=True):
            st.session_state["etapa_fluxo"] = "login"
            st.rerun()

# --- 4. PAINEL GERAL ---
elif st.session_state["etapa_fluxo"] == "painel_geral":
    st.markdown(
        f"""
        <div style='background-image: url("{URL_BANNER}"); background-size: cover; background-position: center;
                     height: 280px; border-radius: 16px; display: flex; align-items: center;
                     justify-content: center; margin-bottom: 2rem; position: relative;'>
            <div style='background: rgba(0,0,0,0.35); padding: 2rem 3rem; border-radius: 12px; text-align: center;'>
                <h1 style='color: #FFFFFF; margin: 0; font-size: 2.4rem; font-weight: 800; letter-spacing: -0.5px; line-height: 1.3;'>Sua casa a um passo de você</h1>
                <p style='color: #FFFFFF; font-size: 1.1rem; margin-top: 0.5rem; font-weight: 400; letter-spacing: 0.3px;'>Encontre o lar perfeito para criar as melhores memórias com quem você ama.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<p class='subtitulo-cinza' style='font-size: 0.95rem; margin-bottom: 2rem;'>Bem-vindo ao sistema de gestão imobiliária G&G Imóveis.</p>", unsafe_allow_html=True)

    st.markdown("<h3>Oportunidades e Destaques da Semana</h3>", unsafe_allow_html=True)

    col_img1, col_img2, col_img3 = st.columns(3)

    with col_img1:
        st.markdown(
            f"""
            <div class="card-imovel">
                <img src='{URL_BOSQUE}' style='width:100%; height:220px; object-fit:cover; border-radius:8px; margin-bottom:12px;' />
                <h4 style="margin-top:0; font-size:1.1rem; font-weight:700;">Residencial Bosque Imperial</h4>
                <p class='subtitulo-cinza' style='font-size:0.85rem; font-style:italic; margin-bottom:12px;'>Conforto, segurança e área de lazer completa para a família.</p>
                <p style='color: #0E1D2F !important; font-weight: 800; margin-bottom:0; font-size:0.95rem;'>Valores a partir de R$ 350 mil</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Simule sua entrada", key="btn_simular_bosque", use_container_width=True):
            st.session_state["imovel_selecionado"] = "Residencial Bosque Imperial - R$ 350.000,00"
            st.session_state["etapa_fluxo"] = "passo1_cliente"
            st.rerun()

    with col_img2:
        st.markdown(
            f"""
            <div class="card-imovel">
                <img src='{URL_PALMEIRAS}' style='width:100%; height:220px; object-fit:cover; border-radius:8px; margin-bottom:12px;' />
                <h4 style="margin-top:0; font-size:1.1rem; font-weight:700;">Condomínio Jardim das Palmeiras</h4>
                <p class='subtitulo-cinza' style='font-size:0.85rem; font-style:italic; margin-bottom:12px;'>O lugar ideal para viver seus melhores momentos ao ar livre.</p>
                <p style='color: #0E1D2F !important; font-weight: 800; margin-bottom:0; font-size:0.95rem;'>Valores a partir de R$ 220 mil</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Simule sua entrada", key="btn_simular_palmeiras", use_container_width=True):
            st.session_state["imovel_selecionado"] = "Condomínio Jardim das Palmeiras - R$ 220.000,00"
            st.session_state["etapa_fluxo"] = "passo1_cliente"
            st.rerun()

    with col_img3:
        st.markdown(
            f"""
            <div class="card-imovel">
                <img src='{URL_VISTA}' style='width:100%; height:220px; object-fit:cover; border-radius:8px; margin-bottom:12px;' />
                <h4 style="margin-top:0; font-size:1.1rem; font-weight:700;">Residencial Vista Verde</h4>
                <p class='subtitulo-cinza' style='font-size:0.85rem; font-style:italic; margin-bottom:12px;'>Seu novo lar cercado de tranquilidade e natureza.</p>
                <p style='color: #0E1D2F !important; font-weight: 800; margin-bottom:12px; font-size:0.95rem;'>Valores a partir de R$ 185 mil</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Simule sua entrada", key="btn_simular_vista", use_container_width=True):
            st.session_state["imovel_selecionado"] = "Residencial Vista Verde - R$ 185.000,00"
            st.session_state["etapa_fluxo"] = "passo1_cliente"
            st.rerun()

# --- 5. PASSO 1: COMPLETAR FICHA DO CLIENTE ---
elif st.session_state["etapa_fluxo"] == "passo1_cliente":
    st.header("Passo 1 de 3: Cadastro e Ficha do Cliente")
    st.write("Complete as informações essenciais do cliente para poder realizar a simulação:")

    cpf_atual = st.session_state.get("usuario_logado", "")
    dados_atuais = st.session_state["banco_clientes"].get(cpf_atual, {})

    with st.form("form_atualizar_cliente_passo1"):
        nome_cli = st.text_input("Nome Completo", value=dados_atuais.get("nome", ""))
        
        cpf_cli = st.text_input(
            "CPF do Cliente",
            value=dados_atuais.get("cpf", cpf_atual),
            disabled=True,
            help="O CPF está vinculado à sua conta e não pode ser alterado."
        )
        
        email_cli = st.text_input("E-mail", value=dados_atuais.get("email", ""))
        tel_cli = st.text_input("Telefone / WhatsApp", value=dados_atuais.get("telefone", ""), placeholder="Ex: (82) 99999-9999")
        
        c1, c2 = st.columns(2)
        with c1:
            renda_cli = st.number_input("Renda Mensal (R$)", value=float(dados_atuais.get("renda", 0.0)), step=500.0)
        with c2:
            nasc_cli = st.text_input("Data de Nascimento", value=dados_atuais.get("nascimento", ""), placeholder="Ex: 01/01/1990")

        btn_avancar = st.form_submit_button("Salvar e Avançar para o Cadastro de Corretor →", use_container_width=True)

    if btn_avancar:
        cpf_salvar = dados_atuais.get("cpf", cpf_atual)
        if not cpf_salvar or not nome_cli or not email_cli or not tel_cli or renda_cli <= 0:
            st.error("Por favor, preencha todos os campos obrigatórios (incluindo WhatsApp e Renda Mensal).")
        else:
            dados_atualizados = {
                "cpf": cpf_salvar,
                "nome": nome_cli,
                "email": email_cli,
                "telefone": tel_cli,
                "renda": renda_cli,
                "nascimento": nasc_cli,
                "senha": dados_atuais.get("senha", hash_senha("Senha@123"))
            }
            salvar_cliente_disco(cpf_salvar, dados_atualizados)
            st.session_state["etapa_fluxo"] = "passo2_corretor"
            st.rerun()

    if st.button("← Voltar ao Painel Geral", use_container_width=True, key="btn_voltar_passo1"):
        st.session_state["etapa_fluxo"] = "painel_geral"
        st.rerun()

# --- 6. PASSO 2: CADASTRO DO CORRETOR ---
elif st.session_state["etapa_fluxo"] == "passo2_corretor":
    st.header("Passo 2 de 3: Cadastro do Corretor")
    st.write("Informe os dados do corretor responsável ou parceiro para vinculação à simulação:")

    with st.form("form_cadastro_corretor_passo2"):
        nome_corr = st.text_input("Nome Completo do Corretor", placeholder="Ex: Carlos Eduardo Silva")
        cpf_corr = st.text_input("CPF do Corretor", placeholder="Digite apenas os números")
        creci = st.text_input("Número do CRECI", placeholder="Ex: 12345-F")
        telefone_corr = st.text_input("Telefone / WhatsApp", placeholder="Ex: (82) 98888-8888")

        btn_avancar_simulacao = st.form_submit_button("Salvar Corretor e Ir para Simulação →", use_container_width=True)

    if btn_avancar_simulacao:
        cpf_corr_limpo = re.sub(r"\D", "", cpf_corr)

        if not nome_corr or not cpf_corr_limpo or not creci:
            st.error("Por favor, preencha os campos obrigatórios (Nome, CPF e CRECI).")
        else:
            st.session_state["banco_corretores"][cpf_corr_limpo] = {
                "nome": nome_corr,
                "cpf": cpf_corr_limpo,
                "creci": creci,
                "telefone": telefone_corr,
            }
            st.session_state["etapa_fluxo"] = "passo3_simulacao"
            st.rerun()

    if st.button("← Voltar ao Passo 1", use_container_width=True, key="btn_voltar_passo2"):
        st.session_state["etapa_fluxo"] = "passo1_cliente"
        st.rerun()

# --- 7. PASSO 3: SIMULAÇÃO DO FINANCIAMENTO ---
elif st.session_state["etapa_fluxo"] == "passo3_simulacao":
    st.header("Passo 3 de 3: Simulação de Financiamento")
    st.write("Confirme os dados de entrada para gerar a proposta completa de financiamento.")

    imovel_padrao = st.session_state.get("imovel_selecionado") or "Residencial Bosque Imperial - R$ 350.000,00"
    lista_chaves = list(IMOVEIS_OPCOES.keys())
    idx_padrao = lista_chaves.index(imovel_padrao) if imovel_padrao in lista_chaves else 0

    imovel_selecionado = st.selectbox(
        "Imóvel Selecionado:",
        options=lista_chaves,
        index=idx_padrao
    )
    
    valor_imovel = IMOVEIS_OPCOES[imovel_selecionado]
    entrada = st.number_input("Valor da Entrada (R$)", value=50000.0, step=5000.0)

    if st.button("Gerar Cálculo Final da Simulação", use_container_width=True):
        cpf_limpo = st.session_state.get("usuario_logado", "")

        if not cpf_limpo or cpf_limpo not in st.session_state["banco_clientes"]:
            st.error("CPF de cliente válido não encontrado na sessão. Retorne ao início.")
        elif entrada > valor_imovel:
            st.error("O valor da entrada não pode ser maior que o valor total do imóvel.")
        else:
            cliente = st.session_state["banco_clientes"][cpf_limpo]
            renda_cliente = cliente.get("renda", 0.0)

            salario_minimo = 1518.0
            qtd_salarios = renda_cliente / salario_minimo if salario_minimo > 0 else 0

            if qtd_salarios <= 1:
                taxa_juros_mensal = 0.5
            elif qtd_salarios <= 2:
                taxa_juros_mensal = 1.0
            elif qtd_salarios <= 3:
                taxa_juros_mensal = 2.0
            elif qtd_salarios <= 4:
                taxa_juros_mensal = 4.0
            else:
                taxa_juros_mensal = 6.0

            taxa_juros_anual = taxa_juros_mensal * 12

            porcentagem_entrada = (entrada / valor_imovel) * 100

            if porcentagem_entrada >= 100:
                pct_subsidio = 0.35
            elif porcentagem_entrada > 50:
                pct_subsidio = 0.20
            elif porcentagem_entrada > 45:
                pct_subsidio = 0.12
            elif porcentagem_entrada > 20:
                pct_subsidio = 0.07
            else:
                pct_subsidio = 0.02

            valor_subsidio = valor_imovel * pct_subsidio
            saldo_devedor = valor_imovel - entrada - valor_subsidio
            saldo_devedor_exibir = max(0.0, saldo_devedor)

            st.info(f"**Cliente:** {cliente.get('nome')} | **Renda Mensal:** R$ {renda_cliente:,.2f} ({qtd_salarios:.1f} Salários Mínimos)")
            st.info(f"**Taxa de Juros Aplicada:** {taxa_juros_mensal:.1f}% a.m. ({taxa_juros_anual:.1f}% a.a.)")
            st.info(f"**Valor do Imóvel Selecionado:** R$ {valor_imovel:,.2f}")
            st.info(f"**Subsídio Concedido ({pct_subsidio * 100:.0f}%):** R$ {valor_subsidio:,.2f}")
            st.success(f"**Saldo Final a Financiar:** R$ {saldo_devedor_exibir:,.2f}")

    if st.button("← Voltar ao Painel Geral", use_container_width=True):
        st.session_state["etapa_fluxo"] = "painel_geral"
        st.rerun()
        