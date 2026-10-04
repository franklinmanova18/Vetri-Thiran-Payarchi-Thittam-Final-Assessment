import importlib


def test_backend_app_imports():
    module = importlib.import_module("backend.main")
    assert hasattr(module, "app")


def test_document_service_module_exists():
    service_module = importlib.import_module("services.document_service")
    assert hasattr(service_module, "DocumentService")
