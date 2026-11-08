# Habitar Commons

**Classificação modular das formas de habitar, inspirada nos Creative Commons.**
Versão 1.3 · novembro de 2026 · Jurisdição-alvo: Portugal

Os Creative Commons não mudaram o direito de autor: tornaram-no legível. O Habitar Commons faz o mesmo com a habitação. Decompõe qualquer arranjo habitacional num conjunto fechado de condições e responde, para qualquer casa, a seis perguntas:

1. Que direito tem quem lá vive?
2. Quem paga?
3. Como se forma e evolui o que se paga?
4. Durante quanto tempo isso está garantido?
5. Para quem se destina a casa?
6. Quem decide as regras?

## O que está neste repositório

| Pasta | Conteúdo |
| --- | --- |
| `docs/` | Booklet v1.3 (PDF) e especificação completa (XLSX) |
| `spec/` | Ruleset do validador de compatibilidade (`rules_v1_3.yaml`, 27 regras) |
| `examples/` | Manifesto completo de exemplo (`HC-CR-MID_v1_3.yaml`) |

## Como funciona

- **Sete camadas:** metadados; direito e titularidade; economia; governação e garantias; forma de habitar; módulos e kits; estrutura da operação.
- **Headline:** um código curto, `H-<BASE>-<ECON>-<TERM>`. Por exemplo, `H-MEMB-COST-LONG`: cooperativa de membros, preço ao custo, direito de longa duração.
- **Manifesto:** a especificação completa em YAML ou JSON. É sempre a fonte de verdade.
- **Validador:** regras declarativas (quando → então) com três níveis: `error`, `warning`, `info`.

## Catálogo v1.3: 18 tipos em 5 famílias

| Família | Perfis |
| --- | --- |
| Propriedade | P01 Compra de mercado · P02 Propriedade ao custo · P03 Cohousing em propriedade · P04 Propriedade com revenda limitada · P05 Híbridos |
| Arrendamento de mercado | P06 Duração média · P07 Estável · P08 Licença ou subscrição |
| Arrendamento regulado e social | P09 Teto regulado · P10 Custo-base · P11 Social · P12 Emergência ou transição |
| Cooperativa | P13 Custo-base · P14 Social · P15 Custo-base, duração média |
| Direitos reais e trust | P16 Direitos reais limitados · P17 Usufruto vitalício sénior (A e B) · P18 Ativo em trust ou CLT |

## Contribuir

O Habitar Commons é um standard aberto e versionado. Abra uma *issue* para propor um perfil, um código ou uma regra, ou para classificar um modelo que não caiba no catálogo. As versões seguem versionamento semântico: major quando muda o significado de eixos; minor quando acrescenta eixos, perfis ou regras; patch para correções de redação.

## Licença

Publicado pela MOME sob a licença [Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/deed.pt). Pode usar, adaptar e partilhar, com atribuição a Francisco Rocha Antunes, Filipa Serôdio Pinheiro e MOME; as versões adaptadas têm de ser partilhadas nos mesmos termos. Ver `LICENSE`.

A licença aplica-se ao standard. Não substitui a validação jurídica de cada licença-tipo nem dos documentos de cada projeto. Documento técnico de referência, não jurídico.

**Créditos tipográficos do booklet:** título em CC Accidenz Commons, de Archetypo (Joaquín Contreras e Miguel Hernández Montoya) para a Creative Commons, CC BY-SA 4.0; texto em IBM Plex Sans e IBM Plex Mono (SIL Open Font License).

## Autoria

Francisco Rocha Antunes · Filipa Serôdio Pinheiro · MOME, Porto

---

### In English

**Habitar Commons** is an open, modular classification of housing tenures and forms, modelled on Creative Commons. It describes any housing arrangement through seven layers, a short headline code and a machine-readable manifest checked by a declarative validator. Version 1.3 covers 18 base profiles in five families. Released by MOME (Porto, Portugal) under CC BY-SA 4.0.
