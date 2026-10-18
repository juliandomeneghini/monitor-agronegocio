import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# Configuração da página do Streamlit
st.set_page_config(page_title="Monitor de Agronegócio", page_icon="📈", layout="wide")

st.title("🌾 Monitor de Cotações Agrícolas & Impacto Climático")
st.markdown(
    "Este painel apresenta dados raspados automaticamente do CEPEA e armazenados em banco de dados relacional."
)

# Conectar ao banco de dados SQLite
db_path = "data/agri_climate.db"

if not os.path.exists(db_path):
    st.warning(
        "⚠️ Banco de dados ainda não encontrado. Execute o script `scraper_cepea.py` primeiro para coletar os dados!"
    )
else:
    engine = create_engine(f"sqlite:///{db_path}")

    # Ler os dados da tabela
    try:
        df = pd.read_sql("cotacoes_agricolas", con=engine)

        if df.empty:
            st.info("O banco de dados está vazio no momento.")
        else:
            # Métricas principais (KPIs) no topo
            st.subheader("📊 Indicadores Recentes (Soja)")

            # Converter coluna de data
            df["data"] = pd.to_datetime(df["data"])
            df = df.sort_values("data", ascending=False)

            ultimo_preco = df.iloc[0]["preco_brl"]
            preco_anterior = df.iloc[1]["preco_brl"] if len(df) > 1 else ultimo_preco
            variacao = ((ultimo_preco - preco_anterior) / preco_anterior) * 100

            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Preço Atual (BRL / SC 60kg)",
                f"R$ {ultimo_preco:.2f}",
                f"{variacao:.2f}%",
            )
            col2.metric("Commodity Monitorada", "Soja (CEPEA)")
            col3.metric("Total de Registros Históricos", len(df))

            # Gráfico de evolução de preços
            st.markdown("---")
            st.subheader("📈 Evolução Histórica de Preços (BRL)")

            # O Streamlit plota gráficos de linha de forma muito fácil
            df_chart = df.sort_values("data")
            st.line_chart(df_chart.set_index("data")["preco_brl"])

            # Mostrar tabela com os dados brutos se o usuário quiser expandir
            with st.expander("Ver dados brutos extraídos"):
                st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao ler o banco de dados: {e}")
