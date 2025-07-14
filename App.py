import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os

# Arquivos CSV
CLIENTES_FILE = "clientes.csv"
SERVICOS_FILE = "servicos.csv"
ORDENS_FILE = "ordens.csv"

# Inicializa arquivos com colunas padrão se não existirem
for file, columns in [
    (CLIENTES_FILE, ["nome", "telefone", "endereco"]),
    (SERVICOS_FILE, ["descricao", "valor"]),
    (ORDENS_FILE, ["cliente", "servico", "aparelho", "data"])
]:
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

# Funções de manipulação de dados
def carregar_dados(arquivo):
    return pd.read_csv(arquivo)

def salvar_dado(arquivo, novo_dado):
    df = carregar_dados(arquivo)
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    df.to_csv(arquivo, index=False)

def atualizar_dado(arquivo, index, novos_dados):
    df = carregar_dados(arquivo)
    for chave, valor in novos_dados.items():
        df.at[index, chave] = valor
    df.to_csv(arquivo, index=False)

def deletar_dado(arquivo, index):
    df = carregar_dados(arquivo)
    df = df.drop(index).reset_index(drop=True)
    df.to_csv(arquivo, index=False)

# Página de navegação
pagina = st.sidebar.selectbox("📚 Navegação", [
    "📋 Cadastrar Cliente", "🛠 Cadastrar Serviço", "📄 Gerar Ordem de Serviço"
])

# Página 1 - Clientes
if pagina == "📋 Cadastrar Cliente":
    st.title("Cadastro de Cliente")
    nome = st.text_input("Nome do Cliente")
    telefone = st.text_input("Telefone")
    endereco = st.text_area("Endereço")

    if st.button("Salvar Cliente"):
        if nome and telefone and endereco:
            salvar_dado(CLIENTES_FILE, {"nome": nome, "telefone": telefone, "endereco": endereco})
            st.success("✅ Cliente salvo com sucesso!")
            st.experimental_rerun()
        else:
            st.error("❌ Todos os campos são obrigatórios.")

    st.subheader("📄 Clientes Cadastrados")
    clientes_df = carregar_dados(CLIENTES_FILE)

    if not clientes_df.empty:
        for i, row in clientes_df.iterrows():
            st.markdown(f"**{row['nome']}** - {row['telefone']} - {row['endereco']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Editar", key=f"edit_cliente_{i}"):
                    with st.form(f"form_cliente_{i}"):
                        nome_edit = st.text_input("Nome", value=row["nome"])
                        tel_edit = st.text_input("Telefone", value=row["telefone"])
                        end_edit = st.text_area("Endereço", value=row["endereco"])
                        if st.form_submit_button("Salvar Alterações"):
                            atualizar_dado(CLIENTES_FILE, i, {
                                "nome": nome_edit, "telefone": tel_edit, "endereco": end_edit
                            })
                            st.success("✅ Cliente atualizado!")
                            st.experimental_rerun()
            with col2:
                if st.button("🗑️ Excluir", key=f"del_cliente_{i}"):
                    deletar_dado(CLIENTES_FILE, i)
                    st.warning("⚠️ Cliente excluído.")
                    st.experimental_rerun()
    else:
        st.info("Nenhum cliente cadastrado.")

# Página 2 - Serviços
elif pagina == "🛠 Cadastrar Serviço":
    st.title("Cadastro de Serviço")
    descricao = st.text_input("Descrição do Serviço")
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

    if st.button("Salvar Serviço"):
        if descricao and valor > 0:
            salvar_dado(SERVICOS_FILE, {"descricao": descricao, "valor": valor})
            st.success("✅ Serviço salvo com sucesso!")
            st.experimental_rerun()
        else:
            st.error("❌ Preencha todos os campos corretamente.")

    st.subheader("📄 Serviços Cadastrados")
    servicos_df = carregar_dados(SERVICOS_FILE)

    if not servicos_df.empty:
        for i, row in servicos_df.iterrows():
            st.markdown(f"**{row['descricao']}** - R$ {row['valor']:.2f}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Editar", key=f"edit_servico_{i}"):
                    with st.form(f"form_servico_{i}"):
                        desc_edit = st.text_input("Descrição", value=row["descricao"])
                        valor_edit = st.number_input("Valor", value=float(row["valor"]))
                        if st.form_submit_button("Salvar Alterações"):
                            atualizar_dado(SERVICOS_FILE, i, {
                                "descricao": desc_edit, "valor": valor_edit
                            })
                            st.success("✅ Serviço atualizado!")
                            st.experimental_rerun()
            with col2:
                if st.button("🗑️ Excluir", key=f"del_servico_{i}"):
                    deletar_dado(SERVICOS_FILE, i)
                    st.warning("⚠️ Serviço excluído.")
                    st.experimental_rerun()
    else:
        st.info("Nenhum serviço cadastrado.")

