graph [
    directed 1
    node [
        id 0
        label 0
        bipartite 0
        kind "stream"
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
        kind "document"
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
        kind "mapping"
    ]
    node [
        id 5
        label 5
        bipartite 1
    ]
    node [
        id 6
        label 6
        bipartite 0
        kind "scalar"
        value "node"
        anchor "n"
    ]
    node [
        id 7
        label 7
        bipartite 1
    ]
    node [
        id 8
        label 8
        bipartite 0
        kind "alias"
        anchor "n"
    ]
    node [
        id 9
        label 9
        bipartite 1
    ]
    edge [
        source 0
        target 1
    ]
    edge [
        source 1
        target 2
    ]
    edge [
        source 2
        target 3
    ]
    edge [
        source 3
        target 4
    ]
    edge [
        source 4
        target 5
    ]
    edge [
        source 5
        target 6
    ]
    edge [
        source 6
        target 7
    ]
    edge [
        source 5
        target 8
    ]
    edge [
        source 8
        target 9
    ]
]
