def _get_python_version():
    import sys
    return float('.'.join(map(str, sys.version_info[0:2])))


def import_module(module_name, module_path):
    python_version = _get_python_version()

    if python_version < 3.3:
        import imp
        return imp.load_source(module_name, module_path)
    elif python_version > 3.4:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    else:
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(module_name, module_path).load_module()
