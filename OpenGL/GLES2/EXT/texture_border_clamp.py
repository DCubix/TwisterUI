'''OpenGL extension EXT.texture_border_clamp

This module customises the behaviour of the 
OpenGL.raw.GLES2.EXT.texture_border_clamp to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/EXT/texture_border_clamp.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GLES2 import _types, _glgets
from OpenGL.raw.GLES2.EXT.texture_border_clamp import *
from OpenGL.raw.GLES2.EXT.texture_border_clamp import _EXTENSION_NAME

def glInitTextureBorderClampEXT():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )

# INPUT glTexParameterIivEXT.params size not checked against 'pname'
glTexParameterIivEXT=wrapper.wrapper(glTexParameterIivEXT).setInputArraySize(
    'params', None
)
# INPUT glTexParameterIuivEXT.params size not checked against 'pname'
glTexParameterIuivEXT=wrapper.wrapper(glTexParameterIuivEXT).setInputArraySize(
    'params', None
)
glGetTexParameterIivEXT=wrapper.wrapper(glGetTexParameterIivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
glGetTexParameterIuivEXT=wrapper.wrapper(glGetTexParameterIuivEXT).setOutput(
    'params',size=_glgets._glget_size_mapping,pnameArg='pname',orPassIn=True
)
# INPUT glSamplerParameterIivEXT.param size not checked against 'pname'
glSamplerParameterIivEXT=wrapper.wrapper(glSamplerParameterIivEXT).setInputArraySize(
    'param', None
)
# INPUT glSamplerParameterIuivEXT.param size not checked against 'pname'
glSamplerParameterIuivEXT=wrapper.wrapper(glSamplerParameterIuivEXT).setInputArraySize(
    'param', None
)
# INPUT glGetSamplerParameterIivEXT.params size not checked against 'pname'
glGetSamplerParameterIivEXT=wrapper.wrapper(glGetSamplerParameterIivEXT).setInputArraySize(
    'params', None
)
# INPUT glGetSamplerParameterIuivEXT.params size not checked against 'pname'
glGetSamplerParameterIuivEXT=wrapper.wrapper(glGetSamplerParameterIuivEXT).setInputArraySize(
    'params', None
)
### END AUTOGENERATED SECTION