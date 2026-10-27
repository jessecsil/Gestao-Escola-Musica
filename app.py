import streamlit as st
import pandas as pd
import datetime

# Configuração da página
st.set_page_config(
    page_title="Harmonia Operacional - Gestão de Escola de Música",
    page_icon="🎸",
    layout="wide"
)

# Inicialização do estado da sessão com chaves padronizadas
if "alunos" not in st.session_state:
    st.session_state.alunos = [
        {
            "nome": "João Silva", 
            "whatsapp": "(11) 98888-7777",
            "modalidade": "Presencial", 
            "dia": "Domingo", 
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

# Sidebar - Logo ocupando a largura total da barra lateral e Título
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("### 🎸 Sistema de Gestão-Aula")

st.sidebar.markdown("---")
modulo = st.sidebar.radio(
    "Selecione",
    [
        "👥 Alunos e Contratos",
        "Aulas",
        "Financeiro",
        "Resumo do Mês",
    ]
)

# Função para calcular o término preservando exatamente o formato/separador e o tamanho do ano do início
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

# Função para formatar o horário corretamente (ex: 1100 -> 11:00)
def formatar_horario(horario_str):
    horario_limpo = "".join(filter(str.isdigit, str(horario_str)))
    if len(horario_limpo) == 4:
        return f"{horario_limpo[:2]}:{horario_limpo[2:]}"
    return horario_str

# -----------------------------------------------------------------------------
# MÓDULO 1: ALUNOS E CONTRATOS
# -----------------------------------------------------------------------------
if modulo == "👥 Alunos e Contratos":
    
    if st.session_state.editando_idx is not None:
        idx_edit = st.session_state.editando_idx
        aluno_atual = st.session_state.alunos[idx_edit]
        
        st.markdown(f"##### Editando Aluno: {aluno_atual['nome']}")
        with st.form("form_editar_aluno"):
            nome = st.text_input("Nome *", value=aluno_atual["nome"])
            whatsapp = st.text_input("WhatsApp *", value=aluno_atual["whatsapp"])
            
            modalidades_lista = ["Selecione", "Presencial", "Online"]
            mod_idx = modalidades_lista.index(aluno_atual["modalidade"]) if aluno_atual["modalidade"] in modalidades_lista else 0
            modalidade = st.selectbox("Modalidade *", modalidades_lista, index=mod_idx)
            
            dias_semana = ["Selecione", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            dia_idx = dias_semana.index(aluno_atual["dia"]) if aluno_atual["dia"] in dias_semana else 0
            dia = st.selectbox("Dia da aula *", dias_semana, index=dia_idx)
            
            horario_digitos = st.text_input("Horário * (digite ex: 1100 ou 11:30)", value=aluno_atual["horario"])
            endereco = st.text_input("Endereço Completo *", value=aluno_atual["endereco"])
            
            vigencias_lista = ["6 meses", "1 ano"]
            vig_idx = vigencias_lista.index(aluno_atual["vigencia"]) if aluno_atual["vigencia"] in vigencias_lista else 1
            vigencia = st.selectbox("Vigência do Contrato *", vigencias_lista, index=vig_idx)
            
            valor_contrato = st.number_input("Valor do Contrato (R$) *", min_value=0.0, step=100.0, value=float(aluno_atual["valor_contrato"]))
            
            inicio_contrato = st.text_input("Início do Contrato * (ex: 25/10/26)", value=aluno_atual.get("inicio_contrato", "25/10/26"))
            
            termino_contrato = calcular_termino(inicio_contrato, vigencia)
            st.info(f"📅 Término do Contrato Calculado Automaticamente: **{termino_contrato}**")
            
            origens_lista = ["Selecione", "Instagram", "Indicação", "Facebook", "Outros"]
            origem_idx = origens_lista.index(aluno_atual["origem"]) if aluno_atual["origem"] in origens_lista else 0
            origem = st.selectbox("Origem *", origens_lista, index=origem_idx)
            
            rede_social = st.text_input("Rede social (link) (Opcional)", value=aluno_atual["rede_social"])
            custo_transporte = st.number_input("Despesa com Deslocamento / Transporte (R$) (Opcional)", min_value=0.0, step=10.0, value=float(aluno_atual["custo_transporte"]))
            
            status_lista = ["Ativo", "Pendente", "Cancelado"]
            stat_idx = status_lista.index(aluno_atual["status_contrato"]) if aluno_atual["status_contrato"] in status_lista else 0
            status_contrato = st.selectbox("Status *", status_lista, index=stat_idx)
            
            col_b1, col_b2 = st.columns(2)
            submit_edicao = col_b1.form_submit_button("Salvar Alterações")
            cancelar_edicao = col_b2.form_submit_button("Cancelar")
            
            if cancelar_edicao:
                st.session_state.editando_idx = None
                st.rerun()
                
            if submit_edicao:
                if not nome.strip() or modalidade == "Selecione" or dia == "Selecione" or valor_contrato <= 0.0:
                    st.error("❌ Preencha os campos obrigatórios corretamente.")
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
                    if "editor_tabela_alunos" in st.session_state:
                        del st.session_state["editor_tabela_alunos"]
                    if "editor_tabela_vigencia" in st.session_state:
                        del st.session_state["editor_tabela_vigencia"]
                    st.success(f"Aluno {nome} atualizado com sucesso!")
                    st.rerun()

    else:
        col_f1, col_f2 = st.columns([2, 8])
        if not st.session_state.mostrar_form_novo:
            if col_f1.button("➕ Novo Aluno"):
                st.session_state.mostrar_form_novo = True
                st.rerun()
        else:
            if col_f1.button("✖️ Fechar Formulário"):
                st.session_state.mostrar_form_novo = False
                st.rerun()
                
        if st.session_state.mostrar_form_novo:
            with st.form("form_novo_aluno_isolado"):
                st.markdown("##### Preencha os dados do novo aluno:")
                
                nome = st.text_input("Nome *", placeholder="Nome completo")
                whatsapp = st.text_input("WhatsApp *", placeholder="(11) 99999-9999")
                modalidade = st.selectbox("Modalidade *", ["Selecione", "Presencial", "Online"])
                
                dias_semana = ["Selecione", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                dia = st.selectbox("Dia da aula *", dias_semana)
                
                horario_digitos = st.text_input("Horário * (digite ex: 1100 ou 11:30)", placeholder="1100")
                endereco = st.text_input("Endereço Completo *", placeholder="Rua, Número, Bairro, Cidade/UF")
                vigencia = st.selectbox("Vigência do Contrato *", ["1 ano", "6 meses"])
                valor_contrato = st.number_input("Valor do Contrato (R$) *", min_value=0.0, step=100.0, value=0.0)
                
                inicio_contrato = st.text_input("Início do Contrato * (ex: 25/10/26)", value="25/10/26")
                
                termino_sugerido = calcular_termino(inicio_contrato, vigencia)
                st.info(f"📅 Término do Contrato Calculado Automaticamente: **{termino_sugerido}**")
                
                origem = st.selectbox("Origem *", ["Selecione", "Instagram", "Indicação", "Facebook", "Outros"])
                rede_social = st.text_input("Rede social (link) (Opcional)", placeholder="https://...")
                custo_transporte = st.number_input("Despesa com Deslocamento / Transporte (R$) (Opcional)", min_value=0.0, step=10.0, value=0.0)
                status_contrato = st.selectbox("Status *", ["Ativo", "Pendente", "Cancelado"])
                
                submit = st.form_submit_button("Salvar Novo Aluno")
                
                if submit:
                    campos_invalidos = []
                    if not nome.strip(): campos_invalidos.append("Nome")
                    if not whatsapp.strip(): campos_invalidos.append("WhatsApp")
                    if modalidade == "Selecione": campos_invalidos.append("Modalidade")
                    if dia == "Selecione": campos_invalidos.append("Dia da aula")
                    if not horario_digitos.strip(): campos_invalidos.append("Horário")
                    if not endereco.strip(): campos_invalidos.append("Endereço Completo")
                    if valor_contrato <= 0.0: campos_invalidos.append("Valor do Contrato")
                    if origem == "Selecione": campos_invalidos.append("Origem")
                    
                    if campos_invalidos:
                        st.error(f"❌ Atenção! Os campos obrigatórios não preenchidos: **{', '.join(campos_invalidos)}**.")
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
                        st.success(f"Aluno {nome} cadastrado com sucesso!")
                        st.rerun()

    st.markdown("##### 👥 Lista de Alunos")
    
    if not st.session_state.alunos:
        st.info("Nenhum aluno registrado.")
    else:
        df_alunos = pd.DataFrame(st.session_state.alunos)

        df_lista_alunos = pd.DataFrame()
        df_lista_alunos["Nome"] = df_alunos["nome"]
        df_lista_alunos["WhatsApp"] = df_alunos["whatsapp"]
        df_lista_alunos["Modalidade"] = df_alunos["modalidade"]
        df_lista_alunos["Dia de Aula"] = df_alunos["dia"]
        df_lista_alunos["Horário"] = df_alunos["horario"]
        df_lista_alunos["Endereço"] = df_alunos["endereco"]
        df_lista_alunos["Custo Transp."] = df_alunos["custo_transporte"]
        df_lista_alunos["Editar"] = [False] * len(df_alunos)
        df_lista_alunos["Excluir"] = [False] * len(df_alunos)

        tabela_alunos_editada = st.data_editor(
            df_lista_alunos,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Custo Transp.": st.column_config.NumberColumn(format="R$ %.2f"),
                "Editar": st.column_config.CheckboxColumn("✏️ Editar?", help="Marque para editar este aluno"),
                "Excluir": st.column_config.CheckboxColumn("🗑️ Excluir?", help="Marque para excluir este aluno"),
            },
            key="editor_tabela_alunos"
        )

        for idx, row in tabela_alunos_editada.iterrows():
            if row["Editar"]:
                st.session_state.editando_idx = idx
                if "editor_tabela_alunos" in st.session_state:
                    del st.session_state["editor_tabela_alunos"]
                if "editor_tabela_vigencia" in st.session_state:
                    del st.session_state["editor_tabela_vigencia"]
                st.rerun()
            if row["Excluir"]:
                aluno_removido = st.session_state.alunos.pop(idx)
                if "editor_tabela_alunos" in st.session_state:
                    del st.session_state["editor_tabela_alunos"]
                if "editor_tabela_vigencia" in st.session_state:
                    del st.session_state["editor_tabela_vigencia"]
                st.success(f"Aluno {aluno_removido['nome']} excluído com sucesso!")
                st.rerun()

    st.markdown("##### 📋 Vigência Contratual")
    
    if st.session_state.alunos:
        df_vigencia = pd.DataFrame()
        df_vigencia["Nome"] = df_alunos["nome"]
        df_vigencia["Vigência"] = df_alunos["vigencia"]
        df_vigencia["Início do Contrato"] = df_alunos["inicio_contrato"]
        df_vigencia["Término do Contrato"] = df_alunos["termino_contrato"]
        df_vigencia["Origem"] = df_alunos["origem"]
        df_vigencia["Rede Social"] = df_alunos["rede_social"]
        df_vigencia["Status do Contrato"] = df_alunos["status_contrato"]
        df_vigencia["Valor do Contrato"] = df_alunos["valor_contrato"]

        st.data_editor(
            df_vigencia,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Valor do Contrato": st.column_config.NumberColumn(format="R$ %.2f"),
            },
            key="editor_tabela_vigencia"
        )

    st.markdown("##### 📄 Geração Automática de Contrato em PDF")
    
    if st.session_state.alunos:
        from fpdf import FPDF

        nomes_alunos_pdf = [a["nome"] for a in st.session_state.alunos]
        aluno_selecionado = st.selectbox("Selecione o aluno para gerar o PDF do contrato:", nomes_alunos_pdf, key="selectbox_gerar_contrato_pdf")
        
        aluno_dados = next(a for a in st.session_state.alunos if a["nome"] == aluno_selecionado)
        
        nome_empresa = "Harmonia Escola de Música"
        local_assinatura = "São Paulo, SP"
        
        inicio_fmt = aluno_dados.get('inicio_contrato', '___/___/______')
        termino_fmt = aluno_dados.get('termino_contrato', '___/___/______')

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

            return bytes(pdf.output())

        pdf_bytes = criar_pdf_contrato()
        
        with st.container():
            st.download_button(
                label="📥 Baixar Contrato em PDF",
                data=pdf_bytes,
                file_name=f"contrato_{aluno_dados['nome'].replace(' ', '_')}.pdf",
                mime="application/pdf",
                key="btn_baixar_contrato_direto"
            )
    else:
        st.info("Cadastre primeiro um aluno para poder gerar o contrato em PDF.")

# -----------------------------------------------------------------------------
# MÓDULO 2: AULAS
# -----------------------------------------------------------------------------
if modulo == "Aulas":
    
    col_fa1, col_fa2 = st.columns([2, 8])
    if not st.session_state.mostrar_form_registrar_aula:
        if col_fa1.button("➕ Registrar Aula"):
            st.session_state.mostrar_form_registrar_aula = True
            st.rerun()
    else:
        if col_fa1.button("✖️ Fechar Formulário"):
            st.session_state.mostrar_form_registrar_aula = False
            st.rerun()
            
    if st.session_state.mostrar_form_registrar_aula:
        with st.form("form_registrar_nova_aula"):
            st.markdown("##### Preencha os dados da nova aula:")

            if st.session_state.get("alunos", []):
                nomes_alunos = [a["nome"] for a in st.session_state.alunos]
            else:
                nomes_alunos = ["Nenhum aluno cadastrado"]

            aluno_escolhido = st.selectbox("Aluno *", nomes_alunos)
            data_aula = st.date_input("Data *", value=datetime.date.today())
            
            status_aula_reg = st.selectbox(
                "Status *", 
                ["Realizada", "Cancelada pelo aluno", "Cancelada pelo professor"]
            )
            
            opc_reposicao = st.radio(
                "Esta aula será reposta? (Se cancelada) *", 
                ["Sim (Pendente)", "Não (Finalizada)"],
                horizontal=True
            )
            
            col_custo, col_km = st.columns(2)
            with col_custo:
                custo_reg = st.number_input("Custo transporte (R$)", min_value=0.0, step=1.0, value=0.0)
            with col_km:
                km_reg = st.number_input("Km rodados", min_value=0.0, step=0.5, value=0.0)
                
            obs_reg = st.text_area("Observações", placeholder="Resumo da aula ou motivo do cancelamento")
            
            salvar = st.form_submit_button("Salvar Registro")

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
                        "km": km_reg,
                        "obs": obs_reg
                    })
                    
                    if "Cancelada" in status_aula_reg and is_reposta == "Sim":
                        motivo_texto = f"{status_aula_reg} - {obs_reg}" if obs_reg else status_aula_reg
                        st.session_state.reposicoes_pendentes.append({
                            "aluno": aluno_escolhido,
                            "motivo": motivo_texto,
                            "data": data_aula.strftime("%d/%m/%Y")
                        })
                        
                    st.session_state.mostrar_form_registrar_aula = False
                    st.success("Aula registrada com sucesso!")
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
        st.dataframe(st.session_state.historico_aulas, use_container_width=True)
    else:
        st.info("Nenhuma aula registrada até o momento.")

