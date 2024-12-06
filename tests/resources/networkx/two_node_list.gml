graph [
    multigraph 1
    directed 1
    kind "sequence"
    node [
        id 0
        label 0
        bipartite 0
        kind "sequence"
    ]
    node [
        id 1
        label 1
        bipartite 0
        kind "scalar"
        value "left node"
    ]
    node [
        id 2
        label 2
        bipartite 0
        kind "scalar"
        value "right node"
    ]
    node [
        id 3
        label 3
        bipartite 1
    ]
    node [
        id 4
        label 4
        bipartite 1
    ]
    edge[
        source 3
        target 0
    ]
    edge[
        source 1
        target 3
    ]
    edge[
        source 4
        target 1
    ]
    edge[
        source 2
        target 4
    ]
]
