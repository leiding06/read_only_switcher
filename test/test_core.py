import os
import unittest
from qgis.core import QgsVectorLayer, QgsProject

from ..read_only_switcher import determine_new_state, toggle_read_only

class TestReadOnlySwitcher(unittest.TestCase):
    def setUp(self):
        path = os.path.join(os.path.dirname(__file__), "test_data", "test_data_editable_and_readonly.gpkg")

        self.editable_layer = QgsVectorLayer(f"{path}|layername=editable_polygon", "editable_polygon", "ogr")
        self.assertTrue(self.editable_layer.isValid())

        self.readonly_layer = QgsVectorLayer(f"{path}|layername=read_only_polygon", "read_only_polygon", "ogr")
        self.assertTrue(self.readonly_layer.isValid())

        QgsProject.instance().addMapLayer(self.editable_layer)
        QgsProject.instance().addMapLayer(self.readonly_layer)

    def test_determine_new_state(self):
        result = determine_new_state([self.editable_layer, self.readonly_layer])
        self.assertIsNotNone(result)

        has_non_vector, new_state, has_mixed_status, previous_state, vector_layers = result
        self.assertFalse(has_non_vector)
        self.assertTrue(has_mixed_status)
        self.assertTrue(new_state)  # mix
        self.assertEqual(previous_state, "mixed")
        self.assertEqual(set(vector_layers), {self.editable_layer, self.readonly_layer})

    def test_toggle_read_only(self):
        # set editable
        toggle_read_only([self.editable_layer, self.readonly_layer], False)
        self.assertFalse(self.editable_layer.readOnly())
        self.assertFalse(self.readonly_layer.readOnly())

        # set editable
        toggle_read_only([self.editable_layer, self.readonly_layer], True)
        self.assertTrue(self.editable_layer.readOnly())
        self.assertTrue(self.readonly_layer.readOnly())

if __name__ == '__main__':
    unittest.main()
