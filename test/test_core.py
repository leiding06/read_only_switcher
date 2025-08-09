import unittest
import os
from qgis.core import QgsVectorLayer, QgsProject
from qgis.testing import TestCase
from unittest.mock import Mock, MagicMock

# Import plugin class
try:
    from read_only_switcher.read_only_switcher import ReadOnlySwitcher
except ImportError:
    # If relative import fails, try absolute import
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, parent_dir)
    from read_only_switcher import ReadOnlySwitcher


class TestReadOnlySwitcher(TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Initialize test data and plugin"""
        # Load test GeoPackage
        cls.test_data_path = os.path.join(
            os.path.dirname(__file__),
            "test_data",
            "test_data_editable_and_readonly.gpkg"
        )
        
        # Verify test data file exists
        if not os.path.exists(cls.test_data_path):
            raise FileNotFoundError(f"Test data file not found: {cls.test_data_path}")
        
        # Load layers with explicit OGR URI syntax
        cls.ro_layer = QgsVectorLayer(
            f"{cls.test_data_path}|layername=readonly_polygon", 
            "test_ro", 
            "ogr"
        )
        cls.edit_layer = QgsVectorLayer(
            f"{cls.test_data_path}|layername=editable_polygon",
            "test_edit",
            "ogr"
        )
        
        # Verify layer loading
        assert cls.ro_layer.isValid(), f"Failed to load read-only test layer from {cls.test_data_path}"
        assert cls.edit_layer.isValid(), f"Failed to load editable test layer from {cls.test_data_path}"
        
        # Add to project (required for some QGIS operations)
        QgsProject.instance().addMapLayers([cls.ro_layer, cls.edit_layer])
        
        # Create comprehensive mock iface
        cls.mock_iface = Mock()
        cls.mock_iface.mainWindow.return_value = Mock()
        
        # Mock layerTreeView with selectedLayers method
        cls.mock_layer_tree_view = Mock()
        cls.mock_iface.layerTreeView.return_value = cls.mock_layer_tree_view
        
        # Initialize plugin with mock iface
        cls.plugin = ReadOnlySwitcher(cls.mock_iface)
    
    def setUp(self):
        """Reset layer states before each test"""
        # Ensure layer states are known before each test
        self.ro_layer.setReadOnly(True)
        self.edit_layer.setReadOnly(False)
    
    def test_test_data_exists(self):
        """Verify test data file exists and is accessible"""
        self.assertTrue(os.path.exists(self.test_data_path), 
                       f"Test data file should exist at {self.test_data_path}")
    
    def test_layers_loaded(self):
        """Verify test layers are properly loaded"""
        self.assertTrue(self.ro_layer.isValid(), "Read-only test layer should be valid")
        self.assertTrue(self.edit_layer.isValid(), "Editable test layer should be valid")
        
        # Check layer feature counts
        self.assertGreater(self.ro_layer.featureCount(), 0, "Read-only layer should have features")
        self.assertGreater(self.edit_layer.featureCount(), 0, "Editable layer should have features")
    
    def test_initial_states(self):
        """Verify test data initial conditions"""
        self.assertTrue(self.ro_layer.readOnly(),
                       "Test layer should be read-only after setReadOnly(True)")
        self.assertFalse(self.edit_layer.readOnly(),
                        "Test layer should be editable after setReadOnly(False)")
    
    def test_plugin_initialization(self):
        """Test that plugin initializes correctly"""
        self.assertIsNotNone(self.plugin, "Plugin should initialize successfully")
        
        # Check if plugin has run method (your actual method)
        self.assertTrue(hasattr(self.plugin, 'run'), 
                       "Plugin should have run method")
    
    def test_run_with_single_readonly_layer(self):
        """Test plugin run method with single read-only layer selected"""
        # Setup mock: select read-only layer
        self.mock_layer_tree_view.selectedLayers.return_value = [self.ro_layer]
        
        # Ensure initial state
        self.ro_layer.setReadOnly(True)
        initial_state = self.ro_layer.readOnly()
        self.assertTrue(initial_state, "Layer should start as read-only")
        
        # Mock plugin run
        with unittest.mock.patch('qgis.utils.iface', self.mock_iface):
            self.plugin.run()
        
        # Verify state change
        final_state = self.ro_layer.readOnly()
        self.assertNotEqual(initial_state, final_state,
                          "Layer read-only state should change after run()")
        self.assertFalse(final_state, "Layer should now be editable")
    
    def test_run_with_single_editable_layer(self):
        """Test plugin run method with single editable layer selected"""
        # Setup mock: select editable layer
        self.mock_layer_tree_view.selectedLayers.return_value = [self.edit_layer]
        
        # Ensure initial state
        self.edit_layer.setReadOnly(False)
        initial_state = self.edit_layer.readOnly()
        self.assertFalse(initial_state, "Layer should start as editable")
        
        # Mock plugin run
        with unittest.mock.patch('qgis.utils.iface', self.mock_iface):
            self.plugin.run()
        
        # Verify state change
        final_state = self.edit_layer.readOnly()
        self.assertNotEqual(initial_state, final_state,
                          "Layer read-only state should change after run()")
        self.assertTrue(final_state, "Layer should now be read-only")
    
    def test_run_with_multiple_layers_same_state(self):
        """Test plugin run method with multiple layers having same state"""
        # Set both layers to read-only
        self.ro_layer.setReadOnly(True)
        self.edit_layer.setReadOnly(True)
        
        # Setup mock: select both layers
        self.mock_layer_tree_view.selectedLayers.return_value = [self.ro_layer, self.edit_layer]
        
        # Mock plugin run
        with unittest.mock.patch('qgis.utils.iface', self.mock_iface):
            self.plugin.run()
        
        # Verify both layers become editable
        self.assertFalse(self.ro_layer.readOnly(), "First layer should now be editable")
        self.assertFalse(self.edit_layer.readOnly(), "Second layer should now be editable")
    
    def test_run_with_no_selection(self):
        """Test plugin run method with no layers selected"""
        # Setup mock: no layers selected
        self.mock_layer_tree_view.selectedLayers.return_value = []
        
        # Mock QMessageBox.warning
        with unittest.mock.patch('qgis.PyQt.QtWidgets.QMessageBox.warning') as mock_warning:
            with unittest.mock.patch('qgis.utils.iface', self.mock_iface):
                self.plugin.run()
            
            # Verify warning message was displayed
            mock_warning.assert_called_once()
            # Check warning message content
            args, kwargs = mock_warning.call_args
            self.assertIn("No layers selected", args[1])  # Message text
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup"""
        QgsProject.instance().removeAllMapLayers()


if __name__ == "__main__":
    unittest.main(verbosity=2)