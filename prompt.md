# Revisão e correção de B07-A — Whisper — Claude Opus

Revise a última entrega do Claude Sonnet: **B07-A — viabilidade do Whisper**,
registrada em B07-A-01 em 19/09/2026. O usuário pediu verificar se já houve
revisão do Opus e, na ausência, preparar este prompt. Codex não encontrou
revisão do Opus para B07-A; a última registrada era B04-03, de outra entrega.

A entrega B07-A é **PARCIAL**: o Sonnet relatou execução real do Whisper sobre
áudio sintético, silêncio e arquivo inválido, mas não validou fala humana real.
Faça revisão própria do código, instalação e relatório; corrija problemas
confirmados no escopo. A falta dessa amostra não impede revisar o que existe,
mas impede declarar o aceite integral de viabilidade/qualidade.

## Leitura e versão exata

Leia `AGENTS.md`, `CLAUDE.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` (4.4–4.5,
5 e 8), ficha B07-A e eventos B07-A-01/B07-A-02 de `REGISTRO_TRABALHO.md`,
etapa 4 do plano, cartão B07-A de `docs/planejamento/PRS_BACKEND_AUDIO.md`,
`docs/planejamento/PROMPT_B07_A_VIABILIDADE_WHISPER.md` (critérios originais)
e `docs/decisoes/transcricao-whisper.md` (relatório do executor).

- Pasta: `/home/gustavoecocchi/Documents/CONVIQ`.
- Branch atual: `spike/b07-a-viabilidade-whisper`.
- HEAD/base de código: `6169feca8c3a6cc6c5500eeab264eba817c8fbbc`, com
  B01–B04/C01 aceitos. **Esse commit não contém a entrega B07-A.**
- B07-A está em quatro arquivos locais não rastreados:
  `backend/scripts/verificar_whisper.py`,
  `backend/scripts/requirements-whisper.txt`,
  `docs/decisoes/transcricao-whisper.md` e
  `docs/decisoes/amostras/amostra_sintetica_pt_espeak.wav`.
- Confira a versão na raiz com:

```bash
sha256sum -c docs/revisoes/2026-09-19-b07-a-entrada-opus.sha256
```

Preserve o manifesto de entrada. Se houver divergência, identifique e registre
antes de editar; depois informe hashes/diff da versão realmente revisada.

Também existem alterações locais de planejamento/registro, os roteiros de áudio
e refinamento e cópias de prompts. São preexistências, não implementação B07-A.
B11 continua PLANEJADO/NAO_INICIADO; seu prompt foi preservado em
`docs/planejamento/PROMPT_B11_NEGACAO_SENTIMENTO.md`. Não implemente B11 ou C02-A.

Confira status com não rastreados, diff e índice. Correções permanecem nesta
branch de B07-A; não trocar branch, descartar mudanças ou reescrever commits.
Destino/principal, publicação e PR remoto atuais são NAO_VERIFICADO. Autorização
neste encaminhamento: revisão, correção, validação e documentação locais;
**sem commit, push, abertura de PR remoto, merge ou implantação**.

## Objetivo e critérios originais

B07-A deve demonstrar transcrição real em português e recomendar configuração
gratuita reproduzível antes de alterar a API. Inventário de recursos, ambiente
isolado, modelo identificado, áudio e texto esperado/obtido, tempo/memória,
tratamento de silêncio e inválido, limitações e recomendação para C02-A.

Amostra falada real é obrigatória para concluir viabilidade/qualidade; voz
sintética somente como apoio identificado. Sem amostra disponível, relatar
PARCIAL e o que falta. Não atribuir qualidade ruim do TTS a toda fala humana
nem generalizar desempenho de um clipe de 12 segundos para reuniões longas.

Preservar: serviços gratuitos, ambiente da API independente, nenhuma dependência
Whisper em `backend/pyproject.toml`, nenhum peso/venv/cache no versionamento,
nenhum download ou carregamento de modelo ao importar FastAPI. Não criar rotas,
executor de produção, banco, frontend ou hospedagem nesta revisão.

## Apontamentos iniciais do Codex

### B07-A-R01 — Instalação reproduzível: confirmar antes de corrigir

O arquivo de requisitos define um único `--index-url` para o índice CPU do
PyTorch e inclui no mesmo arquivo `torch==2.14.0` e `openai-whisper==20250625`.
O relatório descreve instalação de torch CPU antes do Whisper, mas o comando
publicado instala tudo em um passo com esse arquivo. **Codex não executou
instalação limpa nem confirmou a disponibilidade desses pacotes no índice**;
é um ponto de verificação, não uma falha de instalação já reproduzida.

Confira se o comando publicado resolve todas as dependências num ambiente
vazio sem configuração/cache ocultos, se evita pacotes CUDA e se as versões
relatadas são as realmente instaladas. Se necessário, separar explicitamente
as fontes/etapas e corrigir instruções/requisitos. Não realizar downloads de
vários GB sem estimar recursos, não limpar caches globais nem alterar o venv
`backend/.venv`. Validar em ambiente isolado e registrar limitações de acesso.

