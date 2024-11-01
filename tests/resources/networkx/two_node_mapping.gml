graph [
    multigraph 1
    kind "mapping"
    node [
        id 0
        kind "scalar"
        bipartite 0
        value "left node"
        label "left node"
    ]
    node [
        id 1
        kind "scalar"
        bipartite 0
        value "right node"
        label "right node"
    ]
    node [
        id 2
        bipartite 1
        label "edge"
    ]
    edge[
        source 0
        target 1
    ]
    edge[
        source 0
        target 2
    ]
]
