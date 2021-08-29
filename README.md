# RGTC-compressor-SSE
Compress normal map quickly from 8-bit RGBA to RGTC using SSE2

### Introduction

OpenGL supports [RGTC](https://www.khronos.org/opengl/wiki/Red_Green_Texture_Compression) format for normal maps, also called [BC5](https://en.wikipedia.org/wiki/S3_Texture_Compression#BC4_and_BC5).
While compressing all textures offline is the best idea, sometimes it is necessary to compress textures on the fly.
This repository contains fast SSE2 code for converting RGBA8 image to RGTC format with mipmaps.

### Usage

Build the only .cpp file using C++ compiler of choice.
Don't forget to enable optimization and `-msse2`.

You can use resulting executable to convert 24-bit TGA file into compressed DDS file:

    NormalMap_TGA_RGBA8_to_DDS_RGTC input.tga output.dds
    
There are also a few scripts for testing:

 * `gen.py`: generates normal map of perlin noise height map for testing
 * `test.py`: runs generic and SSE2 code path on the test image

### Algorithm

All mipmap levels are generated from the input RGBA8 texture using simple box filter, with average values rounded to the nearest integer (rounding up in case of tie).
Each mipmap level is compressed to RGTC.

For compression, the image is split into 4x4 blocks.
If dimensions are not divisible by 4, then boundary blocks are padded like with "clamp" wrapping mode.
Red and green channels of each block are compressed individually.

Given a single-channel block, minimum and maximum values are computed.
These values are used as minimum and maximum ramp points, and six additional ramp points are implicitly generated between them.
Each value in a block is usually snapped to the closest ramp point, which is written to output.

Due to precision limitations, sometimes a value which is very close to the middle between two neighboring ramp points is snapped in wrong direction.
This never happens in low-variation blocks: it can only happen when maxValue - minValue > 64.

The code contains "generic" code path, which is slow but simple, and fast "sse2" code path.
Both code paths yield exactly the same output.

### Speed

Results on Ryzen 1600 (one core) for image of size 952 x 1057:

    Running SSE-accelerated code 100 times took 190.00 milliseconds
    Running generic code 100 times took 1096.00 milliseconds
    
It is about 2 ms per megapixel for vectorized code path.

### License

The code is licensed under Boost Software License.

I initially committed the main parts of this code to TheDarkMod source code, which is licensed under GPL:

    r9561
    #5716. Added CompressRGTCFromRGBA8 method to idSIMD.
    ---------------------
    r9558
    #5716. Function R_MipMap is accelerated by SSE2.
    ---------------------

But since I am the sole author of the code, I may distribute it separately under a different license, which I do here.
