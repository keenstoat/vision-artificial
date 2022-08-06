
import cv2
import numpy as np
import glob
import os
import sys
import re
import scipy.stats as stats
import matplotlib.pyplot as plt
import math

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
    if not os.path.exists(f"{image_dir}/{base_image_filename}"):
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

def anova_test(muestra_1, muestra_2):
    anova = stats.f_oneway(muestra_1, muestra_2)
    pvalue = anova.pvalue
    sigma = math.sqrt(1)
    x = np.arange(- 3*sigma, 3*sigma, 0.001)
    y = stats.norm.pdf(x, 0, sigma)

    x2 = np.arange(-1.645, 1.645, 0.001)
    y2 = stats.norm.pdf(x2,0,1)

    _, ax = plt.subplots(figsize=(9,6))
    plt.style.use('fivethirtyeight')
    ax.plot(x, y)
    ax.fill_between(x2, y2, 0, alpha=0.25, color='b')
    ax.text(-2.5, 0.3, f"confianza: 90%", size='large')
    ax.axvline(x=pvalue, color='g', lw=1)
    ax.text(pvalue+0.05, 0.05, f"p={pvalue:.4f}", color='g')
    ax.set_xlim([-3,3])
    ax.set_ylim([0,0.43])
    plt.savefig('anova.png', bbox_inches='tight')

    return anova


if __name__ == "__main__":
    sys.argv.pop(0)
    arg = sys.argv.pop(0) if sys.argv else "*"
    tallos_calculados_full = 0
    tallos_calculados_list = []
    tallos_esperados_list = []
    for sample_dir in glob.glob(f"grass-{arg}"):
        tallos_calculados = contar_tallos_grama(sample_dir)
        
        if sample_dir == "grass-full": 
            tallos_calculados_full = tallos_calculados
        
        tallos_esperados = glob.glob(f"{sample_dir}/grass-*-tallos*")
        if tallos_esperados: 
            tallos_esperados = re.match('.*grass-([0-9]+)-tallos.*', tallos_esperados[0])[1]
            tallos_esperados = int(tallos_esperados)
            # agregar tallos calculados ssi hay esperados
            tallos_esperados_list.append(tallos_esperados)
            tallos_calculados_list.append(tallos_calculados)
        else:
            tallos_esperados = "n/a"
        print(f"Tallos en {sample_dir}: calculados: {tallos_calculados} - esperados: {tallos_esperados}")

    print()

    media = np.mean(tallos_esperados_list)
    std = np.std(tallos_esperados_list)
    print("Tallos esperados en ventana de 512x512 px:")
    print(f"\tMedia: {media:.4f}\n\tDesv est: {std:.4f}")

    media = np.mean(tallos_calculados_list)
    std = np.std(tallos_calculados_list)
    print("Tallos calculados en ventana de 512x512 px:")
    print(f"\tMedia: {media:.4f}\n\tDesv est: {std:.4f}")

    ## ANOVA
    test = anova_test(tallos_esperados_list, tallos_calculados_list)
    
    ## ventanas particionadas de 512x512 en la imagen completa
    grass_full_image = cv2.imread("grass-full/grass.jpg")
    h, w = grass_full_image.shape[:2]
    particiones = (h * w) / 512**2

    print()
    print(f"Particiones de 512x512 en full:   {particiones:.4f}")
    print(f"Tallos calculados full:           {tallos_calculados_full}")
    print(f"Media tallos calculados full:     {(particiones * media):.4f}")
    print(f"Desv. est tallos calculados full: {(particiones * std):.4f}")
    print(f"ANOVA one-way:")
    print(f"\tF: {test.statistic:.4f}\n\tp: {test.pvalue:.4f}")
    
