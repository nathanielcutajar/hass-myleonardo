import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_tree():
    return ast.parse(
        (ROOT / "config_flow.py").read_text(encoding="utf-8")
    )


def get_function(class_name, function_name):
    for node in load_tree().body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (
                    isinstance(item, ast.AsyncFunctionDef)
                    and item.name == function_name
                ):
                    return item

    raise AssertionError(f"{class_name}.{function_name} not found")


def names_in(node):
    names = {
        item.id
        for item in ast.walk(node)
        if isinstance(item, ast.Name)
    }
    attrs = {
        item.attr
        for item in ast.walk(node)
        if isinstance(item, ast.Attribute)
    }

    return names | attrs


def constants_in(node):
    return {
        item.value
        for item in ast.walk(node)
        if isinstance(item, ast.Constant)
    }


class MyLeonardoConfigFlowStructureTest(unittest.TestCase):
    def test_user_step_routes_cloud_and_modbus_paths(self):
        function = get_function("MyLeonardoConfigFlow", "async_step_user")
        source_names = names_in(function)

        self.assertIn("CONNECTION_TYPE_MODBUS", source_names)
        self.assertIn("CONNECTION_TYPE_HYBRID", source_names)
        self.assertIn("CONNECTION_TYPE_CLOUD", source_names)
        self.assertIn("CONNECTION_TYPE_SELECTOR", source_names)

        source_constants = constants_in(function)
        self.assertIn("user", source_constants)

    def test_cloud_step_sets_unique_id_and_validates(self):
        function = get_function("MyLeonardoConfigFlow", "async_step_cloud")
        source_names = names_in(function)

        self.assertIn("CONF_API_KEY", source_names)
        self.assertIn("CONF_PLANT_KEY", source_names)
        self.assertIn("_async_try_validate_input", source_names)
        self.assertIn("async_set_unique_id", source_names)
        self.assertIn("_abort_if_unique_id_configured", source_names)

    def test_modbus_step_sets_unique_id_and_validates(self):
        function = get_function("MyLeonardoConfigFlow", "async_step_modbus")
        source_names = names_in(function)

        self.assertIn("CONF_MODBUS_HOST", source_names)
        self.assertIn("CONF_MODBUS_PORT", source_names)
        self.assertIn("_async_try_validate_modbus_input", source_names)
        self.assertIn("async_set_unique_id", source_names)
        self.assertIn("_abort_if_unique_id_configured", source_names)

    def test_hybrid_step_sets_unique_id_and_validates_both_sources(self):
        function = get_function("MyLeonardoConfigFlow", "async_step_hybrid")
        source_names = names_in(function)

        self.assertIn("CONF_API_KEY", source_names)
        self.assertIn("CONF_PLANT_KEY", source_names)
        self.assertIn("CONF_MODBUS_HOST", source_names)
        self.assertIn("CONF_MODBUS_PORT", source_names)
        self.assertIn("_async_try_validate_hybrid_input", source_names)
        self.assertIn("async_set_unique_id", source_names)
        self.assertIn("_abort_if_unique_id_configured", source_names)

    def test_cloud_options_use_cloud_polling_limits(self):
        function = get_function("MyLeonardoOptionsFlow", "async_step_init")
        source_names = names_in(function)

        self.assertIn("DEFAULT_REALTIME_SCAN_INTERVAL", source_names)
        self.assertIn("MIN_REALTIME_SCAN_INTERVAL", source_names)

    def test_modbus_options_use_modbus_polling_limits(self):
        function = get_function("MyLeonardoOptionsFlow", "_async_step_modbus")
        source_names = names_in(function)

        self.assertIn("DEFAULT_MODBUS_SCAN_INTERVAL", source_names)
        self.assertIn("MIN_MODBUS_SCAN_INTERVAL", source_names)

    def test_hybrid_options_use_modbus_and_cloud_polling_limits(self):
        function = get_function("MyLeonardoOptionsFlow", "_async_step_hybrid")
        source_names = names_in(function)

        self.assertIn("DEFAULT_MODBUS_SCAN_INTERVAL", source_names)
        self.assertIn("MIN_MODBUS_SCAN_INTERVAL", source_names)
        self.assertIn("DEFAULT_ENERGY_SCAN_INTERVAL", source_names)
        self.assertIn("MIN_ENERGY_SCAN_INTERVAL", source_names)
        self.assertIn("DEFAULT_ADVANCED_SCAN_INTERVAL", source_names)
        self.assertIn("MIN_ADVANCED_SCAN_INTERVAL", source_names)

    def test_reconfigure_supports_cloud_and_modbus_entries(self):
        function = get_function(
            "MyLeonardoConfigFlow",
            "async_step_reconfigure_confirm",
        )
        source_names = names_in(function)

        self.assertIn("CONNECTION_TYPE_MODBUS", source_names)
        self.assertIn("CONNECTION_TYPE_HYBRID", source_names)
        self.assertIn("_async_try_validate_modbus_input", source_names)
        self.assertIn("_async_try_validate_hybrid_input", source_names)
        self.assertIn("_async_try_validate_input", source_names)
        self.assertIn("async_update_entry", source_names)


if __name__ == "__main__":
    unittest.main()
