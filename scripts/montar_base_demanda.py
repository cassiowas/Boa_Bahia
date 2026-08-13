"""
Junta temperatura, feriados e eventos confirmados de cada loja em uma
única tabela diária, pronta para ser cruzada com o histórico de vendas já
validado. É esse arquivo que alimenta o Cowork para gerar a sugestão de
pedido semanal.

Lê as saídas de scripts/coleta_temperatura_feriados.py e do comando
/buscar_eventos. Eventos só entram na tabela se já tiverem sido
confirmados na curadoria (coluna `confirmado` preenchida com um valor
afirmativo); eventos ainda não revisados ou rejeitados ficam de fora.

Uso:
    python scripts/montar_base_demanda.py

Saída (ver convenção em CLAUDE.md, outputs/<script>/<loja>/):
    outputs/montar_base_demanda/butanta_shopping/base_demanda.csv
    outputs/montar_base_demanda/shopping_metro_santa_cruz/base_demanda.csv
"""

import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPERATURA_FERIADOS_DIR = ROOT / "outputs" / "coleta_temperatura_feriados"
EVENTOS_DIR = ROOT / "outputs" / "buscar_eventos"
OUTPUT_DIR = ROOT / "outputs" / "montar_base_demanda"

LOJAS = [
    ("butanta_shopping", "Butantã Shopping"),
    ("shopping_metro_santa_cruz", "Shopping Metro Santa Cruz"),
]

CONFIRMADOS_VALIDOS = {"sim", "s", "yes", "true", "1"}


def ler_csv(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def agregar_temperatura_diaria(linhas: list[dict]) -> dict[str, dict]:
    leituras_por_dia = defaultdict(list)
    for linha in linhas:
        dia = linha["data_hora"][:10]
        leituras_por_dia[dia].append(float(linha["temp_c"]))
    return {
        dia: {
            "temp_min_c": round(min(temps), 1),
            "temp_max_c": round(max(temps), 1),
            "temp_media_c": round(sum(temps) / len(temps), 1),
        }
        for dia, temps in leituras_por_dia.items()
    }


def indexar_feriados(linhas: list[dict]) -> dict[str, dict]:
    por_dia: dict[str, dict] = {}
    for linha in linhas:
        info = por_dia.setdefault(linha["data"], {"nomes": [], "tipos": []})
        info["nomes"].append(linha["nome"])
        info["tipos"].append(linha["tipo"])
    return por_dia


def dias_do_evento(data_evento: str) -> list[str]:
    """Expande uma data única ou um período ("AAAA-MM-DD a AAAA-MM-DD")."""
    data_evento = data_evento.strip()
    if " a " in data_evento:
        inicio_str, fim_str = (parte.strip() for parte in data_evento.split(" a ", 1))
        inicio, fim = date.fromisoformat(inicio_str), date.fromisoformat(fim_str)
        dias, atual = [], inicio
        while atual <= fim:
            dias.append(atual.isoformat())
            atual += timedelta(days=1)
        return dias
    return [date.fromisoformat(data_evento).isoformat()]


def indexar_eventos(linhas: list[dict]) -> dict[str, dict]:
    por_dia: dict[str, dict] = {}
    for linha in linhas:
        if linha.get("confirmado", "").strip().lower() not in CONFIRMADOS_VALIDOS:
            continue
        for dia in dias_do_evento(linha["data_evento"]):
            info = por_dia.setdefault(dia, {"nomes": [], "tipos": [], "locais": []})
            info["nomes"].append(linha["evento"])
            info["tipos"].append(linha["tipo"])
            info["locais"].append(linha["local"])
    return por_dia


def montar_tabela(loja_slug: str, loja_nome: str) -> list[dict]:
    base_temp_feriados = TEMPERATURA_FERIADOS_DIR / loja_slug
    temperaturas = agregar_temperatura_diaria(ler_csv(base_temp_feriados / "temperatura.csv"))
    feriados = indexar_feriados(ler_csv(base_temp_feriados / "feriados.csv"))
    eventos = indexar_eventos(ler_csv(EVENTOS_DIR / loja_slug / "eventos.csv"))

    dias = sorted(set(temperaturas) | set(feriados) | set(eventos))

    tabela = []
    for dia in dias:
        temp = temperaturas.get(dia, {})
        feriado = feriados.get(dia)
        evento = eventos.get(dia)
        tabela.append(
            {
                "data": dia,
                "loja": loja_nome,
                "temp_min_c": temp.get("temp_min_c", ""),
                "temp_max_c": temp.get("temp_max_c", ""),
                "temp_media_c": temp.get("temp_media_c", ""),
                "feriado": 1 if feriado else 0,
                "feriado_nome": "; ".join(feriado["nomes"]) if feriado else "",
                "feriado_tipo": "; ".join(feriado["tipos"]) if feriado else "",
                "evento": 1 if evento else 0,
                "evento_nome": "; ".join(evento["nomes"]) if evento else "",
                "evento_tipo": "; ".join(evento["tipos"]) if evento else "",
                "evento_local": "; ".join(evento["locais"]) if evento else "",
            }
        )
    return tabela


def salvar_csv(linhas: list[dict], caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        campos = list(linhas[0].keys()) if linhas else []
        writer = csv.DictWriter(arquivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(linhas)


def main() -> None:
    for slug, nome in LOJAS:
        print(f"Montando base de {nome}...")
        tabela = montar_tabela(slug, nome)
        destino = OUTPUT_DIR / slug / "base_demanda.csv"
        salvar_csv(tabela, destino)
        print(f"  {len(tabela)} dias -> {destino}")


if __name__ == "__main__":
    main()
