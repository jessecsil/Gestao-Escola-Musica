import streamlit as st
import pandas as pd
import datetime
from supabase import create_client, Client

# Conexão com Supabase
supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

# Função para carregar alunos do banco
def carregar_alunos():
    resposta = supabase.table("alunos").select("*").execute()
    return resposta.data

# Função para salvar novo aluno no banco
def salvar_novo_aluno(dados_aluno):
    supabase.table("alunos").insert(dados_aluno).execute()

# Função para atualizar aluno no banco
def atualizar_aluno_banco(aluno_id, dados_aluno):
    supabase.table("alunos").update(dados_aluno).eq("id", aluno_id).execute()

# Função para deletar aluno do banco
def deletar_aluno_banco(aluno_id):
    supabase.table("alunos").delete().eq("id", aluno_id).execute()

# Configuração da página
st.set_page_config(
    page_title="Harmonia Operacional - Gestão de Escola de Música",
    page_icon="🎸",
    layout="wide"
)

# Mapeamento dos dias da semana em português
DIAS_SEMANA_MAP = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}

# Inicialização do estado da sessão com chaves padronizadas
if "alunos" not in st.session_state:
    st.session_state.alunos = [
        {
            "nome": "João Silva", 
            "whatsapp": "(11) 98888-7777",
            "modalidade": "Presencial", 
            "dia": "Terça-feira", 
            "horario": "11:00",
            "endereco": "Rua das Flores, 123 - São Paulo/SP",
            "valor_contrato": 3600.0, 
            "origem": "Instagram",
            "rede_social": "@joaosilva",
            "custo_transporte": 50.0, 
            "status_contrato": "Ativo", 
            "vigencia": "1 ano", 
            "inicio_contrato": "25/10/26",
            "termino_contrato": "25/10/27",
            "aula_concluida": False
        }
    ]

if "mostrar_form_novo" not in st.session_state:
    st.session_state.mostrar_form_novo = False

if "editando_idx" not in st.session_state:
    st.session_state.editando_idx = None

if "mostrar_form_registrar_aula" not in st.session_state:
    st.session_state.mostrar_form_registrar_aula = False

if "mostrar_form_registrar_pagamento" not in st.session_state:
    st.session_state.mostrar_form_registrar_pagamento = False

if "historico_aulas" not in st.session_state:
    st.session_state.historico_aulas = []

if "reposicoes_pendentes" not in st.session_state:
    st.session_state.reposicoes_pendentes = []

if "historico_pagamentos" not in st.session_state:
    st.session_state.historico_pagamentos = []

# Sidebar - Logo e Menu
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("### 🎸 Harmonia Música")

st.sidebar.markdown("---")
modulo = st.sidebar.radio(
    "Menu Principal",
    [
        "👥 Alunos",
        "Aulas",
        "Financeiro",
        "Resumo do Mês",
    ]
)

# Função para calcular o término preservando o formato e separador
def calcular_termino(inicio_str, vigencia_str):
    try:
        separador = "/"
        if "-" in inicio_str:
            separador = "-"
        elif "." in inicio_str:
            separador = "."
            
        partes = inicio_str.split(separador)
        if len(partes) != 3:
            return inicio_str
            
        dia_i, mes_i, ano_i = int(partes[0]), int(partes[1]), int(partes[2])
        if ano_i < 100:
            ano_i += 2000
            
        data_inicio_obj = datetime.date(ano_i, mes_i, dia_i)
        
        if vigencia_str == "6 meses":
            data_termino_obj = data_inicio_obj + datetime.timedelta(days=182)
        else:
            try:
                data_termino_obj = data_inicio_obj.replace(year=data_inicio_obj.year + 1)
            except ValueError:
                data_termino_obj = data_inicio_obj + datetime.timedelta(days=365)
                
        ano_fmt = str(data_termino_obj.year)[-2:] if len(partes[2]) == 2 else str(data_termino_obj.year)
        return f"{data_termino_obj.day:02d}{separador}{data_termino_obj.month:02d}{separador}{ano_fmt}"
    except:
        return inicio_str

def formatar_horario(horario_str):
    horario_limpo = "".join(filter(str.isdigit, str(horario_str)))
    if len(horario_limpo) == 4:
        return f"{horario_limpo[:2]}:{horario_limpo[2:]}"
    return horario_str

