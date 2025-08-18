import unittest
import os
import sys
from unittest.mock import MagicMock

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from src.interfaces.web_app.interaction_handler import InteractionHandler
from src.knowledge_management.domain.model.graph import KnowledgeGraph
from src.knowledge_management.domain.model.node import Node
from src.knowledge_management.domain.model.edge import Edge

class TestInteractionHandler(unittest.TestCase):

    def setUp(self):
        """Set up a mock knowledge graph and an InteractionHandler instance for testing."""
        self.kg = KnowledgeGraph()
        self.visualizer = MagicMock()
        self.config = MagicMock()
        def config_get_side_effect(key, default=None):
            if key == 'search.search_fields':
                return ['label', 'type']
            if key == 'search.case_sensitive':
                return False
            return default
        self.config.get.side_effect = config_get_side_effect
        self.handler = InteractionHandler(self.kg, self.visualizer, self.config)

        # Add sample nodes
        self.node1 = Node(node_id='person1', label='Alice', node_type='person', properties={'age': 30})
        self.node2 = Node(node_id='org1', label='Google', node_type='organization', properties={'industry': 'Tech'})
        self.node3 = Node(node_id='person2', label='Bob', node_type='person', properties={'age': 25})
        self.kg.add_node(self.node1)
        self.kg.add_node(self.node2)
        self.kg.add_node(self.node3)

        # Add a sample edge
        self.edge1 = Edge(edge_id='edge1', source_id='person1', target_id='org1', label='works_at', weight=1.0)
        self.kg.add_edge(self.edge1)

    def test_search_nodes(self):
        """Test the node search functionality."""
        results = self.handler.search_nodes('Alice')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 'person1')

        results_case_insensitive = self.handler.search_nodes('google')
        self.assertEqual(len(results_case_insensitive), 1)
        self.assertEqual(results_case_insensitive[0]['id'], 'org1')
        
        results_no_match = self.handler.search_nodes('Charlie')
        self.assertEqual(len(results_no_match), 0)

    def test_filter_nodes_by_type(self):
        """Test filtering nodes by their type."""
        person_nodes = self.handler.filter_nodes_by_type(['person'])
        self.assertEqual(len(person_nodes), 2)
        self.assertIn('person1', person_nodes)
        self.assertIn('person2', person_nodes)

        org_nodes = self.handler.filter_nodes_by_type(['organization'])
        self.assertEqual(len(org_nodes), 1)
        self.assertEqual(org_nodes[0], 'org1')

    def test_add_node(self):
        """Test adding a new node."""
        new_node_id = self.handler.add_node('person3', 'Charlie', 'person', attributes={'age': 40})
        self.assertTrue(new_node_id)
        self.assertIn('person3', self.kg.nodes)
        node = self.kg.get_node('person3')
        self.assertEqual(node.label, 'Charlie')
        self.assertEqual(node.properties['age'], 40)

    def test_delete_node(self):
        """Test deleting a node."""
        result = self.handler.remove_node('person1')
        self.assertTrue(result)
        self.assertIsNone(self.kg.get_node('person1'))
        # Verify that the edge connected to the node is also deleted
        self.assertNotIn('edge1', self.kg.edges)

    def test_add_edge(self):
        """Test adding a new edge."""
        result = self.handler.add_edge('person2', 'org1', 'works_at', attributes={'since': '2022'})
        self.assertTrue(result)

        # Find the edge that was just added
        added_edge = None
        # The instruction implies get_all_edges() is the correct method to use.
        for edge in self.kg.get_all_edges():
            if edge.source_id == 'person2' and edge.target_id == 'org1' and edge.type == 'works_at':
                added_edge = edge
                break

        self.assertIsNotNone(added_edge)
        self.assertEqual(added_edge.properties.get('since'), '2022')

# Placeholder for web app tests
class TestWebApp(unittest.TestCase):

    def test_placeholder(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()