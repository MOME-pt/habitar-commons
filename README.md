# Habitar Commons

**Classificação modular das formas de habitar, inspirada nos Creative Commons.**
Versão 2.0-rc1 (versão candidata) · novembro de 2026 · Jurisdição-alvo: Portugal

> **Estado.** A 2.0-rc1 é uma versão candidata. O regime cooperativo dos modelos da família HC (transmissão, oneração, reembolso e acesso da segunda geração) está sujeito a parecer jurídico; a v2.0 final publica-se depois desse parecer. A última versão estável é a [v1.3.1](https://github.com/MOME-pt/habitar-commons/releases/tag/v1.3.1). Ver `CHANGELOG.md`.

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
| `docs/` | Booklet v2.0-rc1 (PDF), cartões dos 19 perfis e poster A0 (PDF) e especificação completa (XLSX, 15 separadores, 64 decisões); versões anteriores em `archive/` |
| `spec/` | Catálogo dos 19 perfis (`profiles_v2_0.yaml`), ruleset (`rules_v2_0.yaml`, 46 regras) e esquema do manifesto (`manifest.schema.json`) |
| `validator/` | Validador de referência em Python (`validate.py`) |
| `tests/` | Manifesto de teste, 92 casos (dois por regra) e 12 casos de representação em `representation/` |
| `examples/` | Modelo `HC-CR-MID_v2_0.yaml`; versões anteriores em `archive/` |

### Validar um manifesto

```bash
pip install pyyaml jsonschema
python validator/validate.py examples/HC-CR-MID_v2_0.yaml
python tests/run_tests.py
```

## Como funciona

- **Âmbito:** só habitação. O título de ocupação é obrigatório; alojamento local, empreendimentos turísticos e habitação periódica ficam fora.
- **Sete camadas:** metadados; direito e titularidade; economia; governação e salvaguardas; modo de habitar; serviços e módulos; estrutura da operação. Acrescem um bloco físico, a estrutura de fluxos e preço, e a avaliação pós-ocupação.
- **Headline:** `H-<BASE>-<ECON>-<TERM>-<LOCK>`, derivado dos eixos pelo validador. Por exemplo, `H-MEMB-COST-MBR-PERP`: cooperativa de membros, preço ao custo, direito enquanto se for membro, acessibilidade vinculada sem prazo.
- **Manifesto:** a especificação completa em YAML ou JSON. Declara o arranjo; não o prova. A Camada 6 separa campos públicos e privados.
- **Validador:** verifica a coerência interna do manifesto (níveis sintático e semântico). Não verifica a conformidade jurídica nem o funcionamento real, que exigem verificação humana e avaliação pós-ocupação.
- **Classificação e selo:** qualquer arranjo habitacional pode ser classificado segundo o Habitar Commons. O selo Habitar Commons fica reservado aos arranjos desmercantilizados que cumpram critérios publicados, com verificação por terceiro.

## Catálogo v2.0: 19 perfis em 5 famílias

O identificador entre parênteses é imutável; o número P é só ordem de apresentação.

| Família | Perfis |
| --- | --- |
| Propriedade | P01 Compra (mercado) (`own-market`) · P02 Propriedade ao custo (autopromoção) (`own-cost`) · P03 Cohousing em propriedade (`cohousing-own`) · P04 Propriedade com revenda limitada (`own-resale-cap`) · P05 Híbridos (rent-to-buy, shared equity) (`hybrid-rtb`) |
| Arrendamento de mercado | P06 Arrendamento de mercado, duração média (`lease-market-mid`) · P07 Arrendamento de mercado estável (`lease-market-long`) · P08 Licença / subscrição (só com título habitacional) (`licence-sub`) |
| Arrendamento regulado e social | P09 Arrendamento com teto regulado (`lease-capped`) · P10 Arrendamento custo-base (`lease-cost`) · P11 Arrendamento social / renda apoiada (`lease-social`) · P12 Emergência / transição (`temporary-emergency`) |
| Cooperativa | P13 Cooperativa custo-base (`coop-cost`) · P14 Cooperativa social (`coop-social`) · P15 Cooperativa custo-base, duração média (`coop-cost-mid`) |
| Direitos reais e entidade guardiã | P16 Direitos reais limitados (`real-limited`) · P17 Usufruto ou DHD sénior com entrada (`senior-usufruct-entry`) · P18 Venda da nua propriedade com reserva de usufruto (`senior-bare-ownership`) · P19 Ativo em entidade guardiã (modelo CLT) (`guardian-clt`) |

## Contribuir

O Habitar Commons é um standard aberto e versionado. Abra uma *issue* para propor um perfil, um código ou uma regra, ou para classificar um modelo que não caiba no catálogo. Versionamento semântico: major quando muda o significado de eixos ou a forma do manifesto; minor quando acrescenta eixos, perfis ou regras; patch para correções. Os códigos retirados são aceites como sinónimos, com aviso, até à major seguinte.

## Licença

Publicado pela MOME sob a licença [Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/deed.pt). Pode usar, adaptar e partilhar, com atribuição a Francisco Rocha Antunes, Filipa Serôdio Pinheiro e MOME; as versões adaptadas têm de ser partilhadas nos mesmos termos. Ver `LICENSE`.

A licença aplica-se ao standard. Os modelos da família HC são modelos, não licenças-tipo: não substituem estatutos, regulamentos nem contratos. Documento técnico de referência, não jurídico.

## Autoria

Francisco Rocha Antunes · Filipa Serôdio Pinheiro · MOME, Porto

---

### In English

**Habitar Commons** is an open, modular classification of housing tenures and forms, modelled on Creative Commons. Version 2.0-rc1 (release candidate) covers 19 base profiles in five families, with a derived five-part headline, a machine-readable manifest and a declarative validator (46 rules). Released by MOME (Porto, Portugal) under CC BY-SA 4.0.