# -----------------------------------------------------------------------------
# MÓDULO 1: ALUNOS E CONTRATOS
# -----------------------------------------------------------------------------
if modulo == "👥 Alunos":
    st.markdown("### 👥 Gestão de Alunos")
    
    if st.session_state.editando_idx is not None:
        idx_edit = st.session_state.editando_idx
        aluno_atual = st.session_state.alunos[idx_edit]
        
        st.markdown(f"**Editando Aluno: {aluno_atual['nome']}**")
        with st.form("form_editar_aluno"):
            nome = st.text_input("Nome *", value=aluno_atual["nome"])
            whatsapp = st.text_input("WhatsApp *", value=aluno_atual["whatsapp"])
            
            modalidades_lista = ["Selecione", "Presencial", "Online"]
            mod_idx = modalidades_lista.index(aluno_atual["modalidade"]) if aluno_atual["modalidade"] in modalidades_lista else 0
            modalidade = st.selectbox("Modalidade *", modalidades_lista, index=mod_idx)
            
            dias_semana = ["Selecione", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            dia_idx = dias_semana.index(aluno_atual["dia"]) if aluno_atual["dia"] in dias_semana else 0
            dia = st.selectbox("Dia da aula *", dias_semana, index=dia_idx)
            
            horario_digitos = st.text_input("Horário * (ex: 1100)", value=aluno_atual["horario"])
            endereco = st.text_input("Endereço Completo *", value=aluno_atual["endereco"])
            
            vigencias_lista = ["6 meses", "1 ano"]
            vig_idx = vigencias_lista.index(aluno_atual["vigencia"]) if aluno_atual["vigencia"] in vigencias_lista else 1
            vigencia = st.selectbox("Vigência *", vigencias_lista, index=vig_idx)
            
            valor_contrato = st.number_input("Valor do Contrato (R$) *", min_value=0.0, step=100.0, value=float(aluno_atual["valor_contrato"]))
            inicio_contrato = st.text_input("Início do Contrato * (ex: 25/10/26)", value=aluno_atual.get("inicio_contrato", "25/10/26"))
            
            termino_contrato = calcular_termino(inicio_contrato, vigencia)
            st.info(f"📅 Término Calculado: **{termino_contrato}**")
            
            origens_lista = ["Selecione", "Instagram", "Indicação", "Facebook", "Outros"]
            origem_idx = origens_lista.index(aluno_atual["origem"]) if aluno_atual["origem"] in origens_lista else 0
            origem = st.selectbox("Origem *", origens_lista, index=origem_idx)
            
            rede_social = st.text_input("Rede social (Opcional)", value=aluno_atual["rede_social"])
            custo_transporte = st.number_input("Custo Transporte (R$) (Opcional)", min_value=0.0, step=10.0, value=float(aluno_atual["custo_transporte"]))
            
            status_lista = ["Ativo", "Pendente", "Cancelado"]
            stat_idx = status_lista.index(aluno_atual["status_contrato"]) if aluno_atual["status_contrato"] in status_lista else 0
            status_contrato = st.selectbox("Status *", status_lista, index=stat_idx)
            
            submit_edicao = st.form_submit_button("Salvar Alterações", use_container_width=True)
            cancelar_edicao = st.form_submit_button("Cancelar", use_container_width=True)
            
            if cancelar_edicao:
                st.session_state.editando_idx = None
                st.rerun()
                
            if submit_edicao:
                if not nome.strip() or modalidade == "Selecione" or dia == "Selecione" or valor_contrato <= 0.0:
                    st.error("❌ Preencha os campos obrigatórios.")
                else:
                    horario_formatado = formatar_horario(horario_digitos)
                    transporte_final = 0.0 if modalidade == "Online" else custo_transporte

                    st.session_state.alunos[idx_edit] = {
                        "nome": nome,
                        "whatsapp": whatsapp,
                        "modalidade": modalidade,
                        "dia": dia,
                        "horario": horario_formatado,
                        "endereco": endereco,
                        "valor_contrato": valor_contrato,
                        "inicio_contrato": inicio_contrato,
                        "termino_contrato": termino_contrato,
                        "origem": origem,
                        "rede_social": rede_social if rede_social else "Não informada",
                        "custo_transporte": transporte_final,
                        "status_contrato": status_contrato,
                        "vigencia": vigencia,
                        "aula_concluida": aluno_atual["aula_concluida"]
                    }
                    st.session_state.editando_idx = None
                    st.success(f"Aluno {nome} atualizado!")
                    st.rerun()

    else:
        if not st.session_state.mostrar_form_novo:
            if st.button("➕ Novo Aluno", use_container_width=True):
                st.session_state.mostrar_form_novo = True
                st.rerun()
        else:
            if st.button("✖️ Fechar Formulário", use_container_width=True):
                st.session_state.mostrar_form_novo = False
                st.rerun()
                
        if st.session_state.mostrar_form_novo:
            with st.form("form_novo_aluno_isolado"):
                st.markdown("**Cadastrar Novo Aluno:**")
                
                nome = st.text_input("Nome *")
                whatsapp = st.text_input("WhatsApp *")
                modalidade = st.selectbox("Modalidade *", ["Selecione", "Presencial", "Online"])
                
                dias_semana = ["Selecione", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                dia = st.selectbox("Dia da aula *", dias_semana)
                
                horario_digitos = st.text_input("Horário * (ex: 1100)")
                endereco = st.text_input("Endereço Completo *")
                vigencia = st.selectbox("Vigência *", ["1 ano", "6 meses"])
                valor_contrato = st.number_input("Valor do Contrato (R$) *", min_value=0.0, step=100.0, value=0.0)
                
                inicio_contrato = st.text_input("Início do Contrato *", value="25/10/26")
                termino_sugerido = calcular_termino(inicio_contrato, vigencia)
                st.info(f"📅 Término Calculado: **{termino_sugerido}**")
                
                origem = st.selectbox("Origem *", ["Selecione", "Instagram", "Indicação", "Facebook", "Outros"])
                rede_social = st.text_input("Rede social (Opcional)")
                custo_transporte = st.number_input("Custo Transporte (R$) (Opcional)", min_value=0.0, step=10.0, value=0.0)
                status_contrato = st.selectbox("Status *", ["Ativo", "Pendente", "Cancelado"])
                
                submit = st.form_submit_button("Salvar Aluno", use_container_width=True)
                
                if submit:
                    if not nome.strip() or modalidade == "Selecione" or dia == "Selecione" or valor_contrato <= 0.0:
                        st.error("❌ Preencha os campos obrigatórios.")
                    else:
                        horario_formatado = formatar_horario(horario_digitos)
                        transporte_final = 0.0 if modalidade == "Online" else custo_transporte

                        st.session_state.alunos.append({
                            "nome": nome,
                            "whatsapp": whatsapp,
                            "modalidade": modalidade,
                            "dia": dia,
                            "horario": horario_formatado,
                            "endereco": endereco,
                            "valor_contrato": valor_contrato,
                            "inicio_contrato": inicio_contrato,
                            "termino_contrato": termino_sugerido,
                            "origem": origem,
                            "rede_social": rede_social if rede_social else "Não informada",
                            "custo_transporte": transporte_final,
                            "status_contrato": status_contrato,
                            "vigencia": vigencia,
                            "aula_concluida": False
                        })
                        st.session_state.mostrar_form_novo = False
                        st.success(f"Aluno {nome} cadastrado!")
                        st.rerun()

    st.markdown("---")
    st.markdown("##### 📱 Alunos Cadastrados")
    
    if not st.session_state.alunos:
        st.info("Nenhum aluno registrado.")
    else:
        for idx, aluno in enumerate(st.session_state.alunos):
            with st.container(border=True):
                st.markdown(f"**👤 {aluno['nome']}**")
                st.text(f"📱 WhatsApp: {aluno['whatsapp']}")
                st.text(f"🎸 Aula: {aluno['dia']} às {aluno['horario']} ({aluno['modalidade']})")
                st.text(f"💰 Valor: R$ {aluno['valor_contrato']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.text(f"📌 Status: {aluno['status_contrato']}")
                
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("✏️ Editar", key=f"edit_{idx}", use_container_width=True):
                    st.session_state.editando_idx = idx
                    st.rerun()
                if col_btn2.button("🗑️ Excluir", key=f"del_{idx}", use_container_width=True):
                    st.session_state.alunos.pop(idx)
                    st.success("Aluno removido!")
                    st.rerun()

    st.markdown("---")
    st.markdown("##### 📄 Gerar Contrato em PDF")
    
    if st.session_state.alunos:
        nomes_alunos_pdf = [a["nome"] for a in st.session_state.alunos]
        aluno_selecionado = st.selectbox("Selecione o aluno:", nomes_alunos_pdf, key="selectbox_gerar_contrato_pdf")
        
        aluno_dados = next(a for a in st.session_state.alunos if a["nome"] == aluno_selecionado)
        nome_empresa = "Harmonia Escola de Música"
        local_assinatura = "São Paulo, SP"
        
        inicio_fmt = aluno_dados.get('inicio_contrato', '___/___/______')
        termino_fmt = aluno_dados.get('termino_contrato', '___/___/______')

        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 14)
                self.cell(0, 10, 'CONTRATO DE PRESTACAO DE SERVICOS', 0, 1, 'C')
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

        def criar_pdf_contrato():
            pdf = PDF()
            pdf.add_page()
            pdf.set_font('Arial', '', 11)
            
            pdf.cell(0, 8, f"CONTRATANTE: {aluno_dados['nome']}", 0, 1)
            pdf.cell(0, 8, f"ENDERECO: {aluno_dados['endereco']}", 0, 1)
            pdf.cell(0, 8, f"WHATSAPP: {aluno_dados['whatsapp']}", 0, 1)
            pdf.cell(0, 8, f"CONTRATADA: {nome_empresa}", 0, 1)
            pdf.ln(5)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, "CLÁUSULA 1ª - DO OBJETO", 0, 1)
            pdf.set_font('Arial', '', 11)
            
            dia_aula = aluno_dados['dia'].lower()
            if not dia_aula.startswith("aos"):
                dia_aula = f"aos {dia_aula}"
                
            texto_obj = (f"O presente contrato tem por objeto a prestação de serviços de aulas de música "
                         f"na modalidade {aluno_dados['modalidade']}, a serem realizadas {dia_aula} "
                         f"às {aluno_dados['horario']} horas.")
            pdf.multi_cell(0, 6, texto_obj)
            pdf.ln(4)
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, "CLÁUSULA 2ª - DA VIGÊNCIA E VALOR", 0, 1)
            pdf.set_font('Arial', '', 11)
            texto_vig = (f"O contrato terá a vigência de {aluno_dados['vigencia']}, com início em {inicio_fmt} "
                         f"e término em {termino_fmt}. O valor total pactuado é de R$ {aluno_dados['valor_contrato']:.2f}, "
                         f"adimplido conforme o acordado entre as partes.")
            pdf.multi_cell(0, 6, texto_vig)
            pdf.ln(15)
            
            pdf.cell(0, 8, f"{local_assinatura}, _____ de _________________ de 20____.", 0, 1)
            pdf.ln(25)
            
            pdf.cell(95, 6, "__________________________________", 0, 0, 'C')
            pdf.cell(95, 6, "__________________________________", 0, 1, 'C')
            pdf.cell(95, 6, "CONTRATANTE (Aluno)", 0, 0, 'C')
            pdf.cell(95, 6, "CONTRATADA (Escola)", 0, 1, 'C')

            saida = pdf.output(dest='S')
            if isinstance(saida, bytes):
                return saida
            elif isinstance(saida, bytearray):
                return bytes(saida)
            elif isinstance(saida, str):
                return saida.encode('latin-1')
            else:
                return bytes(saida)

        pdf_bytes = criar_pdf_contrato()
        
        st.download_button(
            label="📥 Baixar Contrato em PDF",
            data=pdf_bytes,
            file_name=f"contrato_{aluno_dados['nome'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            key="btn_baixar_contrato_direto",
            use_container_width=True
        )
    else:
        st.info("Cadastre um aluno para gerar o contrato.")

