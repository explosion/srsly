#!/usr/bin/env python
import sys
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc
from setuptools import Extension, setup, find_packages
from pathlib import Path
from Cython.Build import cythonize
from Cython.Compiler import Options
import contextlib
import os


# Preserve `__doc__` on functions and classes
# http://docs.cython.org/en/latest/src/userguide/source_files_and_compilation.html#compiler-options
Options.docstrings = True


PACKAGE_DATA = {"": ["*.pyx", "*.pxd", "*.c", "*.h"]}
PACKAGES = find_packages()
MOD_NAMES = ["srsly.msgpack._unpacker", "srsly.msgpack._packer"]
COMPILE_OPTIONS = {
    "msvc": ["/Ox", "/EHsc"],
    "mingw32": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
    "other": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
}
COMPILER_DIRECTIVES = {
    "language_level": -3,
    "embedsignature": True,
    "annotation_typing": False,
}
LINK_OPTIONS = {"msvc": [], "mingw32": [], "other": ["-lstdc++", "-lm"]}

if sys.byteorder == "big":
    macros = [("__BIG_ENDIAN__", "1")]
else:
    macros = [("__LITTLE_ENDIAN__", "1")]


# By subclassing build_extensions we have the actual compiler that will be used
# which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
class build_ext_options:
    def build_options(self):
        if hasattr(self.compiler, "initialize"):
            self.compiler.initialize()
        self.compiler.platform = sys.platform[:6]
        for e in self.extensions:
            e.extra_compile_args += COMPILE_OPTIONS.get(
                self.compiler.compiler_type, COMPILE_OPTIONS["other"]
            )
            e.extra_link_args += LINK_OPTIONS.get(
                self.compiler.compiler_type, LINK_OPTIONS["other"]
            )


class build_ext_subclass(build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        build_ext.build_extensions(self)


def clean(path):
    n_cleaned = 0
    for name in MOD_NAMES:
        name = name.replace(".", "/")
        for ext in ["so", "html", "cpp", "c"]:
            file_path = path / f"{name}.{ext}"
            if file_path.exists():
                file_path.unlink()
                n_cleaned += 1
    print(f"Cleaned {n_cleaned} files")


@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


def setup_package():
    root = Path(__file__).parent

    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        return clean(root)

    with (root / "srsly" / "about.py").open("r") as f:
        about = {}
        exec(f.read(), about)

    with chdir(str(root)):
        include_dirs = [get_python_inc(plat_specific=True), "."]
        ext_modules = []
        for name in MOD_NAMES:
            mod_path = name.replace(".", "/") + ".pyx"
            ext_modules.append(
                Extension(
                    name,
                    [mod_path],
                    language="c++",
                    include_dirs=include_dirs,
                    define_macros=macros,
                )
            )
        ext_modules.append(
            Extension(
                "srsly.ujson.ujson",
                sources=[
                    "./srsly/ujson/ujson.c",
                    "./srsly/ujson/objToJSON.c",
                    "./srsly/ujson/JSONtoObj.c",
                    "./srsly/ujson/lib/ultrajsonenc.c",
                    "./srsly/ujson/lib/ultrajsondec.c",
                ],
                include_dirs=["./srsly/ujson", "./srsly/ujson/lib"],
                extra_compile_args=["-D_GNU_SOURCE"],
            )
        )
        print("Cythonizing sources")
        ext_modules = cythonize(ext_modules, compiler_directives=COMPILER_DIRECTIVES, language_level=2)

        setup(
            name="srsly",
            packages=PACKAGES,
            version=about["__version__"],
            ext_modules=ext_modules,
            cmdclass={"build_ext": build_ext_subclass},
            package_data=PACKAGE_DATA,
        )


if __name__ == "__main__":
    setup_package()