# -----------------------------------------------------------------------------
# MÓDULO 3: FINANCEIRO
# -----------------------------------------------------------------------------
if modulo == "Financeiro":
    
    col_fin1, col_fin2 = st.columns([2, 8])
    if not st.session_state.mostrar_form_registrar_pagamento:
        if col_fin1.button("➕ Registrar Pagamento"):
            st.session_state.mostrar_form_registrar_pagamento = True
            st.rerun()
    else:
        if col_fin1.button("✖️ Fechar Formulário"):
            st.session_state.mostrar_form_registrar_pagamento = False
            st.rerun()
            
    if st.session_state.mostrar_form_registrar_pagamento:
        with st.form("form_registrar_novo_pagamento"):
            st.markdown("##### Preencha os dados do pagamento:")

            if st.session_state.get("alunos", []):
                lista_alunos_obj = st.session_state.alunos
                nomes_alunos_fin = [a["nome"] for a in lista_alunos_obj]
            else:
                nomes_alunos_fin = ["Nenhum aluno cadastrado"]
                lista_alunos_obj = []

            aluno_pag = st.selectbox("Selecione o Aluno *", nomes_alunos_fin)
            
            valor_fixo = 0.0
            vencimento_fixo_str = datetime.date.today().strftime("%d/%m/%Y")
            
            if lista_alunos_obj:
                aluno_selecionado_dados = next((a for a in lista_alunos_obj if a["nome"] == aluno_pag), None)
                if aluno_selecionado_dados:
                    valor_fixo = float(aluno_selecionado_dados.get("valor_contrato", 0.0))
                    vencimento_fixo_str = aluno_selecionado_dados.get("termino_contrato", vencimento_fixo_str)

            st.info(f"📄 **Dados do Contrato Puxados Automaticamente:**\n\n"
                    f"- **Aluno:** {aluno_pag}\n"
                    f"- **Valor do Contrato:** R$ {valor_fixo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + f"\n"
                    f"- **Vencimento (Término):** {vencimento_fixo_str}")

            status_pag = st.selectbox(
                "Status do Pagamento *", 
                ["Recebido", "Em Atraso", "Previsto"]
            )
            
            obs_pag = st.text_area("Observações (Opcional)", placeholder="Detalhes sobre a cobrança ou pagamento")
            
            salvar_pag = st.form_submit_button("Salvar Pagamento")

            if salvar_pag:
                if not st.session_state.get("alunos", []):
                    st.error("Cadastre um aluno primeiro!")
                else:
                    st.session_state.historico_pagamentos.insert(0, {
                        "Aluno": aluno_pag,
                        "Valor do Contrato": valor_fixo,
                        "Vencimento do Contrato": vencimento_fixo_str,
                        "Status": status_pag,
                        "Observações": obs_pag
                    })
                    st.session_state.mostrar_form_registrar_pagamento = False
                    st.success("Pagamento registrado com sucesso!")
                    st.rerun()

    st.markdown("---")

    total_recebido = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Recebido")
    total_em_atraso = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Em Atraso")
    total_previsto = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Previsto")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Recebido", f"R$ {total_recebido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col_f2:
        st.metric("Em Atraso", f"R$ {total_em_atraso:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    with col_f3:
        st.metric("Previsto", f"R$ {total_previsto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("##### 📋 Histórico Financeiro")
    if st.session_state.historico_pagamentos:
        st.dataframe(
            st.session_state.historico_pagamentos,
            use_container_width=True,
            column_config={
                "Valor do Contrato": st.column_config.NumberColumn(format="R$ %.2f")
            }
        )
    else:
        st.info("Nenhum registro financeiro cadastrado até o momento.")

# -----------------------------------------------------------------------------
# MÓDULO 4: RESUMO DO MÊS
# -----------------------------------------------------------------------------
if modulo == "Resumo do Mês":
    st.markdown("<h2 style='color: white;'>Resumo do Mês</h2>", unsafe_allow_html=True)
    st.markdown("---")

    # Cálculos para os Cards do Resumo
    alunos_ativos_count = sum(1 for a in st.session_state.alunos if a.get("status_contrato") == "Ativo")
    alunos_pausa_count = sum(1 for a in st.session_state.alunos if a.get("status_contrato") != "Ativo")

    total_recebido_mes = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Recebido")
    total_atraso_mes = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") == "Em Atraso")
    total_previsto_mes = sum(float(p.get("Valor do Contrato", 0.0)) for p in st.session_state.historico_pagamentos if p.get("Status") in ["Previsto", "Em Atraso"]) + total_recebido_mes
    
    total_custos_transp = sum(float(a.get("custo_transporte", 0.0)) for a in st.session_state.alunos)
    total_custos_aulas = sum(float(a.get("custo", 0.0)) for a in st.session_state.historico_aulas)
    custo_transporte_geral = total_custos_transp + total_custos_aulas

    # Linha 1 de Cards de Métricas (2 colunas de cards superiores idênticas à imagem)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric("Alunos Ativos", str(alunos_ativos_count), delta=f"{alunos_pausa_count} em pausa", delta_color="off")
    with col_c2:
        st.metric("Recebido", f"R$ {total_recebido_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta="no mês", delta_color="off")

    col_c3, col_c4 = st.columns(2)
    with col_c3:
        st.metric("Previsto", f"R$ {total_previsto_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta=f"R$ {total_atraso_mes:,.2f} em atraso".replace(",", "X").replace(".", ",").replace("X", "."), delta_color="inverse")
    with col_c4:
        st.metric("Custos Transporte", f"R$ {custo_transporte_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), delta="combustível + pedágio", delta_color="off")

    st.markdown("---")
    st.markdown("##### 📊 Receita por Aluno")

    # Gráfico de Receita por Aluno baseado nos dados cadastrados
    if st.session_state.alunos:
        df_receita = pd.DataFrame([
            {"Aluno": a["nome"], "Receita": float(a["valor_contrato"])}
            for a in st.session_state.alunos
        ])
        df_receita = df_receita.sort_values(by="Receita", ascending=False).set_index("Aluno")
        
        st.bar_chart(df_receita)
    else:
        st.info("Nenhum dado de aluno disponível para gerar o gráfico de receita.")