# -----------------------------------------------------------------------------
# MÓDULO 2: AULAS (Com Agenda do Dia)
# -----------------------------------------------------------------------------
if modulo == "Aulas":
    st.markdown("### 📅 Módulo de Aulas")
    
    # --- AGENDA DO DIA AUTOMÁTICA ---
    hoje = datetime.date.today()
    dia_semana_hoje = DIAS_SEMANA_MAP[hoje.weekday()]
    data_formatada_hoje = hoje.strftime("%d/%m/%Y")
    
    st.markdown(f"##### 📌 Agenda de Hoje ({data_formatada_hoje} - {dia_semana_hoje})")
    
    alunos_hoje = [
        a for a in st.session_state.get("alunos", []) 
        if a.get("dia") == dia_semana_hoje and a.get("status_contrato") == "Ativo"
    ]
    
    if alunos_hoje:
        # Ordenar por horário
        alunos_hoje_ordenados = sorted(alunos_hoje, key=lambda x: x.get("horario", ""))
        for a in alunos_hoje_ordenados:
            tipo_icone = "💻 Online" if a.get("modalidade") == "Online" else "🏠 Presencial"
            with st.container(border=True):
                col_h1, col_h2 = st.columns([1, 2])
                with col_h1:
                    st.markdown(f"⏰ **{a.get('horario')}**")
                    st.caption(f"{tipo_icone}")
                with col_h2:
                    st.markdown(f"👤 **{a.get('nome')}**")
                    if a.get("modalidade") == "Presencial" and a.get("endereco"):
                        st.caption(f"📍 {a.get('endereco')}")
                    st.caption(f"📱 {a.get('whatsapp')}")
    else:
        st.info(f"Nenhuma aula agendada para hoje ({dia_semana_hoje}).")

    st.markdown("---")
    
    # --- REGISTRO DE AULAS REALIZADAS / CANCELADAS ---
    if not st.session_state.mostrar_form_registrar_aula:
        if st.button("➕ Registrar Aula", use_container_width=True):
            st.session_state.mostrar_form_registrar_aula = True
            st.rerun()
    else:
        if st.button("✖️ Fechar Formulário", use_container_width=True):
            st.session_state.mostrar_form_registrar_aula = False
            st.rerun()
            
    if st.session_state.mostrar_form_registrar_aula:
        with st.form("form_registrar_nova_aula"):
            st.markdown("**Registrar Nova Aula:**")

            nomes_alunos = [a["nome"] for a in st.session_state.alunos] if st.session_state.get("alunos", []) else ["Nenhum aluno cadastrado"]
            aluno_escolhido = st.selectbox("Aluno *", nomes_alunos)
            data_aula = st.date_input("Data *", value=datetime.date.today())
            
            status_aula_reg = st.selectbox("Status *", ["Realizada", "Cancelada pelo aluno", "Cancelada pelo professor"])
            opc_reposicao = st.radio("Reposição? *", ["Sim (Pendente)", "Não (Finalizada)"], horizontal=True)
            
            custo_reg = st.number_input("Custo transporte (R$)", min_value=0.0, step=1.0, value=0.0)
            obs_reg = st.text_area("Observações", placeholder="Motivo ou resumo")
            
            salvar = st.form_submit_button("Salvar Aula", use_container_width=True)

            if salvar:
                if not st.session_state.get("alunos", []):
                    st.error("Cadastre um aluno primeiro!")
                else:
                    is_reposta = "Sim" if "Sim" in opc_reposicao else "Não"
                    if status_aula_reg == "Realizada":
                        situacao_final = "Realizada"
                    elif is_reposta == "Sim":
                        situacao_final = f"{status_aula_reg} (Pendente)"
                    else:
                        situacao_final = f"{status_aula_reg} (Finalizada)"

                    st.session_state.historico_aulas.insert(0, {
                        "aluno": aluno_escolhido,
                        "data": data_aula.strftime("%d/%m/%Y"),
                        "status": situacao_final,
                        "reposta": is_reposta if "Cancelada" in status_aula_reg else "N/A",
                        "custo": custo_reg,
                        "obs": obs_reg
                    })
                    
                    if "Cancelada" in status_aula_reg and is_reposta == "Sim":
                        st.session_state.reposicoes_pendentes.append({
                            "aluno": aluno_escolhido,
                            "motivo": status_aula_reg,
                            "data": data_aula.strftime("%d/%m/%Y")
                        })
                        
                    st.session_state.mostrar_form_registrar_aula = False
                    st.success("Aula registrada!")
                    st.rerun()

    st.markdown("---")
    total_custos = sum(item.get("custo", 0.0) for item in st.session_state.historico_aulas)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Reposições Pendentes", len(st.session_state.reposicoes_pendentes))
    with col_m2:
        st.metric("Custos do Mês", f"R$ {total_custos:.2f}")

    st.markdown("##### 📋 Histórico de Aulas")
    if st.session_state.historico_aulas:
        for aula in st.session_state.historico_aulas:
            with st.container(border=True):
                st.markdown(f"**Aluno: {aula['aluno']}** ({aula['data']})")
                st.text(f"Status: {aula['status']}")
                if aula['obs']:
                    st.text(f"Obs: {aula['obs']}")
    else:
        st.info("Nenhuma aula registrada.")

