# Instruções do ConvIQ para Claude

Leia e siga `AGENTS.md`, `SISTEMA_GOVERNANCIA_CONVIQ.md` e
`REGISTRO_TRABALHO.md`, além do escopo no `PLANO_DESENVOLVIMENTO.md`.

Sonnet e Opus devem registrar sua própria atuação no arquivo de registro antes
de devolver o trabalho. Atualize a ficha e o histórico com o que foi feito,
validação, pendências, branch e situação de commit, push e integração.
Use o formato da seção 8 da governança. Identifique-se conforme o papel
realmente atribuído; não presuma que uma revisão ou aprovação já ocorreu.

Uma implementação pode estar finalizada e ainda não commitada, ou commitada
em uma branch sem estar integrada à principal. Declare essas situações
separadamente. Entregue para a coordenação; não aprove a própria entrega
nem inicie o próximo PR automaticamente.

Quando o usuário pedir um prompt, leia o prompt atual em `prompt.md`. Esse é o
rascunho oficial de trabalho e contém somente a instrução vigente; o histórico
de versões fica em `REGISTRO_TRABALHO.md` ou em cópias nomeadas indicadas pelo
Codex.
