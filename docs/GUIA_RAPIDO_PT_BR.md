# Guia rápido do GROWN (português)

**GROWN** = **Growth through Reproducible, Orientation-aware Workflows
for Nanostructures**.

O GROWN permite preparar entradas reproduzíveis para crescimento
cristalino atomístico orientado por templates, comparando frentes X,
Y, Z e, com custo maior, direções simultâneas. O **Input Builder** é
o programa amigável para usuários que não querem editar manualmente
os ~100 parâmetros de linha de comando do motor científico.

## Instalação leve com pip

```bash
git clone https://github.com/tromer-unb/GROWN.git
cd GROWN
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
grown-input --help
```

## Instalação com Conda

```bash
git clone https://github.com/tromer-unb/GROWN.git
cd GROWN
conda env create -f environment.yml
conda activate grown
python -m pip install -e . --no-deps
```

**Estas instalações são do código-fonte no GitHub.** O programa
ainda não é um pacote formal publicado no PyPI ou no Conda. Para
preparar inputs, somente ASE, NumPy e SciPy são necessários.
Para efetivamente rodar o crescimento, instale separadamente
MACE, CHGNet, GPAW etc.

## Gerando o input: validação antes da simulação

```bash
grown-input validate software/GROWN_INPUT_BUILDER/examples/graphene_X.json
grown-input generate software/GROWN_INPUT_BUILDER/examples/graphene_X.json
grown-input status software/GROWN_INPUT_BUILDER/examples/generated/graphene_X
```

O segundo comando apenas **gera arquivos** `run.sh`, `job.pbs`, CIFs,
`validated_input.json`, relatório geométrico e cópia do motor. Não
executa cálculos energéticos nem envia trabalhos para o cluster.
Para o seu sistema, crie `grown-input init novo_caso.json`, informe
os caminhos dos CIFs, espécies, eixo, dimensão e parâmetros.

## Exemplos reais do artigo

- **Grafite Bernal AB:** inputs MACE para X, Y, Z com 100 adições;
  sementes C256 e periodicidades físicas distintas;
- **Grafeno / Si(100) / MoS₂:** cinco exemplos originais do Input Builder;
- **Grafeno sobre MoS₂ e SiC:** estruturas originais, templates do
  grafeno e comandos arquivados para MACE e CHGNet;
- **Defeitos:** probabilidades de vacância de 10% e 20%, N de 10% e
  substituição estocástica por boro no grafite;
- **Duas direções simultâneas:** funcionam, mas ficam muito caras para
  sistemas grandes. Recomenda-se usar células pequenas.

Tudo está organizado em [exemplos do artigo](PAPER_EXAMPLES.md).

## O que o método não garante

`events: 100` significa no máximo 100 eventos aceitos, não 100
tentativas. O crescimento pode parar normalmente por **ausência de
candidatos geométricos**, mesmo sem rejeição energética. O GROWN
não possui um potencial vdW próprio: as energias interlamelares
vêm do potencial escolhido. A energia de clivagem MACE de
**0,271 J/m²** versus referência ideal AB de **0,39 ± 0,02 J/m²**
é encorajadora na escala e sinal, mas 30,5% menor. Isso não
prediz cinética ou velocidade experimental de crescimento.

Mais detalhes no [manual completo (EN)](INPUT_BUILDER.md),
[configurações](CONFIG_REFERENCE.md) e [método](SCIENTIFIC_METHOD.md).
