graph [
    multigraph 1
    kind "mapping"
    node [
        id 0
        bipartite 0
        kind "scalar"
        value "my node"
        label 0
    ]
    node [
        id 1
        bipartite 0
        kind "scalar"
        value "my node"
        label 1
    ]
    node [
        id 2
        bipartite 1
        label 2
    ]
    edge [
        source 0
        target 1
        direction "tail"
    ]
    edge [
        source 0
        target 2
        direction "head"
    ]
]
