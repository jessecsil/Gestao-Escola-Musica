import streamlit as st
import pandas as pd
import datetime
import urllib.parse
from supabase import create_client, Client

# Configuração da página
st.set_page_config(
    page_title="Harmonia Operacional - Gestão de Escola de Música",
    page_icon="🎸",
    layout="wide"
)

# Conexão com o Supabase usando as chaves dos Secrets
try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error("⚠️ Erro de conexão com o banco de dados. Verifique as chaves nos Secrets do Streamlit Cloud.")

# Mapeamento dos dias da semana e meses em português (com inicial maiúscula)
DIAS_SEMANA_MAP = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}

MESES_PT_MAP = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# --- FUNÇÃO PARA GERAR LINK DO WHATSAPP ---
def formatar_link_whatsapp(numero_str):
    digitos = "".join(filter(str.isdigit, str(numero_str)))
    if not digitos:
        return ""
    if not digitos.startswith("55") and len(digitos) in [10, 11]:
        digitos = f"55{digitos}"
    return f"https://wa.me/{digitos}"

# --- FUNÇÃO PARA GERAR LINK DO WAZE ---
def formatar_link_waze(endereco_str):
    if not endereco_str or endereco_str.lower() == "não informado":
        return ""
    endereco_codificado = urllib.parse.quote(endereco_str)
    return f"https://waze.com/ul?q={endereco_codificado}&navigate=yes"

# --- FUNÇÕES DE BANCO DE DADOS (SUPABASE) ---

def carregar_alunos():
    try:
        res = supabase.table("alunos").select("*").order("nome").execute()
        return res.data
    except:
        return []

def salvar_novo_aluno_banco(dados):
    try:
        supabase.table("alunos").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar aluno: {e}")
        return False

