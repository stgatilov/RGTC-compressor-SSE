import os
from gen import genNormalMap

genNormalMap(1057, 952, 'input.tga')

def dotslash(cmd):
    if os.name != 'nt':
        return './' + cmd
    return cmd

os.system('%s  input.tga output.dds' % dotslash('NormalMap_TGA_RGBA8_to_DDS_RGTC'))

for algo in ['--sse', '--gen']:
    os.system('%s  input.tga __temp__.dds  %s --repeat 100' % (dotslash('NormalMap_TGA_RGBA8_to_DDS_RGTC'), algo))
