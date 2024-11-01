graph [
    multigraph 1
    kind "sequence"
    node [
        id 0
        bipartite 0
        kind "scalar"
        value "left node"
        label "left node"
    ]
    node [
        id 1
        bipartite 0
        kind "scalar"
        value "right node"
        label "right node"
    ]
    node [
        id 2
        bipartite 1
        label 2
    ]
    edge[
        source 2
        target 0
        direction "head"
    ]
    edge[
        source 2
        target 1
        direction "tail"
    ]
]
