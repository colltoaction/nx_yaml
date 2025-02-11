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
        kind "sequence"
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
        tag "SequenceStartEvent"
    ]
    node [
        id 11
        label 11
        bipartite 0
    ]
    node [
        id 12
        label 12
        bipartite 1
        kind "mapping"
    ]
    node [
        id 13
        label 13
        bipartite 1
    ]
    node [
        id 14
        label 14
        bipartite 0
        kind "event"
        tag "MappingStartEvent"
    ]
    node [
        id 15
        label 15
        bipartite 0
    ]
    node [
        id 16
        label 16
        bipartite 1
        kind "scalar"
        value "a"
    ]
    node [
        id 17
        label 17
        bipartite 1
    ]
    node [
        id 18
        label 18
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 19
        label 19
        bipartite 0
    ]
    node [
        id 20
        label 20
        bipartite 1
        kind "mapping"
    ]
    node [
        id 21
        label 21
        bipartite 1
    ]
    node [
        id 22
        label 22
        bipartite 0
        kind "event"
        tag "MappingStartEvent"
    ]
    node [
        id 23
        label 23
        bipartite 0
    ]
    node [
        id 24
        label 24
        bipartite 1
        kind "scalar"
        value "b"
    ]
    node [
        id 25
        label 25
        bipartite 1
    ]
    node [
        id 26
        label 26
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 27
        label 27
        bipartite 0
    ]
    node [
        id 28
        label 28
        bipartite 1
        kind "scalar"
        value "c"
    ]
    node [
        id 29
        label 29
        bipartite 1
    ]
    node [
        id 30
        label 30
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 31
        label 31
        bipartite 0
    ]
    node [
        id 32
        label 32
        bipartite 1
        kind "scalar"
        value "d"
    ]
    node [
        id 33
        label 33
        bipartite 1
    ]
    node [
        id 34
        label 34
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 35
        label 35
        bipartite 0
    ]
    node [
        id 36
        label 36
        bipartite 1
        kind "scalar"
        value "e"
    ]
    node [
        id 37
        label 37
        bipartite 1
    ]
    node [
        id 38
        label 38
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 39
        label 39
        bipartite 0
        kind "event"
        tag "MappingEndEvent"
    ]
    node [
        id 40
        label 40
        bipartite 0
        kind "event"
        tag "MappingEndEvent"
    ]
    node [
        id 41
        label 41
        bipartite 0
    ]
    node [
        id 42
        label 42
        bipartite 1
        kind "mapping"
    ]
    node [
        id 43
        label 43
        bipartite 1
    ]
    node [
        id 44
        label 44
        bipartite 0
        kind "event"
        tag "MappingStartEvent"
    ]
    node [
        id 45
        label 45
        bipartite 0
    ]
    node [
        id 46
        label 46
        bipartite 1
        kind "scalar"
        value "c"
    ]
    node [
        id 47
        label 47
        bipartite 1
    ]
    node [
        id 48
        label 48
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 49
        label 49
        bipartite 0
    ]
    node [
        id 50
        label 50
        bipartite 1
        kind "scalar"
    ]
    node [
        id 51
        label 51
        bipartite 1
    ]
    node [
        id 52
        label 52
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 53
        label 53
        bipartite 0
    ]
    node [
        id 54
        label 54
        bipartite 1
        kind "scalar"
        value "d"
    ]
    node [
        id 55
        label 55
        bipartite 1
    ]
    node [
        id 56
        label 56
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 57
        label 57
        bipartite 0
    ]
    node [
        id 58
        label 58
        bipartite 1
        kind "scalar"
    ]
    node [
        id 59
        label 59
        bipartite 1
    ]
    node [
        id 60
        label 60
        bipartite 0
        kind "event"
        tag "ScalarEvent"
    ]
    node [
        id 61
        label 61
        bipartite 0
        kind "event"
        tag "MappingEndEvent"
    ]
    node [
        id 62
        label 62
        bipartite 0
        kind "event"
        tag "SequenceEndEvent"
    ]
    node [
        id 63
        label 63
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
        target 63
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
        source 5
        target 62
    ]
    edge [
        source 7
        target 8
    ]
    edge [
        source 7
        target 9
    ]
    edge [
        source 8
        target 11
    ]
    edge [
        source 8
        target 41
    ]
    edge [
        source 9
        target 14
    ]
    edge [
        source 9
        target 40
    ]
    edge [
        source 9
        target 44
    ]
    edge [
        source 9
        target 61
    ]
    edge [
        source 11
        target 12
    ]
    edge [
        source 11
        target 13
    ]
    edge [
        source 12
        target 15
    ]
    edge [
        source 12
        target 19
    ]
    edge [
        source 13
        target 18
    ]
    edge [
        source 13
        target 22
    ]
    edge [
        source 13
        target 39
    ]
    edge [
        source 15
        target 16
    ]
    edge [
        source 15
        target 17
    ]
    edge [
        source 19
        target 20
    ]
    edge [
        source 19
        target 21
    ]
    edge [
        source 20
        target 23
    ]
    edge [
        source 20
        target 27
    ]
    edge [
        source 20
        target 31
    ]
    edge [
        source 20
        target 35
    ]
    edge [
        source 21
        target 26
    ]
    edge [
        source 21
        target 30
    ]
    edge [
        source 21
        target 34
    ]
    edge [
        source 21
        target 38
    ]
    edge [
        source 23
        target 24
    ]
    edge [
        source 23
        target 25
    ]
    edge [
        source 27
        target 28
    ]
    edge [
        source 27
        target 29
    ]
    edge [
        source 31
        target 32
    ]
    edge [
        source 31
        target 33
    ]
    edge [
        source 35
        target 36
    ]
    edge [
        source 35
        target 37
    ]
    edge [
        source 41
        target 42
    ]
    edge [
        source 41
        target 43
    ]
    edge [
        source 42
        target 45
    ]
    edge [
        source 42
        target 49
    ]
    edge [
        source 42
        target 53
    ]
    edge [
        source 42
        target 57
    ]
    edge [
        source 43
        target 48
    ]
    edge [
        source 43
        target 52
    ]
    edge [
        source 43
        target 56
    ]
    edge [
        source 43
        target 60
    ]
    edge [
        source 45
        target 46
    ]
    edge [
        source 45
        target 47
    ]
    edge [
        source 49
        target 50
    ]
    edge [
        source 49
        target 51
    ]
    edge [
        source 53
        target 54
    ]
    edge [
        source 53
        target 55
    ]
    edge [
        source 57
        target 58
    ]
    edge [
        source 57
        target 59
    ]
]