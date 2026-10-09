import { describe, expect, it } from 'vitest'
import contrato from '../../../docs/contratos/analise-texto.md?raw'
import enumsBackend from '../../../backend/app/schemas/comum.py?raw'
import { CODIGOS_ERRO, SENTIMENTOS, SITUACOES_CHURN, VINCULOS } from './analise.ts'

/** Valores de uma `class <nome>(str, Enum)` do backend: `NOME = "valor"`. */
function valoresDoEnum(nome: string): string[] {
  const inicio = enumsBackend.indexOf(`class ${nome}(`)
  expect(inicio, `class ${nome} no backend`).toBeGreaterThanOrEqual(0)
  const proxima = enumsBackend.indexOf('\nclass ', inicio + 1)
  const corpo = enumsBackend.slice(inicio, proxima === -1 ? undefined : proxima)
  return [...corpo.matchAll(/^\s+[A-Z_]+ = "([a-z_]+)"/gm)].map((m) => m[1])
}

describe('tipos de C01 não divergem do backend nem do contrato', () => {
  it('os enums literais são exatamente os do backend', () => {
    expect([...VINCULOS]).toEqual(valoresDoEnum('Vinculo'))
    expect([...SENTIMENTOS]).toEqual(valoresDoEnum('Sentimento'))
    expect([...SITUACOES_CHURN]).toEqual(valoresDoEnum('ChurnSituacao'))
  })

  it('os códigos de erro são exatamente os da tabela "Erros HTTP" do contrato', () => {
    const tabela = contrato.slice(contrato.indexOf('## Erros HTTP'), contrato.indexOf('## Exemplos'))
    const codigos = [...tabela.matchAll(/^\| `([A-Z_]+)` \|/gm)].map((m) => m[1])

    expect(codigos.length).toBeGreaterThan(0)
    expect([...CODIGOS_ERRO]).toEqual(codigos)
  })
})