def atualizar_aluno_banco(aluno_id, dados):
    try:
        supabase.table("alunos").update(dados).eq("id", aluno_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar aluno: {e}")
        return False

def deletar_aluno_banco(aluno_id):
    try:
        supabase.table("alunos").delete().eq("id", aluno_id).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao deletar aluno: {e}")
        return False

def carregar_aulas():
    try:
        res = supabase.table("aulas").select("*").order("created_at", desc=True).execute()
        return res.data
    except:
        return []

def salvar_aula_banco(dados):
    try:
        supabase.table("aulas").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar aula: {e}")
        return False

def carregar_financeiro():
    try:
        res = supabase.table("financeiro").select("*").order("created_at", desc=True).execute()
        return res.data
    except:
        return []

def salvar_pagamento_banco(dados):
    try:
        supabase.table("financeiro").insert(dados).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar pagamento: {e}")
        return False


# Carregar dados em tempo real do banco de dados
st.session_state.alunos = carregar_alunos()
st.session_state.historico_aulas = carregar_aulas()
st.session_state.historico_pagamentos = carregar_financeiro()

if "mostrar_form_novo" not in st.session_state:
    st.session_state.mostrar_form_novo = False

if "editando_idx" not in st.session_state:
    st.session_state.editando_idx = None

if "mostrar_form_registrar_aula" not in st.session_state:
    st.session_state.mostrar_form_registrar_aula = False

if "mostrar_form_registrar_pagamento" not in st.session_state:
    st.session_state.mostrar_form_registrar_pagamento = False

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

def calcular_termino_e_meses(inicio_str, plano_str):
    try:
        separador = "/"
        if "-" in inicio_str:
            separador = "-"
        elif "." in inicio_str:
            separador = "."
            
        partes = inicio_str.split(separador)
        if len(partes) != 3:
            return inicio_str, 12
            
        dia_i, mes_i, ano_i = int(partes[0]), int(partes[1]), int(partes[2])
        if ano_i < 100:
            ano_i += 2000
            
        data_inicio_obj = datetime.date(ano_i, mes_i, dia_i)
        
        if plano_str == "Mensal":
            meses = 1
            data_termino_obj = data_inicio_obj + datetime.timedelta(days=30)
        elif plano_str == "Semestral":
            meses = 6
            data_termino_obj = data_inicio_obj + datetime.timedelta(days=182)
        else: # Anual
            meses = 12
            try:
                data_termino_obj = data_inicio_obj.replace(year=data_inicio_obj.year + 1)
            except ValueError:
                data_termino_obj = data_inicio_obj + datetime.timedelta(days=365)
                
        ano_fmt = str(data_termino_obj.year)[-2:] if len(partes[2]) == 2 else str(data_termino_obj.year)
        termino_str = f"{data_termino_obj.day:02d}{separador}{data_termino_obj.month:02d}{separador}{ano_fmt}"
        return termino_str, meses
    except:
        return inicio_str, 12

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
            cpf = st.text_input("CPF * (ex: 000.000.000-00)", value=aluno_atual.get("cpf", ""))
            whatsapp = st.text_input("WhatsApp *", value=aluno_atual["whatsapp"])
            
            instrumentos_lista = ["Violão", "Guitarra", "Baixo", "Teclado", "Cavaquinho"]
            inst_idx = instrumentos_lista.index(aluno_atual.get("instrumento", "Violão")) if aluno_atual.get("instrumento", "Violão") in instrumentos_lista else 0
            instrumento = st.selectbox("Instrumento / Tipo de Aula *", instrumentos_lista, index=inst_idx)
            
            tempos_lista = ["1 hora", "45 minutos", "30 minutos", "1 hora e 30 minutos"]
            tempo_idx = tempos_lista.index(aluno_atual.get("tempo_aula", "1 hora")) if aluno_atual.get("tempo_aula", "1 hora") in tempos_lista else 0
            tempo_aula = st.selectbox("Tempo de Duração da Aula *", tempos_lista, index=tempo_idx)

            modalidades_lista = ["Selecione", "Presencial", "Online"]
            mod_idx = modalidades_lista.index(aluno_atual["modalidade"]) if aluno_atual["modalidade"] in modalidades_lista else 0
            modalidade = st.selectbox("Modalidade *", modalidades_lista, index=mod_idx)
            
            dias_semana = ["Selecione", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
            dia_idx = dias_semana.index(aluno_atual["dia"]) if aluno_atual["dia"] in dias_semana else 0
            dia = st.selectbox("Dia da aula *", dias_semana, index=dia_idx)
            
            horario_digitos = st.text_input("Horário * (ex: 1100)", value=aluno_atual["horario"])
            endereco = st.text_input("Endereço Completo *", value=aluno_atual["endereco"])
            
            planos_lista = ["Mensal", "Semestral", "Anual"]
            vig_atual = aluno_atual.get("vigencia", "Anual")
            if vig_atual == "6 meses":
                vig_atual = "Semestral"
            elif vig_atual == "1 ano":
                vig_atual = "Anual"
            plano_idx = planos_lista.index(vig_atual) if vig_atual in planos_lista else 2
            
            plano = st.selectbox("Plano contratado *", planos_lista, index=plano_idx)
            
            valor_mensal = st.number_input("Valor Mensal (R$) *", min_value=0.0, step=50.0, value=float(aluno_atual.get("valor_mensal", 0.0)))
            
            inicio_contrato = st.text_input("Início do Contrato * (ex: 25/10/26)", value=aluno_atual.get("inicio_contrato", "25/10/26"))
            
            termino_contrato, meses_calc = calcular_termino_e_meses(inicio_contrato, plano)
            valor_total_calc = valor_mensal * meses_calc
            
            st.info(f"📅 Término Calculado: **{termino_contrato}** | 💵 **Valor Total do Contrato ({meses_calc} meses): R$ {valor_total_calc:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
            
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
                if not nome.strip() or not cpf.strip() or modalidade == "Selecione" or dia == "Selecione" or valor_mensal <= 0.0:
                    st.error("❌ Preencha os campos obrigatórios (Nome, CPF, etc.).")
                else:
                    horario_formatado = formatar_horario(horario_digitos)
                    transporte_final = 0.0 if modalidade == "Online" else custo_transporte

                    dados_atualizados = {
                        "nome": nome,
                        "cpf": cpf,
                        "whatsapp": whatsapp,
                        "instrumento": instrumento,
                        "tempo_aula": tempo_aula,
                        "modalidade": modalidade,
                        "dia": dia,
                        "horario": horario_formatado,
                        "endereco": endereco,
                        "valor_mensal": valor_mensal,
                        "valor_contrato": valor_total_calc,
                        "inicio_contrato": inicio_contrato,
                        "termino_contrato": termino_contrato,
                        "origem": origem,
                        "rede_social": rede_social if rede_social else "Não informada",
                        "custo_transporte": transporte_final,
                        "status_contrato": status_contrato,
                        "vigencia": plano,
                    }
                    
                    if atualizar_aluno_banco(aluno_atual["id"], dados_atualizados):
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
                cpf = st.text_input("CPF * (ex: 000.000.000-00)")
                whatsapp = st.text_input("WhatsApp *")
                
                instrumento = st.selectbox("Instrumento / Tipo de Aula *", ["Violão", "Guitarra", "Baixo", "Teclado", "Cavaquinho"])
                tempo_aula = st.selectbox("Tempo de Duração da Aula *", ["1 hora", "45 minutos", "30 minutos", "1 hora e 30 minutos"])
                
                modalidade = st.selectbox("Modalidade *", ["Selecione", "Presencial", "Online"])
                
                dias_semana = ["Selecione", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
                dia = st.selectbox("Dia da aula *", dias_semana)
                
                horario_digitos = st.text_input("Horário * (ex: 1100)")
                endereco = st.text_input("Endereço Completo *")
                
                plano = st.selectbox("Plano contratado *", ["Mensal", "Semestral", "Anual"])
                
                valor_mensal = st.number_input("Valor Mensal (R$) *", min_value=0.0, step=50.0, value=0.0)
                
                inicio_contrato = st.text_input("Início do Contrato *", value="25/10/26")
                termino_sugerido, meses_calc = calcular_termino_e_meses(inicio_contrato, plano)
                valor_total_calc = valor_mensal * meses_calc
                
                st.info(f"📅 Término Calculado: **{termino_sugerido}** | 💵 **Valor Total ({meses_calc} meses): R$ {valor_total_calc:,.2f}**".replace(",", "X").replace(".", ",").replace("X", "."))
                
                origem = st.selectbox("Origem *", ["Selecione", "Instagram", "Indicação", "Facebook", "Outros"])
                rede_social = st.text_input("Rede social (Opcional)")
                custo_transporte = st.number_input("Custo Transporte (R$) (Opcional)", min_value=0.0, step=10.0, value=0.0)
                status_contrato = st.selectbox("Status *", ["Ativo", "Pendente", "Cancelado"])
                
                submit = st.form_submit_button("Salvar Aluno", use_container_width=True)
                
                if submit:
                    if not nome.strip() or not cpf.strip() or modalidade == "Selecione" or dia == "Selecione" or valor_mensal <= 0.0:
                        st.error("❌ Preencha os campos obrigatórios (Nome, CPF, etc.).")
                    else:
                        horario_formatado = formatar_horario(horario_digitos)
                        transporte_final = 0.0 if modalidade == "Online" else custo_transporte

                        novo_aluno = {
                            "nome": nome,
                            "cpf": cpf,
                            "whatsapp": whatsapp,
                            "instrumento": instrumento,
                            "tempo_aula": tempo_aula,
                            "modalidade": modalidade,
                            "dia": dia,
                            "horario": horario_formatado,
                            "endereco": endereco,
                            "valor_mensal": valor_mensal,
                            "valor_contrato": valor_total_calc,
                            "inicio_contrato": inicio_contrato,
                            "termino_contrato": termino_sugerido,
                            "origem": origem,
                            "rede_social": rede_social if rede_social else "Não informada",
                            "custo_transporte": transporte_final,
                            "status_contrato": status_contrato,
                            "vigencia": plano,
                            "aula_concluida": False
                        }
                        
                        if salvar_novo_aluno_banco(novo_aluno):
                            st.session_state.mostrar_form_novo = False
                            st.success(f"Aluno {nome} salvo!")
                            st.rerun()

    st.markdown("---")
    st.markdown("##### 📱 Alunos Cadastrados")
    
    if not st.session_state.alunos:
        st.info("Nenhum aluno registrado no banco de dados.")
    else:
        for idx, aluno in enumerate(st.session_state.alunos):
            with st.container(border=True):
                st.markdown(f"**👤 {aluno['nome']}** (CPF: {aluno.get('cpf', 'Não informado')})")
                
                num_wa = aluno.get('whatsapp', '')
                link_wa = formatar_link_whatsapp(num_wa)
                if link_wa:
                    st.markdown(f"📱 WhatsApp: [{num_wa}]({link_wa}) 🟢")
                else:
                    st.text(f"📱 WhatsApp: {num_wa}")

                end_aluno = aluno.get('endereco', 'Não informado')
                link_waze = formatar_link_waze(end_aluno)
                if link_waze:
                    st.markdown(f"📍 Endereço: [{end_aluno}]({link_waze}) 🚗 *(clique para abrir no Waze)*")
                else:
                    st.text(f"📍 Endereço: {end_aluno}")

                inst_exibir = aluno.get('instrumento', 'Violão')
                tempo_exibir = aluno.get('tempo_aula', '1 hora')
                st.text(f"🎸 Aula de {inst_exibir} ({tempo_exibir}): {aluno.get('dia', '')} às {aluno.get('horario', '')} ({aluno.get('modalidade', '')})")
                
                with st.expander("➕ Ver mais detalhes (Contrato, Valores e Ações)"):
                    val_mensal = float(aluno.get('valor_mensal', 0.0))
                    val_contrato = float(aluno.get('valor_contrato', 0.0))
                    plano_exibir = aluno.get('vigencia', 'Anual')
                    
                    st.text(f"📋 Plano: {plano_exibir}")
                    st.text(f"💵 Valor Mensal: R$ {val_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    st.text(f"💰 Valor Total do Contrato: R$ {val_contrato:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    st.text(f"📅 Início: {aluno.get('inicio_contrato', '')} | Término: {aluno.get('termino_contrato', '')}")
                    st.text(f"🚗 Custo Transporte: R$ {float(aluno.get('custo_transporte', 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                    st.text(f"📌 Status: {aluno.get('status_contrato', '')}")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    if col_btn1.button("✏️ Editar", key=f"edit_{aluno['id']}", use_container_width=True):
                        st.session_state.editando_idx = idx
                        st.rerun()
                    if col_btn2.button("🗑️ Excluir", key=f"del_{aluno['id']}", use_container_width=True):
                        if deletar_aluno_banco(aluno['id']):
                            st.success("Aluno removido!")
                            st.rerun()

    st.markdown("---")
    st.markdown("##### 📄 Gerar Contrato em PDF")
    
    if st.session_state.alunos:
        nomes_alunos_pdf = [a["nome"] for a in st.session_state.alunos]
        aluno_selecionado = st.selectbox("Selecione o aluno:", nomes_alunos_pdf, key="selectbox_gerar_contrato_pdf")
        
        aluno_dados = next(a for a in st.session_state.alunos if a["nome"] == aluno_selecionado)
        
        nome_professor = "GELTER LOURENÇO DA SILVA"
        rg_professor = "29.853.642-0"
        cnpj_professor = "24.195.286.0001-76"
        banco_professor = "536"
        agencia_professor = "0655"
        conta_professor = "16954797-3"
        dia_vencimento = "20"
        multa_atraso = "5%"
        prazo_atraso_dias = "15 (quinze)"
        endereco_professor = "Rua Guaraipo, no 46 Pq. Sevilha na cidade de São Paulo/SP"
        local_assinatura = "São Paulo, SP"
        
        inicio_fmt = aluno_dados.get('inicio_contrato', '___/___/______')
        termino_fmt = aluno_dados.get('termino_contrato', '___/___/______')

        from fpdf import FPDF

        class PDF(FPDF):
            def header(self):
                instrumento_titulo = aluno_dados.get('instrumento', 'Violão').upper()
                self.set_font('Arial', 'B', 12)
                self.cell(0, 8, f'CONTRATO DE PRESTAÇÃO DE SERVIÇOS DE AULAS DE {instrumento_titulo}', 0, 1, 'C')
                self.ln(4)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        def criar_pdf_contrato():
            pdf = PDF()
            pdf.add_page()
            pdf.set_font('Arial', '', 9.5)
            
            instrumento_aluno = aluno_dados.get('instrumento', 'Violão')
            cpf_aluno = aluno_dados.get('cpf', '_________________')
            nome_aluno = aluno_dados['nome']
            endereco_aluno = aluno_dados.get('endereco', '')
            whatsapp_aluno = aluno_dados.get('whatsapp', '')
            
            # --- PREÁMBULO COM DADOS EM NEGRITO ---
            pdf.write(5, "Pelo presente instrumento particular, de um lado, ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{nome_aluno}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", inscrito(a) no CPF sob o nº ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{cpf_aluno}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", residente e domiciliado(a) na ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{endereco_aluno}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", telefone ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{whatsapp_aluno}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", doravante denominado(a) CONTRATANTE e, de outro lado, ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{nome_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", brasileiro, casado, (Autônomo) Músico e Professor, portador da cédula de identidade RG sob nº ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{rg_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, " e inscrito no CNPJ sob nº ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{cnpj_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", residente e domiciliado na ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{endereco_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", doravante denominado CONTRATADO.\n\nCONTRATANTE e CONTRATADO têm entre si, justo e contratado o presente contrato, que se regerá pelas seguintes Cláusulas e Condições, que abaixo livremente estipulam, obrigando-se a cumpri-las por si:\n\n")
            
            # --- CLÁUSULA PRIMEIRA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA PRIMEIRA - DO OBJETO", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            
            mod_aluno = aluno_dados.get('modalidade', '')
            local_aula = aluno_dados.get('endereco', '') if mod_aluno == 'Presencial' else 'ambiente virtual (Online)'
            tempo_duracao = aluno_dados.get('tempo_aula', '1 hora')
            horario_aula = aluno_dados.get('horario', '')
            dia_aula_str = aluno_dados.get('dia', '')
            
            pdf.write(5, "1.1. O presente contrato tem por objeto a prestação de serviços de aulas de ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{instrumento_aluno}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", a serem ministradas pelo PROFESSOR em ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{local_aula}.\n")
            pdf.set_font('Arial', '', 9.5)
            
            pdf.write(5, "1.1.1. As aulas ocorrerão semanalmente, às ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{dia_aula_str} das {horario_aula}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", com duração de ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{tempo_duracao}.\n")
            pdf.set_font('Arial', '', 9.5)
            
            c1_resto = (
                f"1.1.2. Cada aula terá a duração de {tempo_duracao}, podendo existir tolerância de até 5 minutos para "
                f"ajustes de início e término, sem prejuízo do conteúdo ministrado.\n"
                f"1.1.3. Para a realização das aulas online, o CONTRATANTE declara-se ciente da necessidade de conexão "
                f"estável com a internet e de espaço sem ruídos ou interferências externas, visando o melhor aproveitamento das aulas.\n"
                f"1.1.4. Para a realização das aulas presenciais, as partes devem comparecer ao local acordado com no mínimo 10 "
                f"(dez) minutos de antecedência, sendo certo que o atraso por parte do CONTRATANTE não será compensado posteriormente à aula agendada.\n"
                f"1.1.5. As aulas ministradas pelo CONTRATADO terão a duração firmada de {tempo_duracao}.\n"
                f"1.1.6. Sempre e assim que possível, o CONTRATADO prestará suporte via WhatsApp (horário comercial) para o esclarecimento de dúvidas do CONTRATANTE.\n\n"
            )
            pdf.write(5, c1_resto)
            
            # --- CLÁUSULA SEGUNDA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA SEGUNDA - DO PLANO DAS AULAS, VALORES E FORMA DE PAGAMENTO", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            
            val_mensal = float(aluno_dados.get('valor_mensal', 0.0))
            val_total = float(aluno_dados.get('valor_contrato', 0.0))
            plano_escolhido = aluno_dados.get('vigencia', 'Anual')
            
            pdf.write(5, "2.1. Para a prestação dos serviços, o CONTRATANTE escolhe o plano de aulas abaixo:\n- Plano Escolhido: ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{plano_escolhido}\n")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, "- Valor Mensal: R$ ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{val_mensal:.2f}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, " (4 aulas no mês, uma por semana)\n- Valor Total do Contrato (")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{plano_escolhido}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, "): R$ ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{val_total:.2f}\n\n")
            pdf.set_font('Arial', '', 9.5)
            
            c2_p1 = (
                f"2.1.1. No caso da escolha pelo Plano, para os meses que possuam mais de 4 (quatro) semanas, a última semana "
                f"(correspondente à quinta aula) ficará vaga e livre para as partes, sendo mantido o valor do plano mensal indicado acima. "
                f"Caso o CONTRATANTE manifeste interesse pela quinta aula no mês, e havendo disponibilidade do CONTRATADO, deverá o "
                f"CONTRATANTE efetuar o pagamento do valor da aula avulsa no momento de sua manifestação.\n"
                f"2.1.2. No caso das aulas presenciais cujo deslocamento será realizado pelo CONTRATADO, o CONTRATANTE deverá realizar "
                f"o pagamento dos valores relativos ao Plano escolhido, somado à Taxa de Deslocamento, a ser informada pelo CONTRATADO.\n"
                f"2.2. O pagamento dos valores relativos ao plano escolhido deverá ser realizado na modalidade Pix para a chave: "
            )
            pdf.write(5, c2_p1)
            
            # Dados da chave Pix e Pagamento em Negrito na Cláusula 2.2
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{cnpj_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", Banco ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{banco_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", Agência ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{agencia_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, " e conta ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{conta_professor}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, ", até o dia ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{dia_vencimento}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, " de cada mês, sendo certo que o atraso sem aviso prévio implicará na imediata suspensão da prestação dos serviços até a devida regularização ou renegociação. Se o atraso ultrapassar o prazo de ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{prazo_atraso_dias}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, " dias corridos, incidirá multa de ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{multa_atraso}")
            pdf.set_font('Arial', '', 9.5)
            
            c2_p2 = (
                f" ao dia.\n"
                f"2.2.1. Para a comprovação do pagamento, o CONTRATANTE deverá enviar o comprovante ao CONTRATADO.\n"
                f"2.2.2. No caso de inadimplemento e ausência de renegociação, o CONTRATADO tomará as medidas cabíveis em lei.\n\n"
            )
            pdf.write(5, c2_p2)
            
            # --- CLÁUSULA TERCEIRA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA TERCEIRA - DAS AULAS, REMARCAÇÃO E ABONOS", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            c3 = (
                f"3.1. Para o abono de aulas ou remarcação, somente serão aceitas justificativas por motivos de saúde ou urgência.\n"
                f"3.2. No caso de viagem do CONTRATANTE, este deverá avisar o CONTRATADO com no mínimo 30 (trinta) dias de antecedência, "
                f"para que as aulas sejam remarcadas, devendo o valor do Plano ser pago normalmente.\n"
                f"3.3. Caso a aula caia em feriado, o CONTRATADO contatará o CONTRATANTE para a devida remarcação.\n\n"
            )
            pdf.write(5, c3)
            
            # --- CLÁUSULA QUARTA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA QUARTA - DOS MATERIAIS E FERRAMENTAS", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            c4 = (
                f"4.1. Será de inteira responsabilidade do CONTRATANTE a obtenção dos materiais e instrumentos necessários.\n"
                f"4.2. O CONTRATANTE autoriza o uso não comercial de trechos de aula e imagens para fins de divulgação do trabalho do CONTRATADO.\n\n"
            )
            pdf.write(5, c4)
            
            # --- CLÁUSULA QUINTA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA QUINTA - RESCISÃO E MULTA", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, "5.1. O presente contrato é firmado na modalidade de plano ")
            pdf.set_font('Arial', 'B', 9.5)
            pdf.write(5, f"{plano_escolhido}")
            pdf.set_font('Arial', '', 9.5)
            pdf.write(5, " e, no caso de manifestação de vontade de encerramento, o CONTRATANTE deverá notificar o CONTRATADO por escrito com no mínimo 30 dias de antecedência. O rompimento imediato implicará na aplicação de multa no montante de R$ 400,00 (quatrocentos reais).\n\n")
            
            # --- CLÁUSULA SEXTA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA SEXTA - MUDANÇA DE ENDEREÇO E MANUTENÇÃO DE HORÁRIO", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            c6 = (
                f"6.1. Caso o CONTRATANTE mude de endereço, fica preservado o direito de manter dia e horário, desde que o novo local seja de fácil acesso.\n"
                f"6.2. Caso o deslocamento se torne inviável, o CONTRATADO apresentará alternativas de continuidade.\n"
                f"6.3. Em hipótese alguma a mudança de endereço será considerada motivo de rescisão imediata sem aviso prévio de 30 dias.\n\n"
            )
            pdf.write(5, c6)
            
            # --- CLÁUSULA SÉTIMA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA SÉTIMA - DAS DISPOSIÇÕES GERAIS", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            c7 = (
                f"7.1. No caso de alteração destes termos e/ou valores, o CONTRATADO informará o CONTRATANTE para aceite.\n\n"
            )
            pdf.write(5, c7)
            
            # --- CLÁUSULA OITAVA ---
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, "CLÁUSULA OITAVA - DO FORO", 0, 1)
            pdf.set_font('Arial', '', 9.5)
            c8 = (
                f"8.1. Fica eleito o foro da Comarca de São Paulo/SP para dirimir eventuais litígios. E por estarem justas e contratadas, "
                f"as partes firmam o presente instrumento em 02 (duas) vias de igual teor.\n\n"
            )
            pdf.write(5, c8)
            pdf.ln(5)
            
            # Data com mês iniciando em letra maiúscula
            hoje_dt = datetime.date.today()
            dia_hoje = hoje_dt.day
            mes_hoje = MESES_PT_MAP[hoje_dt.month]
            ano_hoje = hoje_dt.year
            data_atual_extenso = f"{local_assinatura}, {dia_hoje} de {mes_hoje} de {ano_hoje}."
            
            pdf.cell(0, 5, data_atual_extenso, 0, 1)
            pdf.ln(20)
            
            pdf.cell(95, 5, "________________________________________________", 0, 0, 'C')
            pdf.cell(95, 5, "________________________________________________", 0, 1, 'C')
            pdf.cell(95, 5, f"CONTRATANTE - {nome_aluno}", 0, 0, 'C')
            pdf.cell(95, 5, f"CONTRATADO - {nome_professor}", 0, 1, 'C')

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
            label="📥 Baixar Contrato em PDF (Oficial)",
            data=pdf_bytes,
            file_name=f"contrato_{aluno_dados['nome'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            key="btn_baixar_contrato_direto",
            use_container_width=True
        )
    else:
        st.info("Cadastre um aluno para gerar o contrato.")

# -----------------------------------------------------------------------------
# MÓDULO 2: AULAS
# -----------------------------------------------------------------------------
if modulo == "Aulas":
    st.markdown("### 📅 Módulo de Aulas")
    
    hoje = datetime.date.today()
    dia_semana_hoje = DIAS_SEMANA_MAP[hoje.weekday()]
    data_formatada_hoje = hoje.strftime("%d/%m/%Y")
    
    st.markdown(f"##### 📌 Agenda de Hoje ({data_formatada_hoje} - {dia_semana_hoje})")
    
    alunos_hoje = [
        a for a in st.session_state.get("alunos", []) 
        if a.get("dia") == dia_semana_hoje and a.get("status_contrato") == "Ativo"
    ]
    
    if alunos_hoje:
        alunos_hoje_ordenados = sorted(alunos_hoje, key=lambda x: x.get("horario", ""))
        for a in alunos_hoje_ordenados:
            tipo_icone = "💻 Online" if a.get("modalidade") == "Online" else "🏠 Presencial"
            with st.container(border=True):
                col_h1, col_h2 = st.columns([1, 2])
                with col_h1:
                    st.markdown(f"⏰ **{a.get('horario')}**")
                    st.caption(f"{tipo_icone}")
                with col_h2:
                    st.markdown(f"👤 **{a.get('nome')}** ({a.get('instrumento', 'Violão')})")
                    
                    end_h = a.get('endereco', '')
                    link_waze_h = formatar_link_waze(end_h)
                    if a.get("modalidade") == "Presencial" and link_waze_h:
                        st.markdown(f"📍 [{end_h}]({link_waze_h})")
                    elif end_h:
                        st.caption(f"📍 {end_h}")
                        
                    num_wa_h = a.get('whatsapp', '')
                    link_wa_h = formatar_link_whatsapp(num_wa_h)
                    if link_wa_h:
                        st.markdown(f"📱 [{num_wa_h}]({link_wa_h})")
                    else:
                        st.caption(f"📱 {num_wa_h}")
    else:
        st.info(f"Nenhuma aula agendada para hoje ({dia_semana_hoje}).")

    st.markdown("---")
    
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

                    nova_aula = {
                        "aluno": aluno_escolhido,
                        "data": data_aula.strftime("%d/%m/%Y"),
                        "status": situacao_final,
                        "reposta": is_reposta if "Cancelada" in status_aula_reg else "N/A",
                        "custo": custo_reg,
                        "obs": obs_reg
                    }
                    
                    if salvar_aula_banco(nova_aula):
                        st.session_state.mostrar_form_registrar_aula = False
                        st.success("Aula registrada!")
                        st.rerun()

    st.markdown("---")
    
    reposicoes_pendentes = [a for a in st.session_state.historico_aulas if "Pendente" in a.get("status", "")]
    total_custos = sum(float(item.get("custo", 0.0)) for item in st.session_state.historico_aulas)

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Reposições Pendentes", len(reposicoes_pendentes))
    with col_m2:
        st.metric("Custos Registrados", f"R$ {total_custos:.2f}")

    st.markdown("##### 📋 Histórico de Aulas")
    if st.session_state.historico_aulas:
        for aula in st.session_state.historico_aulas:
            with st.container(border=True):
                st.markdown(f"**Aluno: {aula['aluno']}** ({aula['data']})")
                st.text(f"Status: {aula['status']}")
                if aula.get('obs'):
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
                    valor_fixo = float(aluno_sel.get("valor_mensal", aluno_sel.get("valor_contrato", 0.0)))
                    vencimento_fixo_str = aluno_sel.get("termino_contrato", vencimento_fixo_str)

            st.info(f"📄 Valor Mensal: R$ {valor_fixo:,.2f} | Vencimento: {vencimento_fixo_str}".replace(",", "X").replace(".", ",").replace("X", "."))
            status_pag = st.selectbox("Status *", ["Recebido", "Em Atraso", "Previsto"])
            obs_pag = st.text_area("Observações")
            
            salvar_pag = st.form_submit_button("Salvar Pagamento", use_container_width=True)

            if salvar_pag:
                if not lista_alunos_obj:
                    st.error("Cadastre um aluno!")
                else:
                    novo_pagamento = {
                        "aluno": aluno_pag,
                        "valor": valor_fixo,
                        "vencimento": vencimento_fixo_str,
                        "status": status_pag,
                        "observacoes": obs_pag
                    }
                    
                    if salvar_pagamento_banco(novo_pagamento):
                        st.session_state.mostrar_form_registrar_pagamento = False
                        st.success("Pagamento registrado!")
                        st.rerun()

    st.markdown("---")
    total_recebido = sum(float(p.get("valor", 0.0)) for p in st.session_state.historico_pagamentos if p.get("status") == "Recebido")
    total_atraso = sum(float(p.get("valor", 0.0)) for p in st.session_state.historico_pagamentos if p.get("status") == "Em Atraso")
    total_previsto = sum(float(p.get("valor", 0.0)) for p in st.session_state.historico_pagamentos if p.get("status") == "Previsto")

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
                st.markdown(f"**{pag['aluno']}** - R$ {float(pag.get('valor', 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.text(f"Status: {pag['status']} | Vencimento: {pag.get('vencimento', '')}")
    else:
        st.info("Nenhum registro financeiro.")

# -----------------------------------------------------------------------------
# MÓDULO 4: RESUMO DO MÊS
# -----------------------------------------------------------------------------
if modulo == "Resumo do Mês":
    st.markdown("### 📈 Resumo do Mês")
    st.markdown("---")

    alunos_ativos_count = sum(1 for a in st.session_state.alunos if a.get("status_contrato") == "Ativo")
    total_recebido_mes = sum(float(p.get("valor", 0.0)) for p in st.session_state.historico_pagamentos if p.get("status") == "Recebido")
    
    total_custos_transp = sum(float(a.get("custo_transporte", 0.0)) for a in st.session_state.alunos if a.get("custo_transporte"))
    total_custos_aulas = sum(float(a.get("custo", 0.0)) for a in st.session_state.historico_aulas)
    custo_geral = total_custos_transp + total_custos_aulas

    st.metric("Alunos Ativos", str(alunos_ativos_count))
    st.metric("Recebido no Mês", f"R$ {total_recebido_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    st.metric("Custos com Transporte", f"R$ {custo_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")
    st.markdown("##### 📊 Receita por Aluno")

    if st.session_state.alunos:
        df_receita = pd.DataFrame([
            {"Aluno": a["nome"], "Receita": float(a.get("valor_mensal", a.get("valor_contrato", 0)))}
            for a in st.session_state.alunos
        ])
        df_receita = df_receita.set_index("Aluno")
        st.bar_chart(df_receita)
    else:
        st.info("Nenhum dado para exibir no gráfico.")
