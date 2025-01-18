graph [
    directed 1
    node [
        id 0
        label 0
        bipartite 0
        kind "mapping"
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
    edge[
        source 0
        target 3
    ]
    edge[
        source 3
        target 1
    ]
    edge[
        source 2
        target 3
    ]
]
