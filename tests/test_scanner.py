
import pytest
from pathlib import Path
from src.nx_yaml import nx_compose_all
import networkx as nx

# Test cases: (filename, expected_doc_count)
# Files are located in tests/resources/yaml/
TEST_CASES = [
    # Reusing existing file
    ("empty.yaml", 0),
    # New integration file for directives
    ("scanner_directives.yaml", 3),
]

@pytest.mark.parametrize("filename, expected_doc_count", TEST_CASES)
def test_scanner_parametrized(filename, expected_doc_count):
    try:
        file_path = Path("tests/resources/yaml") / filename
        if not file_path.exists():
            pytest.fail(f"Test file not found: {file_path}")

        yaml_content = file_path.read_text()

        # We wrap the content in a way that nx_compose_all accepts (it takes a stream or string)
        graph = nx_compose_all(yaml_content)

        # Verify it's a tuple of graphs (V, E, I) (Nodes, Edges, Incidence)
        assert isinstance(graph, tuple)
        assert len(graph) == 3
        V, E, I = graph
        assert isinstance(V, nx.Graph)
        assert isinstance(E, nx.Graph)
        assert isinstance(I, nx.Graph)

        # Check for stream node
        stream_nodes = [n for n, d in V.nodes(data=True) if d.get('kind') == 'stream']
        assert len(stream_nodes) == 1
        stream_node = stream_nodes[0]

        # Check for document nodes connected to stream
        doc_nodes = [n for n, d in V.nodes(data=True) if d.get('kind') == 'document']
        assert len(doc_nodes) == expected_doc_count

    except Exception as e:
        pytest.fail(f"Failed to parse {filename}: {e}")
