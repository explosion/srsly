#!/usr/bin/env python
import os
import subprocess
import sys
import contextlib
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc
from setuptools import Extension, setup, find_packages
from pathlib import Path


PACKAGE_DATA = {"": ["*.pyx", "*.pxd", "*.c", "*.h"]}
PACKAGES = find_packages()
MOD_NAMES = ["srsly.msgpack._unpacker", "srsly.msgpack._packer"]
COMPILE_OPTIONS = {
    "msvc": ["/Ox", "/EHsc"],
    "mingw32": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
    "other": ["-O2", "-Wno-strict-prototypes", "-Wno-unused-function"],
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
        for e in self.extensions:
            e.extra_compile_args += COMPILE_OPTIONS.get(
                self.compiler.compiler_type, COMPILE_OPTIONS["other"]
            )
        for e in self.extensions:
            e.extra_link_args += LINK_OPTIONS.get(
                self.compiler.compiler_type, LINK_OPTIONS["other"]
            )


class build_ext_subclass(build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        build_ext.build_extensions(self)


def generate_cython(root, source):
    print("Cythonizing sources")
    script = root / "bin" / "cythonize.py"
    p = subprocess.call([sys.executable, str(script), source], env=os.environ)
    if p != 0:
        raise RuntimeError("Running cythonize failed")


def clean(path):
    for name in MOD_NAMES:
        name = name.replace(".", "/")
        for ext in ["so", "html", "cpp", "c"]:
            file_path = path / f"{name}.{ext}"
            if file_path.exists():
                file_path.unlink()


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

    with chdir(root):
        with (root / "srsly" / "about.py").open("r") as f:
            about = {}
            exec(f.read(), about)

        include_dirs = [get_python_inc(plat_specific=True), ".", root / "include"]

        ext_modules = []
        for mod_name in MOD_NAMES:
            mod_path = mod_name.replace(".", "/") + ".cpp"
            extra_link_args = []
            extra_compile_args = []
            # ???
            # Imported from patch from @mikepb
            # See Issue #267. Running blind here...
            if sys.platform == "darwin":
                dylib_path = [".." for _ in range(mod_name.count("."))]
                dylib_path = "/".join(dylib_path)
                dylib_path = "@loader_path/%s/srsly/platform/darwin/lib" % dylib_path
                extra_link_args.append("-Wl,-rpath,%s" % dylib_path)
            ext_modules.append(
                Extension(
                    mod_name,
                    [mod_path],
                    language="c++",
                    include_dirs=include_dirs,
                    extra_link_args=extra_link_args,
                    define_macros=macros,
                    extra_compile_args=extra_compile_args,
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

        if not (root / "PKG-INFO").exists():  # not source release
            generate_cython(root, "srsly")

        setup(
            name="srsly",
            packages=PACKAGES,
            package_data=PACKAGE_DATA,
            version=about["__version__"],
            ext_modules=ext_modules,
            cmdclass={"build_ext": build_ext_subclass},
        )


if __name__ == "__main__":
    setup_package()
