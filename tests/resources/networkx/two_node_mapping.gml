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
        bipartite 1
    ]
    node [
        id 2
        label 2
        bipartite 0
        kind "scalar"
        value "left node"
    ]
    node [
        id 3
        label 3
        bipartite 1
    ]
    node [
        id 4
        label 4
        bipartite 0
        kind "scalar"
        value "right node"
    ]
    node [
        id 5
        label 5
        bipartite 1
    ]
    edge [
        source 1
        target 0
    ]
    edge [
        source 1
        target 2
    ]
    edge [
        source 3
        target 2
    ]
    edge [
        source 1
        target 4
    ]
    edge [
        source 5
        target 4
    ]
]
