# Instruções do ConvIQ para Claude

Leia `AGENTS.md` e `STATUS.md`; consulte `SISTEMA_GOVERNANCIA_CONVIQ.md`
(seção 11 após integração de EST01), `docs/registro/<ID>.md` do PR em que atua e o escopo no
`PLANO_DESENVOLVIMENTO.md` só no que precisar.

Sonnet e Opus registram sua própria atuação com **um evento curto** (formato
em `docs/registro/README.md`) antes de devolver o trabalho: o que foi feito,
validação, pendências, branch/commit e situação de push, PR e integração.
Identifique-se conforme o papel realmente atribuído; não presuma que uma
revisão ou aprovação já ocorreu.

Uma implementação pode estar finalizada e ainda não commitada, ou commitada
em uma branch sem estar integrada. Declare essas situações separadamente.
Entregue para a coordenação; não aprove a própria entrega nem inicie o
próximo PR automaticamente. Commit e push na branch de trabalho exigem
autorização do usuário para a entrega e testes aprovados; PR, merge e a branch
padrão exigem ordem do usuário.

Quando o usuário pedir um prompt, leia o prompt atual em `prompt.md`: é o
rascunho oficial e contém somente a instrução vigente. Antes de executá-lo,
confira se ele ainda corresponde ao estado do `STATUS.md`; se já foi
cumprido, registre a divergência em vez de repetir o trabalho.
