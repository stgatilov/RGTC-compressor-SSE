import os
from PIL import Image   # pip install Pillow
import noise            # pip install noise
import numpy as np      # pip install numpy


# normal map generator taken from: https://gist.github.com/Huud/63bacf5b8fe9b7b205ee42a786f922f0

# a function that takes a vector - three numbers - and normalize it, i.e make it's length = 1
def normalizeRGB(vec):
    length = np.sqrt(vec[:,:,0]**2 + vec[:,:,1]**2 + vec[:,:,2]**2)
    vec[:,:,0] = vec[:,:,0] / length
    vec[:,:,1] = vec[:,:,1] / length
    vec[:,:,2] = vec[:,:,2] / length
    return vec

# height_image_path is a string to your height map file, e.g "C:\mymap.png":
def heightMapToNormalMap(image):   
    # only use one channel, it can be any sice B&W image channels are equal
    # image = image[:,:,0]
    
    # initialize the normal map, and the two tangents:
    normalMap = np.zeros((image.shape[0],image.shape[1],3))
    tan       = np.zeros((image.shape[0],image.shape[1],3))
    bitan     = np.zeros((image.shape[0],image.shape[1],3))
    
    # we get the normal of a pixel by the 4 pixels around it, sodefine the top, buttom, left and right pixels arrays,
    # which are just the input image shifted one pixel to the corrosponding direction. We do this by padding the image
    # and then 'cropping' the unneeded sides
    B = np.pad(image,1,mode='edge')[2:,1:-1]
    T = np.pad(image,1,mode='edge')[:-2,1:-1]
    L = np.pad(image,1,mode='edge')[1:-1,0:-2]
    R = np.pad(image,1,mode='edge')[1:-1,2:]
    
    # to get a good scale/intensity multiplier, i.e a number that let's the R and G channels occupy most of their available  
    # space between 0-1 without clipping, we will start with an overly strong multiplier - the smaller the the multiplier is, the
    # stronger it is -, to practically guarantee clipping then incrementally increase it until no clipping is happening

    scale = .05
    while True:
        
        #get the tangents of the surface, the normal is thier cross product
        tan[:,:,0],tan[:,:,1],tan[:,:,2]       = np.asarray([scale, 0 , R-L], dtype=object)
        bitan[:,:,0],bitan[:,:,1],bitan[:,:,2] = np.asarray([0, scale , B-T], dtype=object)
        normalMap = np.cross(tan,bitan)

        # normalize the normals to get their length to 1, they are called normals after all
        normalMap = normalizeRGB(normalMap)
        
        # increment the multiplier until the desired range of R and G is reached 
        if scale > 2: break
        if np.max(normalMap[:,:,0]) > 0.95  or np.max(normalMap[:,:,1]) > 0.95 \
        or np.min(normalMap[:,:,0]) < -0.95 or np.min(normalMap[:,:,1]) < -0.95:
            scale += .05
            continue
        else: 
            break
    
    # calculations were done for the channels to be in range -1 to 1 for the channels, however the image saving function
    # expects the range 0-1, so just divide these channels by 2 and add 0.5 to be in that range, we also flip the 
    # G channel to comply with the OpenGL normal map convention
    normalMap[:,:,0] = (normalMap[:,:,0]/2)+.5
    normalMap[:,:,1] = (0.5-(normalMap[:,:,1]/2))
    normalMap[:,:,2] = (normalMap[:,:,2]/2)+.5
    
    # normalizing does most of the job, but clip the remainder just in case 
    normalMap = np.clip(normalMap,0.0,1.0)
    return normalMap


def genNormalMap(width, height, filename):
    shape = (width, height)
    scale = 100.0
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0

    world = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            world[i][j] = noise.pnoise2(i/scale, 
                                        j/scale, 
                                        octaves=octaves, 
                                        persistence=persistence, 
                                        lacunarity=lacunarity, 
                                        repeatx=1024, 
                                        repeaty=1024, 
                                        base=0)

    normalmap = heightMapToNormalMap(world)
    normalmap = np.insert(normalmap, 3, 1.0, axis=2)
    image = Image.fromarray(np.uint8(normalmap * 255))

    image.save(filename)


if __name__ == "__main__":
    genNormalMap(1024, 1024, 'input.tga')
