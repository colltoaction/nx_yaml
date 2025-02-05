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
        kind "scalar"
        tag ""
        value "my node"
    ]
    node [
        id 5
        label 5
        bipartite 1
    ]
    edge [
        source 0
        target 1
        event "start"
    ]
    edge [
        source 1
        target 2
        event "end"
    ]
    edge [
        source 2
        target 3
        event "start"
    ]
    edge [
        source 3
        target 4
        event "end"
    ]
    edge [
        source 4
        target 5
        event "value"
    ]
]
