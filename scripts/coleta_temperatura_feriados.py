"""
Coleta temperatura diária local e feriados (nacionais, regionais e locais)
para Butantã Shopping e Shopping Metro Santa Cruz.

A temperatura vem da Open-Meteo Historical Weather API (gratuita, sem
necessidade de chave) usando as coordenadas aproximadas de cada loja. Os
feriados são calculados localmente (não dependem de rede) e classificados
em "nacional", "regional" (estado de São Paulo) e "local" (município de
São Paulo, onde ambas as lojas estão situadas).

Uso:
    python scripts/coleta_temperatura_feriados.py
    python scripts/coleta_temperatura_feriados.py --inicio 2023-01-01 --fim 2025-12-31

Saída (ver convenção em CLAUDE.md, outputs/<script>/<loja>/):
    outputs/coleta_temperatura_feriados/butanta_shopping/temperatura.csv
    outputs/coleta_temperatura_feriados/butanta_shopping/feriados.csv
    outputs/coleta_temperatura_feriados/shopping_metro_santa_cruz/temperatura.csv
    outputs/coleta_temperatura_feriados/shopping_metro_santa_cruz/feriados.csv
"""

import argparse
import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs" / "coleta_temperatura_feriados"

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


@dataclass
class Loja:
    slug: str
    nome: str
    latitude: float
    longitude: float


LOJAS = [
    Loja("butanta_shopping", "Butantã Shopping", -23.5711, -46.7135),
    Loja("shopping_metro_santa_cruz", "Shopping Metro Santa Cruz", -23.5895, -46.6389),
]


def buscar_temperatura(loja: Loja, inicio: date, fim: date) -> list[dict]:
    params = {
        "latitude": loja.latitude,
        "longitude": loja.longitude,
        "start_date": inicio.isoformat(),
        "end_date": fim.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean",
        "timezone": "America/Sao_Paulo",
    }
    resp = requests.get(OPEN_METEO_ARCHIVE_URL, params=params, timeout=30)
    resp.raise_for_status()
    diario = resp.json()["daily"]
    return [
        {
            "data": data_str,
            "temp_max_c": diario["temperature_2m_max"][i],
            "temp_min_c": diario["temperature_2m_min"][i],
            "temp_media_c": diario["temperature_2m_mean"][i],
        }
        for i, data_str in enumerate(diario["time"])
    ]


def calcular_pascoa(ano: int) -> date:
    """Data da Páscoa no calendário gregoriano (algoritmo de Gauss/Meeus)."""
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def feriados_do_ano(ano: int) -> list[dict]:
    pascoa = calcular_pascoa(ano)
    feriados = [
        (date(ano, 1, 1), "Confraternização Universal", "nacional"),
        (pascoa - timedelta(days=48), "Carnaval (segunda-feira)", "nacional"),
        (pascoa - timedelta(days=47), "Carnaval (terça-feira)", "nacional"),
        (pascoa - timedelta(days=2), "Sexta-feira Santa", "nacional"),
        (date(ano, 4, 21), "Tiradentes", "nacional"),
        (date(ano, 5, 1), "Dia do Trabalho", "nacional"),
        (pascoa + timedelta(days=60), "Corpus Christi", "nacional"),
        (date(ano, 9, 7), "Independência do Brasil", "nacional"),
        (date(ano, 10, 12), "Nossa Senhora Aparecida", "nacional"),
        (date(ano, 11, 2), "Finados", "nacional"),
        (date(ano, 11, 15), "Proclamação da República", "nacional"),
        (date(ano, 12, 25), "Natal", "nacional"),
        (date(ano, 7, 9), "Revolução Constitucionalista de 1932", "regional"),
        (date(ano, 1, 25), "Aniversário da cidade de São Paulo", "local"),
    ]
    # Dia da Consciência Negra: feriado nacional a partir de 2024
    # (Lei 14.759/2023); antes disso, feriado municipal em São Paulo
    # (Lei municipal 13.707/2003).
    if ano >= 2024:
        feriados.append((date(ano, 11, 20), "Dia da Consciência Negra", "nacional"))
    else:
        feriados.append((date(ano, 11, 20), "Dia da Consciência Negra", "local"))
    feriados.sort(key=lambda item: item[0])
    return [{"data": d.isoformat(), "nome": nome, "tipo": tipo} for d, nome, tipo in feriados]


def feriados_no_periodo(inicio: date, fim: date) -> list[dict]:
    todos = [f for ano in range(inicio.year, fim.year + 1) for f in feriados_do_ano(ano)]
    return [f for f in todos if inicio.isoformat() <= f["data"] <= fim.isoformat()]


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        campos = list(linhas[0].keys()) if linhas else []
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ontem = date.today() - timedelta(days=1)
    parser.add_argument("--inicio", type=date.fromisoformat, default=ontem - timedelta(days=730), help="Data inicial (AAAA-MM-DD). Padrão: 2 anos atrás.")
    parser.add_argument("--fim", type=date.fromisoformat, default=ontem, help="Data final (AAAA-MM-DD). Padrão: ontem.")
    args = parser.parse_args()

    feriados = feriados_no_periodo(args.inicio, args.fim)

    for loja in LOJAS:
        print(f"Coletando dados de {loja.nome}...")
        temperaturas = buscar_temperatura(loja, args.inicio, args.fim)
        destino = OUTPUT_DIR / loja.slug
        salvar_csv(temperaturas, destino / "temperatura.csv")
        salvar_csv(feriados, destino / "feriados.csv")
        print(f"  {len(temperaturas)} dias de temperatura -> {destino / 'temperatura.csv'}")
        print(f"  {len(feriados)} feriados -> {destino / 'feriados.csv'}")


if __name__ == "__main__":
    main()
