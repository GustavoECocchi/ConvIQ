# Como registrar o trabalho (modo ágil, v1.2)

Objetivo: o mesmo rastreio com menos leitura e menos escrita. O histórico
anterior a 07/10/2026 foi movido, sem alteração, para os arquivos deste
diretório; o texto original das instruções do histórico está em
[GUIA_ORIGINAL.md](GUIA_ORIGINAL.md).

## O que ler (nesta ordem, parando quando tiver o necessário)

1. [../../STATUS.md](../../STATUS.md): estado atual, próximo passo e armadilhas.
2. A linha do PR na tabela de [../../REGISTRO_TRABALHO.md](../../REGISTRO_TRABALHO.md).
3. `docs/registro/<ID>.md` do PR em que vai atuar (ficha + eventos).
4. O código e o diff da versão indicada. Não leia outros PRs sem motivo.

## O que escrever (e onde), uma vez só

| Quando | Escreva | Onde |
|---|---|---|
| Ao entregar ou verificar | **Um evento curto** (formato abaixo) | fim de `docs/registro/<ID>.md` |
| Se o estado do PR mudou | Atualize **só os campos de estado** da linha da tabela | `REGISTRO_TRABALHO.md` |
| Se o Git mudou | **Substitua** a fotografia vigente (não acumule) | `REGISTRO_TRABALHO.md` |
| Se o próximo passo mudou | Atualize `STATUS.md` | `STATUS.md` |

- O evento **é** o relatório da seção 8: não crie arquivo de relatório
  separado e não repita o evento no chat. A resposta ao usuário tem até 10
  linhas e aponta para o evento. Para encaminhar a outro agente, o usuário
  cola o evento (ou o link).
- A ficha do PR (cabeçalho do `<ID>.md`) só é reescrita quando o estado do
  ciclo muda; não duplique nela o conteúdo dos eventos.
- Fotografias Git antigas **não** são arquivadas de novo: o Git já as guarda.
- Prompts citam caminhos, commit e eventos; não colam listas de hashes nem o
  texto de eventos anteriores.

## Formato do evento (até ~25 linhas)

```text
### <ID>-<nn> — <data> — <Agente / papel>
- **Escopo:** pedido do usuário e prompt seguido.
- **Versão:** branch, base → commit examinado/entregue; se não há commit da
  entrega, HEAD + status, diff local e arquivos não rastreados.
- **Resultado:** achados (ID → confirmado e corrigido / não confirmado / pendente) e entrega.
- **Validação:** comando → resultado; o que NÃO foi executado.
- **Limites e pendências:** só o que o próximo agente precisa saber.
- **Git:** commit, push, PR e integração, cada um com situação própria.
- **Próximo:** responsável e ação.
```

Mantenha a distinção entre o que foi conferido e o que foi apenas relatado, e
os campos de Git separados (seção 5.1 da governança). O que o evento já diz
não se repete no índice nem na fotografia.

## Arquivos

- `<ID>.md`: ficha e histórico de um PR (`B13.md`, `B12.md`...).
- `GERAL.md`: eventos que cobrem várias frentes.
- `FOTOGRAFIAS_HISTORICAS.md`: fotografias e introduções de índice antigas.
- `GUIA_ORIGINAL.md`: texto original das instruções do histórico.
