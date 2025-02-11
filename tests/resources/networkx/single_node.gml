graph [
    directed 1
    node [
        id 0
        label 0
        bipartite 0
    ]
    node [
        id 1
        label 1
        bipartite 1
        kind "stream"
    ]
    node [
        id 2
        label 2
        bipartite 1
    ]
    node [
        id 3
        label 3
        bipartite 0
    ]
    node [
        id 4
        label 4
        bipartite 1
        kind "document"
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
        kind "event"
        tag "DocumentStartEvent"
    ]
    node [
        id 7
        label 7
        bipartite 0
    ]
    node [
        id 8
        label 8
        bipartite 1
        kind "scalar"
        value "my node"
    ]
    node [
        id 9
        label 9
        bipartite 1
    ]
    node [
        id 10
        label 10
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 11
        label 11
        bipartite 0
        kind "event"
        tag "DocumentEndEvent"
    ]
    edge [
        source 0
        target 1
    ]
    edge [
        source 0
        target 2
    ]
    edge [
        source 1
        target 3
    ]
    edge [
        source 2
        target 6
    ]
    edge [
        source 2
        target 11
    ]
    edge [
        source 3
        target 4
    ]
    edge [
        source 3
        target 5
    ]
    edge [
        source 4
        target 7
    ]
    edge [
        source 5
        target 10
    ]
    edge [
        source 7
        target 8
    ]
    edge [
        source 7
        target 9
    ]
]