# 🕸️ nx_yaml

[![PyPI version](https://img.shields.io/pypi/v/nx_yaml.svg)](https://pypi.org/project/nx_yaml/)
[![License: CC0 1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](LICENSE)
[![Network Science](https://img.shields.io/badge/Field-Network%20Science-orange.svg)](https://doi.org/10.1017/nws.2025.10018)

`nx_yaml` bridges [YAML](https://yaml.org/spec/1.2.2) documents and [NetworkX](https://github.com/networkx/networkx) by representing YAML as the standard [Hypergraph Interchange Format (HIF)](https://doi.org/10.1017/nws.2025.10018). For YAML users, this unlocks higher-order graph theory analysis, moving beyond simple tree parsing. For the HIF ecosystem, it provides human-readable native support for higher-order program descriptions.

## Features

*   **Isomorphic Conversion**: Losslessly convert between YAML character streams and NetworkX hypergraphs using `nx_hif`.
*   **Round-Trip Property**: Ensuring full structural and syntactic preservation:
    *   `serialize(compose(yaml)) == yaml`
    *   `compose(serialize(hif)) == hif`
*   **Formal Hypergraph Definition**: Implements the [Hypergraph Interchange Format](https://doi.org/10.1017/nws.2025.10018).
*   **NetworkX Ecosystem**: Built to interoperate with the broader NetworkX ecosystem and libraries.
*   **Extensible**: Designed for further support of diverse higher-order representations.


## Ecosystem Compatibility

`nx_yaml` enables interoperability across projects in the Higher-order Network Science community, including the [HIF-standard](https://github.com/pszufe/HIF-standard):

*   **General Purpose**: [NetworkX](https://github.com/networkx/networkx)
*   **Higher-order Networks**: [HyperNetX](https://github.com/pnnl/hypernetx), [XGI](https://github.com/xgi-org/xgi), [hypergraphx](https://github.com/HGX-Team/hypergraphx), [SimpleHypergraphs.jl](https://github.com/pszufe/SimpleHypergraphs.jl), [Easy-Graph](https://github.com/easy-graph/Easy-Graph), [DeepHypergraph](https://github.com/iMoonLab/DeepHypergraph), [Hypergraph Analysis Toolbox](https://github.com/Jpickard1/Hypergraph-Analysis-Toolbox), [uunet](https://github.com/uuinfolab/uunet)
*   **Temporal & Multilayer**: [networkx-temporal](https://github.com/nelsonaloysio/networkx-temporal), [pymnet](https://github.com/mnets/pymnet), [reticula](https://github.com/reticula-network/reticula), [Raphtory](https://github.com/Pometry/Raphtory), [ASH](https://github.com/GiulioRossetti/ASH)
*   **Visualization**: [helios-web](https://github.com/filipinascimento/helios-web), [pygraphistry](https://github.com/graphistry/pygraphistry)
*   **Categorical & Monoidal**: [catgrad](https://github.com/hellas-ai/catgrad), [Hypergraph](https://github.com/Cobord/Hypergraph)


## Citation

If you use `nx_yaml` in your research, please consider citing the above work:

```bibtex
@article{Coll_Joslyn_Landry_Lotito_Myers_Pickard_Praggastis_Szufel_2025,
  title={HIF: The hypergraph interchange format for higher-order networks},
  volume={13},
  DOI={10.1017/nws.2025.10018},
  journal={Network Science},
  author={Coll, Martín and Joslyn, Cliff A. and Landry, Nicholas W. and Lotito, Quintino Francesco and Myers, Audun and Pickard, Joshua and Praggastis, Brenda and Szufel, Przemysław},
  year={2025},
  pages={e21}
}
```

## License

`nx_yaml` is dedicated to the public domain under the [CC0 1.0 Universal](LICENSE) license.