# -----------------------------------------------------------------------------
# MÓDULO 3: FINANCEIRO
# -----------------------------------------------------------------------------
if modulo == "Financeiro":
    st.markdown("### 💰 Módulo Financeiro")
    
    if not st.session_state.mostrar_form_registrar_pagamento:
        if st.button("➕ Registrar Pagamento", use_container_width=True):
            st.session_state.mostrar_form_registrar_pagamento = True
            st.rerun()
    else:
        if st.button("✖️ Fechar Formulário", use_container_width=True):
            st.session_state.mostrar_form_registrar_pagamento = False
            st.rerun()
            
    if st.session_state.mostrar_form_registrar_pagamento:
        with st.form("form_registrar_novo_pagamento"):
            st.markdown("**Registrar Pagamento:**")

            lista_alunos_obj = st.session_state.alunos if st.session_state.get("alunos", []) else []
            nomes_alunos_fin = [a["nome"] for a in lista_alunos_obj] if lista_alunos_obj else ["Nenhum aluno cadastrado"]

            aluno_pag = st.selectbox("Aluno *", nomes_alunos_fin)
            valor_fixo = 0.0
            vencimento_fixo_str = datetime.date.today().strftime("%d/%m/%Y")
            
            if lista_alunos_obj:
                aluno_sel = next((a for a in lista_alunos_obj if a["nome"] == aluno_pag), None)
                if aluno_sel:
                    valor_fixo = float(aluno_sel.get("valor_contrato", 0.0))
                    vencimento_fixo_str = aluno_sel.get("termino_contrato", vencimento_fixo_str)

            st.info(f"📄 Valor: R$ {valor_fixo:,.2f} | Vencimento: {vencimento_fixo_str}".replace(",", "X").replace(".", ",").replace("X", "."))
            status_pag = st.selectbox("Status *", ["Recebido", "Em Atraso", "Previsto"])
            obs_pag = st.text_area("Observações")
            
            salvar_pag = st.form_submit_button("Salvar Pagamento", use_container_width=True)

            if salvar_pag:
                if not lista_alunos_obj:
                    st.error("Cadastre um aluno!")
                else:
                    st.session_state.historico_pagamentos.insert(0, {
                        "Aluno": aluno_pag,
                        "Valor do Contrato": valor_fixo,
                        "Vencimento do Contrato": vencimento_fixo_str,
                        "Status": status_pag,
                        "Observações": obs_pag
                    })
                    st.session_state.mostrar_form_registrar_pagamento = False
                    st.success("Pagamento registrado!")
                    st.rerun()

    st.markdown("---")
    total_recebido = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Recebido")
    total_atraso = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Em Atraso")
    total_previsto = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Previsto")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Recebido", f"R$ {total_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col_f2:
        st.metric("Em Atraso", f"R$ {total_atraso:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col_f3:
        st.metric("Previsto", f"R$ {total_previsto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("##### 📋 Histórico Financeiro")
    if st.session_state.historico_pagamentos:
        for pag in st.session_state.historico_pagamentos:
            with st.container(border=True):
                st.markdown(f"**{pag['Aluno']}** - R$ {pag['Valor do Contrato']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.text(f"Status: {pag['Status']} | Vencimento: {pag['Vencimento do Contrato']}")
    else:
        st.info("Nenhum registro financeiro.")

# -----------------------------------------------------------------------------
# MÓDULO 4: RESUMO DO MÊS
# -----------------------------------------------------------------------------
if modulo == "Resumo do Mês":
    st.markdown("### 📈 Resumo do Mês")
    st.markdown("---")

    alunos_ativos_count = sum(1 for a in st.session_state.alunos if a.get("status_contrato") == "Ativo")
    total_recebido_mes = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Recebido")
    total_custos_transp = sum(float(a.get("custo_transporte", 0.0)) for a in st.session_state.alunos)

    st.metric("Alunos Ativos", str(alunos_ativos_count))
    st.metric("Recebido no Mês", f"R$ {total_recebido_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.metric("Custos com Transporte", f"R$ {total_custos_transp:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")
    st.markdown("##### 📊 Receita por Aluno")

    if st.session_state.alunos:
        df_receita = pd.DataFrame([
            {"Aluno": a["nome"], "Receita": float(a["valor_contrato"])}
            for a in st.session_state.alunos
        ])
        df_receita = df_receita.set_index("Aluno")
        st.bar_chart(df_receita)
    else:
        st.info("Nenhum dado para exibir no gráfico.")