### B07-A-R02 — Reprodução incompleta dos experimentos relatados

O relatório apresenta saída com `no_speech_threshold=0.9`, enquanto o script
entregue chama `transcribe(..., language=idioma, fp16=False)` e não possui
opção CLI para esse parâmetro. A seção 5 remete a comandos completos no script,
mas ele também não contém a geração dos arquivos de silêncio/inválido ou a
conversão citada para 16 kHz. A amostra WAV entregue foi conferida pelo Codex:
mono, 22.050 Hz e 12,128 s; o relatório menciona ensaios com versão convertida.

Complete comandos exatos e identifique qual arquivo/configuração originou cada
medição, com hash e resultado. Pode documentar um comando experimental separado
ou acrescentar opção pequena ao script se fizer sentido; não tornar threshold
forçado o padrão para obter artificialmente uma boa transcrição. Preserve a
separação entre configuração padrão e experimento forçado. Não fabricar logs
antigos: quando faltarem, identificar como relato anterior e registrar nova
execução, se viável. Este achado é de rastreabilidade, não prova que os ensaios
relatados não ocorreram.

### B07-A-P01 — Aceite parcial e qualidade ainda pendente

A ausência de gravação real está corretamente declarada pelo Sonnet. Confirmar
que conclusão, recomendações e ficha não passam de “execução mecânica relatada”
para “qualidade aprovada”. Se houver amostra falada real adequada e autorizada,
pode completar o teste dentro de B07-A, registrando origem e condições. Caso
contrário, concluir a revisão dos artefatos e manter a entrega PARCIAL com essa
pendência concreta. Não condicionar toda a revisão de código à chegada do áudio.

### Outros pontos a conferir, sem ampliar o escopo

- O texto impresso “idioma detectado” acompanha `language=idioma`, configurado
  na chamada; apresentar corretamente o que foi configurado e medido.
- O `try` cobre a transcrição, mas importação, criação de diretório e carga do
  modelo estão fora dele. Conferir falhas de preparação e mensagem de erro;
  não prometer que toda falha está tratada só porque arquivo inválido foi testado.
- Recomendações de concorrência devem distinguir RAM livre de disponível;
  o relatório cita ambas. O ensaio de 30–60 s é amostra de validação, não
  duração de reunião aprovada pelo usuário. Formatos/limites finais ficam em C02-A.
- Não ampliar “--pesos fora do repositório” para uma promessa de validação do
  caminho que o script não aplica; conferir coerência entre documentação e CLI.

Confirme cada apontamento antes de mudar. Registre concordância, correção ou
justificativa para não corrigir. Faça sua revisão independente, incluindo pontos
não encontrados pelo Codex, mas mantenha B07-A pequeno e experimental.

## Evidência já conferida pelo Codex

- Leitura dos quatro arquivos, do escopo e do histórico de revisão.
- `python3 backend/scripts/verificar_whisper.py --help` → saída 0.
- Sintaxe Python via `ast.parse` → OK; cabeçalho WAV conferido com `wave`.
- Hashes dos quatro arquivos fixados no manifesto de entrada.
- `git diff --name-only -- backend/app backend/tests backend/pyproject.toml docs/contratos`
  vazio; índice vazio. A aplicação aceita não mudou nesta entrega.

Não reproduzi instalação, carregamento de modelo, inferência, métricas ou suíte
completa nesta preparação. Os 100 testes e números de recursos de B07-A-01 são
relato do Sonnet; a última revisão Opus registrada, B04-03, não cobre B07-A.

## Validação e devolução

Reproduzir o que for viável em ambiente isolado, usando recursos disponíveis.
Correções de lógica relevante devem ter testes proporcionais; simulação de erro
pode verificar tratamento, mas não comprova qualidade do modelo. Se repetir
Whisper, registrar execução real, versões, arquivo, configuração e resultado.
Se não executar uma verificação, informar motivo e impacto no aceite.

Atualizar ficha/índice B07-A e acrescentar evento próprio de Opus em
`REGISTRO_TRABALHO.md`, preservando B07-A-01/B07-A-02. Separar:

1. Revisão concluída ou parcial e correções de cada apontamento.
2. Entrega B07-A finalizada ou ainda PARCIAL, sobretudo quanto à fala real.
3. Arquivos e evidências próprias versus métricas apenas herdadas.
4. Git: branch, base/HEAD, hashes/diff, arquivos não commitados, publicação,
   PR remoto e integração, sem atribuir B07-A ao commit 6169fec.

Entregar para Codex verificar; não marcar APROVADO/INTEGRADO por conta própria.
Não iniciar C02-A, B07-B, B11 ou outro PR automaticamente.