# Página 3 - Ordens de Serviço
elif pagina == "📄 Gerar Ordem de Serviço":
    st.title("Gerar Ordem de Serviço")

    clientes_df = carregar_dados(CLIENTES_FILE)
    servicos_df = carregar_dados(SERVICOS_FILE)

    if clientes_df.empty or servicos_df.empty:
        st.warning("⚠️ Cadastre ao menos um cliente e um serviço antes.")
    else:
        cliente_nome = st.selectbox("Selecione o Cliente", clientes_df["nome"])
        servico_desc = st.selectbox("Selecione o Serviço", servicos_df["descricao"])
        aparelho = st.text_input("Aparelho/Equipamento")
        data = datetime.now().strftime("%d/%m/%Y")

        if st.button("Gerar PDF"):
            cliente = clientes_df[clientes_df["nome"] == cliente_nome].iloc[0]
            servico = servicos_df[servicos_df["descricao"] == servico_desc].iloc[0]

            # Gerar PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="ORDEM DE SERVIÇO", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Data: {data}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt="Cliente:", ln=True)
            pdf.cell(200, 10, txt=f"Nome: {cliente['nome']}", ln=True)
            pdf.cell(200, 10, txt=f"Telefone: {cliente['telefone']}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Endereço: {cliente['endereco']}")
            pdf.ln(5)
            pdf.cell(200, 10, txt="Serviço:", ln=True)
            pdf.cell(200, 10, txt=f"Descrição: {servico['descricao']}", ln=True)
            pdf.cell(200, 10, txt=f"Valor: R$ {servico['valor']:.2f}", ln=True)
            pdf.ln(5)
            pdf.cell(200, 10, txt=f"Aparelho: {aparelho}", ln=True)

            nome_arquivo = f"ordem_{cliente['nome'].replace(' ', '_')}_{data.replace('/', '-')}.pdf"
            pdf.output(nome_arquivo)

            salvar_dado(ORDENS_FILE, {
                "cliente": cliente['nome'],
                "servico": servico['descricao'],
                "aparelho": aparelho,
                "data": data
            })

            with open(nome_arquivo, "rb") as f:
                st.download_button("📄 Baixar PDF da Ordem", f, file_name=nome_arquivo, mime="application/pdf")

    st.subheader("📁 Ordens de Serviço Salvas")
    ordens_df = carregar_dados(ORDENS_FILE)

    if not ordens_df.empty:
        for i, row in ordens_df.iterrows():
            st.markdown(f"📌 **{row['cliente']}** - {row['servico']} - {row['aparelho']} - {row['data']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Editar", key=f"edit_ordem_{i}"):
                    with st.form(f"form_ordem_{i}"):
                        cliente_edit = st.selectbox("Cliente", clientes_df["nome"], index=clientes_df[clientes_df["nome"] == row["cliente"]].index[0])
                        servico_edit = st.selectbox("Serviço", servicos_df["descricao"], index=servicos_df[servicos_df["descricao"] == row["servico"]].index[0])
                        aparelho_edit = st.text_input("Aparelho", row["aparelho"])
                        data_edit = st.text_input("Data", row["data"])
                        if st.form_submit_button("Salvar Alterações"):
                            atualizar_dado(ORDENS_FILE, i, {
                                "cliente": cliente_edit,
                                "servico": servico_edit,
                                "aparelho": aparelho_edit,
                                "data": data_edit
                            })
                            st.success("✅ Ordem atualizada!")
                            st.experimental_rerun()
            with col2:
                if st.button("🗑️ Excluir", key=f"del_ordem_{i}"):
                    deletar_dado(ORDENS_FILE, i)
                    st.warning("⚠️ Ordem excluída.")
                    st.experimental_rerun()
    else:
        st.info("Nenhuma ordem cadastrada.")
