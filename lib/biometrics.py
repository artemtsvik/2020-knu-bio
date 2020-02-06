from PIL import Image

def procces(im):
    pixels = im.load()
    v = []
    for i in range(im.size[0]):
        for j in range(im.size[1]):
            if sum(pixels[i,j])/3 > 126:
                v.append(1)
            else: v.append(-1)
    return v
