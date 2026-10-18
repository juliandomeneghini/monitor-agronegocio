import os
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine


def parse_float(val_str):
    """Converte valores no formato brasileiro '1.234,56' para float."""
    try:
        return float(val_str.replace(".", "").replace(",", "."))
    except (ValueError, AttributeError):
        return None


def fetch_soybean_prices():
    print("Acessando o site do CEPEA...")
    url = "https://www.cepea.esalq.usp.br/br/indicador/soja.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao acessar o site: Status {response.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "imagenet-indicador1"})

    data = []
    if table:
        rows = table.find_all("tr")[1:]  # Pula o cabeçalho
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                data_str = cols[0].text.strip()
                preco_brl = parse_float(cols[1].text.strip())
                preco_usd = parse_float(cols[2].text.strip())

                try:
                    data_obj = datetime.strptime(data_str, "%d/%m/%Y").date()
                except ValueError:
                    continue

                data.append(
                    {
                        "data": data_obj,
                        "commodity": "Soja",
                        "preco_brl": preco_brl,
                        "preco_usd": preco_usd,
                    }
                )

    return pd.DataFrame(data)


def save_to_db(df):
    """Salva os dados extraídos em um banco de dados SQLite local."""
    if df.empty:
        print("Nenhum dado para salvar.")
        return

    # Cria a pasta data se não existir
    os.makedirs("data", exist_ok=True)

    engine = create_engine("sqlite:///data/agri_climate.db")
    df.to_sql("cotacoes_agricolas", con=engine, if_exists="append", index=False)
    print(f"Sucesso! {len(df)} registros salvos no banco de dados.")


if __name__ == "__main__":
    df_cotacoes = fetch_soybean_prices()
    if not df_cotacoes.empty:
        print("Amostra dos dados extraídos:")
        print(df_cotacoes.head())
        save_to_db(df_cotacoes)
