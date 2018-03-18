import distutils.ccompiler
import distutils.dist
import glob
import io
import os

import cffi


# Get the directory for the cmark source files. It's under the package root
# as /third_party/cmark/src
HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.abspath(os.path.join(HERE, '../../'))
SRC_DIR = os.path.join(PACKAGE_ROOT, 'third_party/cmark/src')
EXTENSIONS_SRC_DIR = os.path.join(PACKAGE_ROOT, 'third_party/cmark/extensions')
GENERATED_SRC_DIR = os.path.join(PACKAGE_ROOT, 'generated')

with io.open(os.path.join(HERE, 'cmark.cffi.h'), 'r', encoding='utf-8') as fh:
    CMARK_DEF_H = fh.read()

with io.open(os.path.join(HERE, 'cmark_module.h'), 'r', encoding='utf-8') as fh:
    CMARK_MODULE_H = fh.read()


def _get_sources(dir, exclude=set()):
    sources = glob.iglob(os.path.join(dir, '*.c'))
    return [
        os.path.relpath(path, start=PACKAGE_ROOT)
        for path in
        sources
        if os.path.basename(path) not in exclude
    ]


SOURCES = _get_sources(SRC_DIR, exclude=set(['main.c']))
SOURCES.extend(_get_sources(EXTENSIONS_SRC_DIR))


def _compiler_type():
    """
    Gets the compiler type from distutils. On Windows with MSVC it will be
    "msvc". On macOS and linux it is "unix".

    Borrowed from https://github.com/pyca/cryptography/blob\
        /05b34433fccdc2fec0bb014c3668068169d769fd/src/_cffi_src/utils.py#L78
    """
    dist = distutils.dist.Distribution()
    dist.parse_config_files()
    cmd = dist.get_command_obj('build')
    cmd.ensure_finalized()
    compiler = distutils.ccompiler.new_compiler(compiler=cmd.compiler)
    return compiler.compiler_type


COMPILER_TYPE = _compiler_type()
if COMPILER_TYPE == 'unix':
    EXTRA_COMPILE_ARGS = ['-std=c99']
else:
    EXTRA_COMPILE_ARGS = None


ffibuilder = cffi.FFI()
ffibuilder.cdef(CMARK_DEF_H)
ffibuilder.set_source(
    'cmarkgfm._cmark',
    CMARK_MODULE_H,
    sources=SOURCES,
    include_dirs=[SRC_DIR, EXTENSIONS_SRC_DIR, GENERATED_SRC_DIR],
    extra_compile_args=EXTRA_COMPILE_ARGS
)


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)