import unittest
import os
import sys

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.knowledge_management.domain.model.graph import KnowledgeGraph
from src.knowledge_management.domain.model.node import Node
from src.knowledge_management.domain.model.edge import Edge

class TestKnowledgeGraph(unittest.TestCase):

    def test_create_empty_graph(self):
        """Test creating an empty knowledge graph."""
        graph = KnowledgeGraph()
        self.assertEqual(len(graph.nodes), 0)
        self.assertEqual(len(graph.edges), 0)

    def test_add_node(self):
        """Test adding a node to the graph."""
        graph = KnowledgeGraph()
        node = Node(node_id='1', label='Person', properties={'name': 'John Doe'})
        graph.add_node(node)
        self.assertEqual(len(graph.nodes), 1)
        self.assertEqual(graph.nodes['1'], node)

    def test_add_edge(self):
        """Test adding an edge to the graph."""
        graph = KnowledgeGraph()
        node1 = Node(node_id='1', label='Person', properties={'name': 'John Doe'})
        node2 = Node(node_id='2', label='City', properties={'name': 'New York'})
        graph.add_node(node1)
        graph.add_node(node2)
        edge = Edge(edge_id='e1', source_id='1', target_id='2', label='LIVES_IN')
        graph.add_edge(edge)
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.edges['e1'], edge)

if __name__ == '__main__':
    unittest.main()