import os
from importlib import import_module
from types import ModuleType

path = f"{os.getcwd()}/src/process"
tar_dirs = [d for d in os.listdir(path) if not (d.startswith("_") or d == "common")]
modules = [import_module(f"process.{d}.run") for d in tar_dirs]
funcs = [[d for d in dir(mod) if d.startswith("run_")][0] for mod in modules]
run_mod_funcs: list[tuple[ModuleType, str]] = list(zip(modules, funcs))
run_functions = [getattr(mod, func) for mod, func in run_mod_funcs]
