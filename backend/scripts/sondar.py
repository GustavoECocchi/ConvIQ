"""Sondagem da análise de texto pela composição real (`compor_analise_texto`).

Uso, a partir de qualquer pasta:

    python backend/scripts/sondar.py "Queremos conhecer o Fluig." "Vamos cancelar o contrato."
    python backend/scripts/sondar.py --vinculo prospect "Vamos cancelar o contrato."
    python backend/scripts/sondar.py --json "Estamos insatisfeitos com o suporte."

Importa o `app` do checkout em que este arquivo está, e não o de uma instalação
editável do venv (que pode apontar para outra pasta). Confere, para cada frase,
que todo recorte de evidência é literal e que as referências existem.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RAIZ_BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ_BACKEND))

from app.schemas.reuniao import AnaliseTextoRequest  # noqa: E402
from app.services.analise import compor_analise_texto  # noqa: E402


def _trechos(resposta, ids: list[str]) -> list[str]:
    por_id = {e.id: e.trecho for e in resposta.evidencias}
    return [por_id[i] for i in ids]


def sondar(transcricao: str, vinculo: str) -> dict:
    resposta = compor_analise_texto(
        AnaliseTextoRequest(titulo="sonda", empresa="sonda", vinculo=vinculo, transcricao=transcricao)
    )
    ids = {e.id for e in resposta.evidencias}
    for e in resposta.evidencias:
        if resposta.transcricao[e.inicio:e.fim] != e.trecho:
            raise AssertionError(f"recorte não literal: {e}")
    referencias = list(resposta.churn.evidencias)
    referencias += [i for o in resposta.oportunidades for i in o.evidencias]
    referencias += [i for r in resposta.recomendacoes for i in r.evidencias]
    if not set(referencias) <= ids:
        raise AssertionError("referência de evidência inexistente")
    return {
        "app": str(Path(sys.modules["app"].__file__).parent),
        "transcricao": transcricao,
        "vinculo": vinculo,
        "versao": resposta.versao_analise,
        "sentimento": resposta.sentimento.value,
        "churn": resposta.churn.situacao.value,
        "churn_evidencias": _trechos(resposta, resposta.churn.evidencias),
        "oportunidades": [_trechos(resposta, o.evidencias) for o in resposta.oportunidades],
        "produtos": resposta.produtos,
        "concorrentes": resposta.concorrentes,
        "recomendacoes": [r.evidencias for r in resposta.recomendacoes],
        "evidencias": [(e.id, e.trecho, e.inicio, e.fim) for e in resposta.evidencias],
    }


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analisador.add_argument("frases", nargs="+", help="transcrições a analisar")
    analisador.add_argument("--vinculo", default="cliente", choices=["cliente", "prospect", "nao_informado"])
    analisador.add_argument("--json", action="store_true", help="saída completa em JSON")
    args = analisador.parse_args()

    resultados = [sondar(frase, args.vinculo) for frase in args.frases]
    if args.json:
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
        return 0
    print(f"app: {Path(sys.modules['app'].__file__).parent}  versao_analise: {resultados[0]['versao']}")
    for r in resultados:
        print(f"\n{r['transcricao']!r} [{r['vinculo']}]")
        print(f"  sentimento={r['sentimento']}  churn={r['churn']} {r['churn_evidencias']}")
        print(f"  oportunidades={r['oportunidades']}  produtos={r['produtos']}  concorrentes={r['concorrentes']}")
        print(f"  recomendacoes(evidencias)={r['recomendacoes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
