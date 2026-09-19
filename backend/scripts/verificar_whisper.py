#!/usr/bin/env python3
"""CLI de verificação do Whisper para B07-A — não é importado pela API.

Roda num ambiente virtual isolado (ver `requirements-whisper.txt`, ao lado
deste arquivo). `backend/app/` nunca importa este script nem os pacotes de
transcrição; a saúde e a análise por texto continuam sem essa dependência.

Uso:

    .venv-whisper/bin/python backend/scripts/verificar_whisper.py inventario

    .venv-whisper/bin/python backend/scripts/verificar_whisper.py transcrever \\
        --audio caminho/para/audio.wav --modelo base --idioma pt \\
        --pesos /caminho/fora/do/repositorio/cache-whisper

`--pesos` é obrigatório em `transcrever` para que o destino dos pesos do
modelo (centenas de MB) seja uma escolha explícita. Recomenda-se um caminho
fora do repositório; o script **não** valida isso — só exige o argumento.

`--experimento-forcado` reproduz exatamente o experimento da seção 4 do
relatório (revisão B07-A-R02): `no_speech_threshold=0.9`,
`logprob_threshold=None` e `condition_on_previous_text=False`. Sem a flag,
valem os padrões do Whisper. Os três parâmetros juntos são o que faz o
modelo emitir texto para um áudio que ele classifica como não-fala; só o
threshold, sem os outros dois, produz alucinação multilíngue e não
determinística (o fallback de temperatura do Whisper passa a amostrar).
A flag serve para inspecionar o que o modelo "ouviria", não para obter
uma transcrição melhor.

Códigos de saída de `transcrever`: 0 sucesso; 1 falha na transcrição
(ex.: arquivo inválido); 2 falha na preparação (carga do modelo, diretório
de pesos). Outras falhas (import, permissões) não são capturadas e saem com
o traceback normal do Python.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import resource
import shutil
import subprocess
import sys
import time


def _rodar(comando: list[str], timeout: float = 10.0) -> str:
    """Executa um comando auxiliar e devolve stdout, ou uma mensagem de indisponibilidade."""

    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=timeout)
        return resultado.stdout.strip() or resultado.stderr.strip()
    except FileNotFoundError:
        return "NAO_ENCONTRADO"
    except Exception as excecao:  # noqa: BLE001 — inventário tolera qualquer falha de sondagem
        return f"indisponivel ({type(excecao).__name__}: {excecao})"


def _memoria_total_mb() -> str:
    try:
        with open("/proc/meminfo", encoding="utf-8") as arquivo:
            for linha in arquivo:
                if linha.startswith("MemTotal:"):
                    kb = int(linha.split()[1])
                    return f"{kb / 1024:.0f} MB"
    except OSError:
        pass
    return "indisponivel"


def inventario() -> None:
    """Lista hardware/software relevantes para decidir viabilidade, sem imprimir segredos."""

    print("== Ambiente ==")
    print("Python:", sys.version.split()[0], "-", sys.executable)
    print("Plataforma:", platform.platform())
    print("CPUs logicas:", os.cpu_count())
    print("RAM total:", _memoria_total_mb())

    print("\n== FFmpeg/FFprobe ==")
    print("ffmpeg:", shutil.which("ffmpeg") or "NAO_ENCONTRADO")
    print("ffprobe:", shutil.which("ffprobe") or "NAO_ENCONTRADO")

    print("\n== GPU (melhor esforço; ausência de saída não confirma ausência de GPU) ==")
    saida_lspci = _rodar(["lspci"], timeout=5)
    linhas_gpu = [linha for linha in saida_lspci.splitlines() if "VGA" in linha or "3D controller" in linha]
    print("\n".join(linhas_gpu) if linhas_gpu else "nenhuma controladora de vídeo detectada via lspci (ou lspci indisponível)")

    print("\n== PyTorch ==")
    try:
        import torch  # type: ignore[import-not-found]

        print("torch:", torch.__version__)
        print("CUDA disponivel:", torch.cuda.is_available())
    except ImportError:
        print("torch nao instalado neste interpretador (esperado fora do venv do experimento)")

    print("\n== Espaco em disco (diretorio atual) ==")
    uso = shutil.disk_usage(".")
    print(f"livre: {uso.free / (1024**3):.1f} GB de {uso.total / (1024**3):.1f} GB")


def _sha256(caminho: str) -> str:
    resumo = hashlib.sha256()
    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


PARAMETROS_EXPERIMENTO_FORCADO = {
    "no_speech_threshold": 0.9,
    "logprob_threshold": None,
    "condition_on_previous_text": False,
}


def transcrever(
    caminho_audio: str,
    modelo_nome: str,
    idioma: str,
    diretorio_pesos: str,
    experimento_forcado: bool,
) -> int:
    """Carrega o modelo, transcreve o áudio indicado e imprime métricas reais.

    Devolve o código de saída do processo: 0 em sucesso, 1 se a transcrição
    levantar exceção, 2 se a preparação (diretório de pesos, carga do modelo)
    falhar. Quem chama decide o que fazer com a falha; este script não
    inventa um resultado substituto.
    """

    import whisper  # type: ignore[import-not-found]

    print("== Configuracao ==")
    print(f"audio: {caminho_audio}")
    if os.path.isfile(caminho_audio):
        print(f"sha256 do audio: {_sha256(caminho_audio)}")
    else:
        print("sha256 do audio: (arquivo nao encontrado — a transcricao vai falhar abaixo)")
    print(f"modelo: {modelo_nome}")
    print(f"idioma configurado: {idioma} (deteccao automatica de idioma desligada)")
    if experimento_forcado:
        print(f"parametros forcados: {PARAMETROS_EXPERIMENTO_FORCADO}")
    else:
        print("parametros de decodificacao: padroes do Whisper")
    print(f"diretorio de pesos: {diretorio_pesos}")

    try:
        os.makedirs(diretorio_pesos, exist_ok=True)
        inicio = time.perf_counter()
        modelo = whisper.load_model(modelo_nome, download_root=diretorio_pesos)
        tempo_carga = time.perf_counter() - inicio
    except Exception as excecao:  # noqa: BLE001 — preparacao pode falhar por nome, rede ou disco
        print(f"FALHA na preparacao (pesos/modelo): {type(excecao).__name__}: {excecao}")
        return 2

    duracao_audio = _rodar(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", caminho_audio]
    )

    opcoes = {"language": idioma, "fp16": False}
    if experimento_forcado:
        opcoes.update(PARAMETROS_EXPERIMENTO_FORCADO)

    inicio = time.perf_counter()
    try:
        resultado = modelo.transcribe(caminho_audio, **opcoes)
    except Exception as excecao:  # noqa: BLE001 — reportar qualquer falha real do transcritor
        print(f"FALHA na transcricao: {type(excecao).__name__}: {excecao}")
        return 1
    tempo_transcricao = time.perf_counter() - inicio

    pico_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

    print("== Resultado ==")
    print(f"tempo de carga do modelo: {tempo_carga:.2f}s")
    print(f"duracao do audio (ffprobe): {duracao_audio}s")
    print(f"tempo de transcricao: {tempo_transcricao:.2f}s")
    print(f"pico de RSS do processo: {pico_rss_mb:.0f} MB")
    print(f"idioma no resultado: {resultado.get('language')} (ecoa o configurado; nao e deteccao)")
    print(f"segmentos: {len(resultado['segments'])}")
    for segmento in resultado["segments"]:
        prob_sem_fala = segmento.get("no_speech_prob")
        prob_texto = f"{prob_sem_fala:.2f}" if prob_sem_fala is not None else "?"
        print(f"  [{segmento['start']:.1f}-{segmento['end']:.1f}] no_speech_prob={prob_texto} {segmento['text']!r}")
    print("texto completo:")
    print(resultado["text"])
    return 0


def main() -> None:
    analisador = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subcomandos = analisador.add_subparsers(dest="comando", required=True)

    subcomandos.add_parser("inventario", help="Lista hardware/software disponível para o experimento.")

    comando_transcrever = subcomandos.add_parser("transcrever", help="Transcreve um arquivo de áudio com o Whisper.")
    comando_transcrever.add_argument("--audio", required=True, help="Caminho do arquivo de áudio a transcrever.")
    comando_transcrever.add_argument("--modelo", default="base", help="Nome do modelo Whisper (padrão: base).")
    comando_transcrever.add_argument("--idioma", default="pt", help="Código do idioma esperado (padrão: pt).")
    comando_transcrever.add_argument(
        "--pesos",
        required=True,
        help="Diretório para os pesos do modelo (obrigatório; recomendado fora do repositório — o script não valida o caminho).",
    )
    comando_transcrever.add_argument(
        "--experimento-forcado",
        action="store_true",
        help=(
            "Reproduz o experimento forçado do relatório (no_speech_threshold=0.9, "
            "logprob_threshold=None, condition_on_previous_text=False). Não é o modo normal."
        ),
    )

    argumentos = analisador.parse_args()

    if argumentos.comando == "inventario":
        inventario()
    elif argumentos.comando == "transcrever":
        codigo_saida = transcrever(
            argumentos.audio,
            argumentos.modelo,
            argumentos.idioma,
            argumentos.pesos,
            argumentos.experimento_forcado,
        )
        sys.exit(codigo_saida)


if __name__ == "__main__":
    main()
