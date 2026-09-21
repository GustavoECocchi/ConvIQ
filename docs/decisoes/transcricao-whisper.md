# B07-A — Viabilidade do Whisper gratuito

Executado por Claude Sonnet em 19/09/2026 (B07-A-01), a partir do prompt
preparado pelo Codex em PLN01-03; **revisado e corrigido por Claude Opus em
19/09/2026 (B07-A-03)** — receita de instalação corrigida e verificada em
venv vazio (R01), ensaios refeitos com comandos exatos, hashes e a flag
`--experimento-forcado` do script (R02); **revisão independente por Claude
Opus em 21/09/2026 (B07-A-06)** reproduziu instalação e ensaios a partir
de venv vazio e corrigiu R03 (`.gitignore`) e R04 (códigos de saída
documentados) — ver seção 10. Cobre só B07-A: verificar se o
Whisper (open source) roda de verdade neste ambiente e recomendar uma
configuração gratuita reproduzível para C02-A. Não altera `backend/app/`,
o contrato de texto (C01) nem o runtime da API — tudo aqui rodou num
ambiente virtual isolado, fora de `backend/pyproject.toml`.

**Resultado resumido: entrega PARCIAL.** O pipeline mecânico (ambiente →
instalação → modelo → transcrição → tratamento de erro) está provado, com
medições reais. A validação de qualidade com fala humana real — o critério
central de aceite — **não foi concluída**: só havia disponível uma amostra
sintetizada por texto-para-voz, que o próprio Whisper trata como pouco
confiável (ver seção "Amostra sintética"). Falta uma gravação real para
fechar B07-A por completo.

## 1. Ambiente verificado

| Item | Valor observado |
|---|---|
| CPU | Intel Core i5-1335U (13ª geração), 12 CPUs lógicas |
| RAM total | 7608 MB (≈7,4 GiB). No momento do inventário, `free -h` mostrava ~150 MB **free** (não alocada) e ~2,2 GiB **available** (livre + cache reclamável). Para capacidade, o número que importa é o *available* — o *free* baixo é normal em Linux com cache de disco |
| GPU | Intel Iris Xe (integrada); **sem GPU NVIDIA/CUDA** |
| Disco | 419 GB livres de 474 GB no filesystem do projeto |
| FFmpeg / FFprobe | 8.1.2, ambos presentes em `/usr/bin` |
| Python do sistema (API) | 3.14.7 — única versão disponível, sem `pyenv`/`conda` |

Reproduzível com `backend/scripts/verificar_whisper.py inventario` (ver
seção 5).

## 2. Instalação — achado importante sobre cota de disco

Primeira tentativa (`pip install openai-whisper` direto, sem índice
específico) **falhou com `OSError: [Errno 122] Disk quota exceeded`**: o
`pip` resolve `torch` (dependência do Whisper) para a build padrão, que
inclui pacotes NVIDIA CUDA completos — `nvidia-cublas` (423 MB),
`nvidia-cudnn` (553 MB), o próprio `torch` (554 MB), `nvidia-cusparselt`
(170 MB), `nvidia-nccl` (216 MB), `nvidia-cufft` (214 MB),
`nvidia-cusolver` (200 MB) e mais — **vários gigabytes só de download**,
para pacotes CUDA inúteis numa máquina sem GPU NVIDIA.

Correção: fixar a build **CPU-only** do PyTorch. Receita reproduzível, em
um único passo, a partir de um ambiente vazio:

```bash
python3 -m venv .venv-whisper
.venv-whisper/bin/pip install --no-cache-dir -r backend/scripts/requirements-whisper.txt
```

`backend/scripts/requirements-whisper.txt` usa
`--extra-index-url https://download.pytorch.org/whl/cpu` (o PyPI continua
sendo o índice primário) e pina `torch==2.14.0+cpu` — o rótulo local `+cpu`
só existe no índice CPU do PyTorch, então o `pip` não tem como resolver
para o `torch` padrão com CUDA.

