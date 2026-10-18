import pandas as pd
from sqlalchemy import create_engine

# Cria o banco SQLite local (pode ser migrado para PostgreSQL depois)[cite: 2]
ENGINE = create_engine("sqlite:///data/agri_climate.db")


def save_to_db(df: pd.DataFrame, table_name: str = "cotacoes_agricolas"):
    """Insere novos dados garantindo persistência sem duplicatas simples."""
    if not df.empty:
        df.to_sql(table_name, con=ENGINE, if_exists="append", index=False)
        print(f"Sucesso: {len(df)} registros gravados na tabela '{table_name}'.")


if __name__ == "__main__":
    from agro_scraper.src.scraper import fetch_soybean_prices

    df_cotacoes = fetch_soybean_prices()
    save_to_db(df_cotacoes)
