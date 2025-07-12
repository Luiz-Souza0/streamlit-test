import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os

# Arquivos de dados
CLIENTES_FILE = "clientes.csv"
SERVICOS_FILE = "servicos.csv"
ORDENS_FILE = "ordens.csv"

# Inicializa arquivos se não existirem
for file, columns in [
    (CLIENTES_FILE, ["nome", "telefone", "endereco"]),
    (SERVICOS_FILE, ["descricao", "valor"]),
    (ORDENS_FILE, ["cliente", "servico", "aparelho", "data"])
]:
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

# Funções utilitárias
def carregar_dados(arquivo):
    return pd.read_csv(arquivo)

def salvar_dado(arquivo, novo_dado):
    df = carregar_dados(arquivo)
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    df.to_csv(arquivo, index=False)

# Página
pagina = st.sidebar.selectbox("📚 Navegação", ["📋 Cadastrar Cliente", "🛠 Cadastrar Serviço", "📄 Gerar Ordem de Serviço"])

# Página 1 - Cadastro de Cliente
if pagina == "📋 Cadastrar Cliente":
    st.title("Cadastro de Cliente")
    nome = st.text_input("Nome do Cliente")
    telefone = st.text_input("Telefone")
    endereco = st.text_area("Endereço")

    if st.button("Salvar Cliente"):
        if nome and telefone and endereco:
            salvar_dado(CLIENTES_FILE, {
                "nome": nome,
                "telefone": telefone,
                "endereco": endereco
            })
            st.success("✅ Cliente salvo com sucesso!")
        else:
            st.error("❌ Todos os campos são obrigatórios.")

    st.subheader("📄 Clientes Cadastrados")
    st.dataframe(carregar_dados(CLIENTES_FILE))

# Página 2 - Cadastro de Serviço
elif pagina == "🛠 Cadastrar Serviço":
    st.title("Cadastro de Serviço")
    descricao = st.text_input("Descrição do Serviço")
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

    if st.button("Salvar Serviço"):
        if descricao and valor > 0:
            salvar_dado(SERVICOS_FILE, {
                "descricao": descricao,
                "valor": valor
            })
            st.success("✅ Serviço salvo com sucesso!")
        else:
            st.error("❌ Preencha todos os campos corretamente.")

    st.subheader("📄 Serviços Cadastrados")
    st.dataframe(carregar_dados(SERVICOS_FILE))

# Página 3 - Gerar Ordem de Serviço
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

            # Cria PDF
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

            # Salva ordem no CSV
            salvar_dado(ORDENS_FILE, {
                "cliente": cliente['nome'],
                "servico": servico['descricao'],
                "aparelho": aparelho,
                "data": data
            })

            with open(nome_arquivo, "rb") as f:
                st.download_button("📄 Baixar PDF da Ordem", f, file_name=nome_arquivo, mime="application/pdf")

    # Mostrar ordens salvas
    st.subheader("📁 Ordens de Serviço Salvas")
    st.dataframe(carregar_dados(ORDENS_FILE))
