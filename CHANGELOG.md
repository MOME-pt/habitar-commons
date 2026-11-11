# Registo de alterações

## 1.3.1 — 10 nov 2026 (patch, retrocompatível)
Correções a partir de uma revisão crítica externa e de pesquisa jurídica preliminar.
- **Validador.** Operadores separados por tipo (escalares: eq, ne, in, not_in; listas: contains, contains_any, contains_all, contains_none, subset_of). Corrige quatro regras que davam resultados errados: PT001 aceitava hipoteca numa lista de financiamentos; PO001, PO002 e OP002 disparavam em casos válidos, incluindo o próprio exemplo HC-CR-MID.
- **Esquema.** Novo `manifest.schema.json` com tipo e cardinalidade de cada campo. Eixos multivalor declarados como código isolado continuam aceites, com aviso DEP003.
- **Endereçamento.** Sintaxe definida para listas de objetos (`phases[id=PH-DEV].event`, `payer[*].code`) e para referências entre campos (`{ref: axes.asset_owner}`).
- **has_value.** Novo operador que não aceita objetos de esquema vazios. Em manifestos-modelo (`kind: template`) os campos por preencher são relatados como info.
- **Mensagens alinhadas com os testes.** US001 verifica o óbito como evento de PH-END; OP001 verifica a divulgação do fee; o teto do RX-CAPCPI passa a regra própria (RX004).
- **PY003.** As quotas dos pagadores têm de somar 1,0.
- **PT002 reescrita.** O direito de habitação cooperativo não é intransmissível: o DL 502/99 permite a alienação entre vivos com acordo da assembleia geral e a transmissão por morte (art. 22.º). A regra pede agora a base legal e o mecanismo, com referência aos estatutos quando estes restrinjam a transmissão.
- **PT001.** Mantém-se, com fundamento no art. 688.º do Código Civil e no art. 1488.º, aplicável por remissão do art. 19.º, n.º 1, do DL 502/99.
- **Nomes.** `kind: license` passa a `kind: template` e o campo `license` passa a `spec_license`, para não confundir modelos de habitação com a licença do standard. Os nomes antigos são aceites com aviso (DEP001, DEP002) até à v2.0.
- **Modelos HC** marcados como rascunho em revisão jurídica (`status: under_review`).
- **Testes.** 58 casos em `tests/`, com dois por regra e regressões para os erros corrigidos.
- **Editorial.** P12 deixa de referir o código inexistente F-PHIL; corrigidos o título do separador de regras da especificação e o histórico de versões abaixo.

## 1.3 — 08 nov 2026 (primeira versão pública)
- 18 perfis: Cohousing em propriedade (P03, `H-COHO-COST-PERM`) e Usufruto vitalício sénior (P17, `H-REAL-ENTRY-LIFE`, variantes A e B).
- Eixos novos: quem paga (`PY-*`), revisão da renda (`RX-*`), população-alvo (`PO-*`).
- Códigos novos: `T-LIFE`, `E-ENTRY`, `ROLE-COMM`.
- Dez regras novas (PY001–002, RX001–003, PO001–002, CO001, US001–002); 27 regras no total.
- Licença CC BY-SA 4.0; campo `license` nos manifestos.

## 1.2 — 08 nov 2026 (versão de trabalho, não publicada)
- 16 perfis numerados pela sequência natural, família a família.
- Campo `allocator` (quem atribui as casas) na Camada 6; regra AL001.

## 1.1 — 01 nov 2026 (versão de trabalho, não publicada)
- Titular do solo, reversão e vinculação da acessibilidade (`L-*`); fases (`PH-*`); Camada 6; parâmetros PT; F-IMPACT e F-NIS; subtipos de direito real; regras PT001 e PT002.

## 1.0 — 04 fev 2026
- Versão inicial: 12 perfis, vocabulário core, manifesto e validador.