**Revisão B07-A-R03 (Opus, 21/09/2026):** executada na raiz do repositório,
a receita acima cria `.venv-whisper/` (~2,1 GB) e o `.gitignore` só cobria
`.venv/` e `venv/` — o diretório aparecia como não rastreado no `git status`
(reproduzido). Acrescentado `.venv-whisper/` ao `.gitignore`, conforme o
escopo original de B07-A ("`.gitignore` somente se faltar exclusão específica
para os novos artefatos"). O diretório de `--pesos` continua escolha de quem
executa; recomendado fora do repositório.

**Revisão B07-A-R01 (Opus, 19/09/2026):** a primeira versão deste arquivo
usava `--index-url` (índice único) apontando só para o índice CPU, que não
hospeda `openai-whisper`; o comando em um passo **falhava** na resolução
(`No matching distribution found for openai-whisper==20250625` — reproduzido
com `pip install --dry-run` em venv vazio). A instalação relatada em
B07-A-01 tinha sido feita em duas etapas manuais, não com o arquivo
publicado. Após a correção, a receita foi verificada em venv vazio, sem
cache (`--no-cache-dir`), Python 3.14.7, linux x86_64: saída 0,
**0 pacotes `nvidia*`**, `torch` baixado como wheel `+cpu` de 196 MB.
Versões instaladas: `torch==2.14.0+cpu`, `openai-whisper==20250625`,
`numba==0.67.0`, `llvmlite==0.49.0`, `numpy==2.5.3`, `tiktoken==0.14.0`,
`triton==3.8.0` (o `triton` vem como dependência declarada do `torch`
mesmo no build CPU; não é usado na inferência em CPU). Pegada final do
ambiente virtual: **≈2,1 GB**, fora do repositório.

**Relevante para C02-A/hospedagem:** mesmo a instalação mínima CPU-only
soma ~2 GB. Qualquer ambiente de execução (local ou hospedado) precisa
orçar esse espaço, e instalar `torch` sem fixar o índice CPU-only arrisca
estourar cotas de disco ou gastar banda desnecessária baixando CUDA que
nunca será usado.

**Compatibilidade com Python 3.14:** confirmada. `torch==2.14.0+cpu`,
`openai-whisper==20250625`, `numba==0.67.0` e `llvmlite==0.49.0` — os dois
últimos são historicamente os que mais atrasam para suportar uma versão
nova de Python — já têm wheels prontos para `cp314`/`linux_x86_64`. Não
foi necessário instalar outra versão de Python.

## 3. Modelo escolhido e medições reais

Modelo: **`base`** (multilíngue, ~139 MB de pesos), primeira candidata
pedida pelo roteiro. Medido com
`backend/scripts/verificar_whisper.py transcrever`:

| Medição | B07-A-01 (Sonnet) | B07-A-03 (Opus, venv limpo) |
|---|---|---|
| Download dos pesos (`base`, uma vez) | 139 MB, ~4 s nesta rede | (cache reaproveitado) |
| Tempo de carga do modelo (já em cache) | 0,47–1,0 s | 0,47–0,88 s |
| Áudio sintético de 12,1 s — transcrição, padrões | 1,2–1,7 s | 0,98 s |
| Mesmo áudio — transcrição com `--experimento-forcado` | não medido separadamente | 0,98 s |
| Silêncio de 3 s — transcrição, padrões | 3,5–9,9 s | 4,26 s |
| Pico de RSS do processo | ~700–715 MB | 718–724 MB |

Todas as medições são de **um clipe de 12 s ou menos, em CPU, com o
modelo `base`**; não dizem nada sobre reuniões longas (ver seção 7).

**Observação relevante para limites (C02-A):** o tempo de transcrição do
silêncio de 3 s não foi menor que o do áudio de 12 s com fala — às vezes
foi maior. O Whisper processa internamente em janelas fixas de 30 s
(com padding), então o tempo não cai proporcionalmente para clipes curtos
nem para trechos sem fala. **Não estimar capacidade por regra de três
simples a partir de um clipe curto** — é preciso medir com durações mais
próximas do uso real antes de fixar timeout em C02-A.

## 4. Amostra sintética (apoio, não substitui o ensaio falado)

Não havia amostra real disponível nem foi solicitada uma gravação ao
usuário durante esta execução (a decisão de pedir está registrada como
pendência na seção 6). Para verificar o pipeline de ponta a ponta, gerei
uma amostra **sintetizada por texto-para-voz** com `espeak-ng` (ferramenta
local, licença GPL, sem custo), preservada em
[`amostras/amostra_sintetica_pt_espeak.wav`](amostras/amostra_sintetica_pt_espeak.wav)
(12,1 s, voz `pt-br`):

```bash
espeak-ng -v pt-br -s 150 -w amostra_sintetica_pt_espeak.wav \
  "Estamos insatisfeitos com o suporte e pensando em cancelar o contrato. \
Por outro lado, temos interesse em conhecer o Fluig e talvez expandir \
para o módulo de análise."
```

Arquivo preservado: mono, 22.050 Hz, 12,128 s, SHA-256
`9ff6550a54ebbc1c7dea8d2fe4ff37dcab00d047bffac3a561472be286478a9e`. É usado
**diretamente** nos ensaios — o Whisper reamostra para 16 kHz internamente
(via `ffmpeg`), e a conversão prévia para 16 kHz mencionada em B07-A-01 foi
desnecessária: repetida na revisão, produziu texto idêntico ao do arquivo
original em todas as configurações testadas.

**Ensaio 1 — configuração padrão do Whisper** (`transcrever --audio
docs/decisoes/amostras/amostra_sintetica_pt_espeak.wav --pesos <dir>`):
**texto vazio, 0 segmentos, saída 0.** O modelo classificou o áudio inteiro
como provável não-fala (`no_speech_prob` ≈ 0,72 em todos os segmentos
quando forçado a decodificar).

**Ensaio 2 — experimento forçado** (`--experimento-forcado`, que aplica
`no_speech_threshold=0.9`, `logprob_threshold=None` e
`condition_on_previous_text=False`): 2 segmentos, `[0,0–5,2]` e
`[5,2–11,8]`, texto:

> "Esta mojinha só se fez que o nosso poda se empenhe sanguei em cancelado
> contrato. Por outro lado, temos que desencomer sedo fluigi, talvez
> expandir para o modo de alíso."

Reproduzido pela revisão duas vezes seguidas com saída byte a byte
idêntica (determinístico com esses três parâmetros). Comparado ao texto
original, poucos trechos batem ("cancelado contrato", "expandir",
aproximações de "Fluig" e "módulo de análise"); o restante é ruído.

**Achado da revisão (B07-A-R02):** o texto acima **não se reproduz** só
com `no_speech_threshold=0.9`. Com o threshold sozinho (e os demais
padrões), o modelo emite alucinação multilíngue e **não determinística**
— em duas execuções, textos diferentes com fragmentos em coreano,
cirílico, francês e inglês, e segmentos que se estendem até ~28 s num
áudio de 12 s (a janela interna de 30 s é preenchida com texto inventado).
Causa: quando `logprob_threshold` reprova o resultado, o Whisper recorre
a temperaturas maiores e passa a *amostrar*; e com
`condition_on_previous_text=True` a alucinação de um segmento contamina os
seguintes. Os dois parâmetros extras desligam exatamente isso. A primeira
versão do relatório citava só o threshold; a flag do script fixa os três
para que o resultado seja reproduzível.

**Conclusão (inalterada): voz sintetizada por formantes (`espeak-ng`) não
é uma amostra válida para avaliar o Whisper** — o próprio modelo sinaliza
baixa confiança de que aquilo seja fala real, e qualquer texto obtido
forçando a decodificação é majoritariamente incorreto ou inventado. Isso
confirma por que o roteiro exige fala humana real: o resultado aqui prova
só que o *pipeline mecânico* funciona (carrega modelo, roda inferência,
devolve segmentos com timestamps e `no_speech_prob`), não que a
*qualidade* de transcrição é adequada — **e não permite concluir nada
sobre a qualidade com fala humana**, nem para pior nem para melhor.

## 5. Casos de borda testados

Amostras auxiliares, geradas com estes comandos exatos (não versionadas —
são triviais de recriar; os hashes identificam o que foi testado):

```bash
# silêncio de 3 s, 16 kHz mono
ffmpeg -v error -y -f lavfi -i anullsrc=r=16000:cl=mono -t 3 silencio_3s.wav
# sha256 45ec296d121c4f9d30789aecabf462fd1336664eb3169f181d998c99a8e7ad2d

# "áudio" inválido: texto puro com extensão .wav
printf 'isso nao e um arquivo de audio valido\n' > invalido.wav
# sha256 4dd2f50f9db25f49f66e29cddb87e3b8a1313f2162de1a5ae688bdc2cd6ba218
```

Resultados com `verificar_whisper.py transcrever` (padrões do Whisper):

- **Silêncio (3 s):** texto vazio, 0 segmentos, sem exceção, saída 0;
  4,26 s de transcrição na revisão (3,5–9,9 s em B07-A-01). Comportamento
  seguro para o adaptador de B07-B tratar como "nenhuma fala detectada".
- **Arquivo inválido:** `modelo.transcribe(...)` propaga
  `RuntimeError: Failed to load audio: ...` vindo do `ffmpeg` interno do
  Whisper, com a mensagem do `ffmpeg` embutida (incluindo a configuração de
  build inteira — verboso, precisa ser resumido antes de virar mensagem de
  API em B07-B/B08-C). O script captura e sai com **código 1**.
- **Falha de preparação** (acrescentado na revisão): nome de modelo
  inexistente (`--modelo nao-existe`) → `RuntimeError: Model nao-existe not
  found; available models = [...]`, capturado, **código 2**. Cobre também
  falha ao criar o diretório de pesos e falta de rede na primeira baixa dos
  pesos — **correção B07-A-R04 (21/09/2026):** a versão anterior deste
  parágrafo dizia que a falta de rede saía com traceback; verificado com
  proxy inacessível e diretório de pesos vazio (`--modelo tiny`):
  `FALHA na preparacao (pesos/modelo): URLError: <urlopen error [Errno 111]
  Connection refused>`, **código 2**; permissão negada no diretório de pesos
  → `PermissionError`, **código 2**. **Não cobre** falha de importação do
  `whisper` (venv errado): `ModuleNotFoundError` com o traceback normal do
  Python, código 1 do interpretador. O script não promete que toda falha
  está tratada.

O script imprime o SHA-256 do áudio e os parâmetros usados antes de cada
execução, para que cada medição fique ligada ao arquivo e à configuração
que a originou.

## 6. O que falta para fechar B07-A

- **Gravação real fictícia em português.** Falta um áudio falado de
  verdade (não sintetizado) com termos comerciais (ex.: "insatisfeito",
  "cancelar contrato", "concorrente", nome de produto) e texto esperado
  conhecido, para medir qualidade de reconhecimento. Os 30–60 s sugeridos
  são o **tamanho da amostra de validação** pedido pelo cartão B07-A — não
  uma duração de reunião aprovada pelo usuário, que continua indefinida. A
  frase do experimento sintético serve como roteiro de leitura, se ajudar.
  **Ação pendente do usuário ou do Codex: fornecer/gravar essa amostra.**
  Nem a execução (B07-A-01) nem a revisão (B07-A-03) tiveram acesso a uma;
  a revisão do material existente foi concluída sem ela.
- Sem essa amostra, não é possível confirmar taxa de acerto em termos
  relevantes ao card nem afirmar que a qualidade do modelo `base` é
  suficiente — só que ele *roda* neste hardware dentro dos tempos medidos.
  O resultado ruim com voz sintética **não** é evidência sobre fala humana.
- Duração/tamanho máximos de áudio de produção não foram informados
  (plano registra como decisão em aberto). Os limites finais são de C02-A;
  o que está abaixo é recomendação baseada só neste clipe curto.

## 7. Recomendação para C02-A

Com a ressalva da seção 6 (qualidade ainda não comprovada com fala real):

- **Modelo:** `base` multilíngue como ponto de partida — carrega rápido
  (<1 s em cache), usa ~700 MB de RSS, roda em CPU comum sem GPU. Se a
  gravação real mostrar qualidade insuficiente em termos comerciais,
  avaliar `small` (maior, mais lento, ainda sem GPU) como próximo passo —
  não pular direto para modelos maiores sem medir o custo.
- **Executor:** um processo por vez, sem fila externa — consistente com a
  preferência já registrada no roteiro ("processo de API e uma transcrição
  ativa"). Com ~700 MB de pico por transcrição e ~2,2 GiB de RAM
  **disponível** (`available`) observados neste ambiente — o *free* de
  ~150 MB não é a medida certa, é só memória não alocada com cache de
  disco ocupando o resto —, caberiam poucas transcrições simultâneas, e a
  API de texto e o sistema também precisam de memória. Recomendação:
  **uma transcrição ativa**, recusando a segunda com resposta clara, como
  C02-A já prevê; qualquer concorrência maior exige medir RAM disponível
  no ambiente final, não neste.
- **Timeout:** não fixar um valor a partir só deste clipe de 12 s — o
  achado da seção 3 (tempo não escala linearmente com duração/silêncio)
  exige medir com áudio de duração real antes de definir um número em
  C02-A. A amostra de validação de 30–60 s (seção 6) já dá um segundo
  ponto de medida; a duração máxima de reunião a suportar continua sendo
  decisão do usuário, não desta verificação.
- **Decodificação:** usar os padrões do Whisper (`no_speech_threshold`
  0.6, `logprob_threshold` -1.0, `condition_on_previous_text` True) no
  adaptador de B07-B. Não forçar thresholds para "arrancar" texto de áudio
  que o modelo classifica como não-fala — a seção 4 mostra que isso produz
  alucinação. Silêncio/não-fala deve virar resultado vazio tratado como
  falha útil, não texto inventado.
- **Formatos:** aceitar o que o `ffmpeg` do sistema decodifica (cobre
  WAV/MP3/M4A comuns); rejeitar antes de chamar o Whisper qualquer arquivo
  que falhe a inspeção de B06-A, para não gastar CPU/RAM tentando
  transcrever algo inválido (o `RuntimeError` da seção 5 comprova que o
  Whisper só descobre o problema depois de já ter carregado o áudio).
  Requisito indireto para B07-B: tratar timeout/travamento na inspeção
  antes de chegar à transcrição, não durante ela.
- **Não usar API paga** nesta fase — não foi necessário: a instalação
  gratuita local atende o objetivo do usuário.

## 8. Fora do escopo desta entrega

Nenhuma rota, banco, frontend, executor de produção ou dependência nova
foi adicionada a `backend/pyproject.toml`. `backend/app/` não foi tocado —
confirmado com `git diff --stat -- backend/app` (vazio) ao final da
execução e da revisão. Nenhum modelo além do `base` foi baixado; nenhum
benchmark extenso foi executado. Sobre `--pesos`: o script exige o
argumento para que o destino dos pesos seja explícito e recomenda um
caminho fora do repositório, mas **não valida** o caminho — quem executa é
responsável por não apontar para dentro do repositório (pesos, venv e
cache não devem ser versionados).

## 9. Rastreabilidade dos ensaios da revisão (B07-A-03)

| Ensaio | Arquivo (SHA-256) | Comando | Resultado |
|---|---|---|---|
| 1 | `amostra_sintetica_pt_espeak.wav` (`9ff6550a…8a9e`) | `transcrever --audio … --pesos <dir>` | 0 segmentos, texto vazio, saída 0 |
| 2 | idem | `… --experimento-forcado` | 2 segmentos, texto da seção 4, saída 0, determinístico (2 execuções idênticas) |
| 2b | idem | só `no_speech_threshold=0.9` (snippet Python; a opção isolada foi removida da CLI por não ser reproduzível) | alucinação multilíngue, 4–12 segmentos até ~28–30 s, texto diferente a cada execução |
| 2c | `amostra_16k.wav` (`2ca491b0…fbd0`, conversão 16 kHz) | idem 2 e 2b | textos idênticos aos do arquivo original — conversão irrelevante |
| 3 | `silencio_3s.wav` (`45ec296d…ad2d`) | `transcrever --audio …` | 0 segmentos, vazio, 4,26 s, saída 0 |
| 4 | `invalido.wav` (`4dd2f50f…a218`) | `transcrever --audio …` | `RuntimeError: Failed to load audio`, saída 1 |
| 5 | `silencio_3s.wav` | `… --modelo nao-existe` | `RuntimeError: Model nao-existe not found`, saída 2 |

Ambiente dos ensaios: venv vazio criado na revisão com a receita
corrigida (seção 2), Python 3.14.7, `torch==2.14.0+cpu`,
`openai-whisper==20250625`, modelo `base`, CPU. Os números de B07-A-01
foram obtidos pelo Sonnet em venv anterior (instalação em duas etapas) e
não têm log preservado — estão identificados como relato anterior na
tabela da seção 3.

## 10. Reprodução independente (B07-A-06, 21/09/2026)

Revisão da versão commitada `cc61925`, sem tratar B07-A-03 como evidência
por si só. Ambiente: venv vazio novo (`pip 26.0.1`, Python 3.14.7, linux
x86_64), `--no-cache-dir`, temp do `pip` apontado para disco fora do tmpfs
com cota; nenhum cache ou venv anterior existia (o `/tmp` é limpo entre
sessões).

| Verificação | Resultado (21/09/2026) | Confere com B07-A-03? |
|---|---|---|
| Receita antiga reconstruída (`--index-url` único) | `No matching distribution found for openai-whisper==20250625` | sim (premissa de R01) |
| `pip install --dry-run` da receita publicada | resolve 24 pacotes, `torch-2.14.0+cpu`, `openai-whisper-20250625`, `numba-0.67.0`, `llvmlite-0.49.0`, `numpy-2.5.3`, `tiktoken-0.14.0`, `triton-3.8.0`; 0 `nvidia*` | sim |
| Instalação real | saída 0, 41 s, 2,1 GB, `torch.cuda.is_available()` → `False` | sim |
| Padrões do Whisper `v20250625` (fonte oficial) | `no_speech_threshold=0.6`, `logprob_threshold=-1.0`, `condition_on_previous_text=True`; fallback de temperatura disparado por `logprob`/`compression_ratio` | sim (seções 4 e 7) |
| Amostras auxiliares pelos comandos da seção 5 | hashes `45ec296d…ad2d` e `4dd2f50f…a218` idênticos | sim |
| Ensaio 1 (padrões) | 0 segmentos, saída 0, 1,15 s, RSS 692 MB | sim |
| Ensaio 2 (`--experimento-forcado`, 2 execuções) | 2 segmentos `[0,0–5,2]` `[5,2–11,8]`, `no_speech_prob` 0,72, texto idêntico à seção 4 nas duas execuções, 1,05–1,13 s | sim |
| Ensaio 2b (só threshold, snippet, 2 execuções) | 1 segmento até 12,2 s numa; 7 segmentos até 17,2 s com cirílico/inglês na outra — não determinístico | sim (extensão observada menor que os 28–30 s relatados; a natureza do achado é a mesma) |
| Ensaio 3 (silêncio 3 s) | 0 segmentos, saída 0, 6,74 s | sim (tempo maior que o do áudio de 12 s, como a seção 3 alerta) |
| Ensaio 4 (inválido) | `RuntimeError: Failed to load audio`, saída 1 | sim |
| Ensaio 5 (`--modelo nao-existe`) | `RuntimeError: Model nao-existe not found`, saída 2 | sim |
| Falta de rede no 1.º download / permissão no diretório de pesos | saída 2 nos dois casos | **não** — corrigido (R04) |
| Receita cria `.venv-whisper/` não ignorado | reproduzido com `git status` | **não coberto** — corrigido (R03) |
| Suíte da API, `import app.main` sem `whisper`/`torch`, diff de `backend/app`/testes/`pyproject`/contratos | 100/100; nenhum; vazio | sim |

Fala humana real (P01) continua sem amostra: nada nesta reprodução muda a
entrega de PARCIAL.

## Fontes oficiais consultadas

- <https://github.com/openai/whisper> — código e pesos, licença MIT,
  dependência de FFmpeg.
- <https://github.com/openai/whisper/blob/main/model-card.md> — limitações
  conhecidas (alucinação, repetição), citadas na seção 4 como explicação
  do resultado ruim com voz sintética.
