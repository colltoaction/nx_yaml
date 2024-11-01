graph [
    multigraph 1
    kind "sequence"
    node [
        id 0
        bipartite 0
        kind "scalar"
        value "first"
        label 0
    ]
    node [
        id 1
        bipartite 0
        kind "scalar"
        value "second"
        label 1
    ]
    node [
        id 2
        bipartite 0
        kind "scalar"
        value "third"
        label 2
    ]
    node [
        id 3
        bipartite 0
        kind "scalar"
        value "fourth"
        label 3
    ]
    node [
        id 4
        bipartite 0
        kind "scalar"
        value "fifth"
        label 4
    ]
    node [
        id 5
        bipartite 0
        kind "scalar"
        value "sixth"
        label 5
    ]
    node [
        id 6
        label 6
        bipartite 1
    ]
    node [
        id 7
        label 7
        bipartite 1
    ]
    node [
        id 8
        label 8
        bipartite 1
    ]
    node [
        id 9
        label 9
        bipartite 1
    ]
    edge[
        source 0
        target 8
        direction "head"
    ]
    edge[
        source 1
        target 3
        direction "head"
    ]
    edge[
        source 1
        target 8
        direction "tail"
    ]
    edge[
        source 1
        target 9
        direction "head"
    ]
    edge[
        source 2
        target 3
        direction "tail"
    ]
    edge[
        source 2
        target 8
        direction "tail"
    ]
    edge[
        source 2
        target 9
        direction "head"
    ]
    edge[
        source 4
        target 6
        direction "head"
    ]
    edge[
        source 4
        target 8
        direction "tail"
    ]
    edge[
        source 4
        target 9
        direction "head"
    ]
    edge[
        source 5
        target 6
        direction "tail"
    ]
    edge[
        source 5
        target 8
        direction "tail"
    ]
    edge[
        source 5
        target 9
        direction "head"
    ]
    edge[
        source 7
        target 9
        direction "tail"
    ]
]
