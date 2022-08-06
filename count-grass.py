
import cv2
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

image_count = 1
image_dir = ""
image_extension = ""

def read_image(img_filename):
    return cv2.cvtColor(cv2.imread(f"{image_dir}/{img_filename}"), cv2.COLOR_BGR2RGB)

def write_image(name, image_array):
    global image_count
    cv2.imwrite(f"{image_dir}/{image_count}-{name}.{image_extension}", cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB))
    image_count +=1

def contar_tallos_grama(directory):

    global image_count
    global image_dir
    global image_extension
    image_count = 1
    image_dir = directory

    [os.remove(img) for img in glob.glob(f"{image_dir}/*") if not img.startswith(f"{image_dir}/grass")]

    base_image_filename = "grass.jpg"
    image_extension = "jpg"
    if not os.path.exists(base_image_filename):
        base_image_filename = "grass.png"
        image_extension = "png"
        
    # read image
    image_rgb = read_image(base_image_filename)

    ## GRAYSCALE =============================================================
    image_grayscale = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
    write_image("grayscale", image_grayscale)

    ## BINARIZACION DE GRAYSCALE =============================================================
    image = image_grayscale
    lower_theshold  = int(image.mean())
    write_image("binarizado-sin-suavizar", cv2.threshold(image, lower_theshold, 255, cv2.THRESH_BINARY)[1])
    image = cv2.medianBlur(image, 3)
    image = cv2.threshold(image, lower_theshold, 255, cv2.THRESH_BINARY)[1]
    image_binary = image
    write_image("binarizado", image_binary)

    ## DILATAR =============================================================
    image = image_binary
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    image = cv2.dilate(image, kernel, iterations=1)
    image_dilate = image
    write_image("dilatado", image_dilate)

    # GET DIFF =============================================================
    image = cv2.absdiff(image_dilate, image_binary)
    write_image("diff-dilatado-binarizado", image)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    # image = cv2.dilate(image, kernel, iterations=1)
    image_diff = image
    # plot_image(f"Dilatado(Dilatado - Binarizado)", image_diff)
    
    ## GET EGDES =============================================================
    image_edges = 255 - image_diff
    write_image("bordes-en-negro", image_edges)
    
    ## DILATAR LOS BORDES NEGROS ======
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
    image_edges = cv2.erode(image_edges, kernel, iterations=1)
    write_image("bordes-en-negro-dilatado", image_edges)
    
    ## REMOVER AREAS QUE SEGURO NO SON GRAMA ====================================
    image_edges[image_binary == 0] = 0
    write_image("remover-areas-sin-grama", image_edges)

    ## CONTORNOS =============================================================
    image = image_edges
    contours = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    
    image_contours = cv2.drawContours(image_rgb.copy(), contours, -1, (255, 0, 0), 2)
    write_image("contornos-full", image_contours)
    
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 50]
    image_contours = cv2.drawContours(image_rgb.copy(), contours, -1, (255, 0, 0), 2)
    write_image("contornos-significativos", image_contours)

    return len(contours)


for sample_dir in glob.glob(f"grass-*"):
    tallos = contar_tallos_grama(sample_dir)
    print(f"Tallos encontrados en {sample_dir}", tallos)