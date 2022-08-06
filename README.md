
# Estimacion del cantidad tallos de grama en una imagen

### Vision Artificial 2022 - Carlos Josue Avila - carne: 20016235

## Abstracto

Este proyecto consiste en contar el numero de tallos de grama en una imagen de manera que se pueda estimar el numero de tallos de grama en un area de mayor tamaño.

Para esto se procesado imagenes de muestra de 512x512 pixeles. Estas muestras se han tomado como segmentos de imagenes de mayor tamaño.

El proceso consiste en transformaciones a la imagen de manera que se puedan encontrar contornos en la misma. 



# Procedimiento

## Toma de muestras para analisis
Dada una fotografia de un area con grama como la siguiente:

<table><thead><tr><th>
Fotografia completa de grama
</th></tr></thead><tbody><tr><td>
<img src="imagen-grama-full.jpg">
</td></tr></tbody></table>

Se han tomado 5 imagenes de muestra de 512 x 512 pixeles.

<table><thead><tr><th>
Muestra de 512 x 512 pixeles
</th></tr></thead><tbody><tr><td>
<img src="grass-1/grass.png">
</td></tr></tbody></table>


## Escala de grises

La muestra es convertida a escala de grises. Esto reduce los canales de colores a solamente uno.
<table><thead><tr><th>
Escala de grises
</th></tr></thead><tbody><tr><td>
<img src="grass-1/1-grayscale.png">
</td></tr></tbody></table>


## Binarizacion

Luego la imagen es binarizada con un umbral del valor de la media artimetica de la imagen.

Antes de realizar la binarizacion la imagen es suavizada con un filtro de mediana. Esto remueve los detalles muy finos de la grama en la imagen y asi la binarizacion queda con menos ruido.

Como se puede observar en las imagenes siguientes cuando se binariza solamente algunas orillas tienen un poco de ruido, parece sal y pimienta.

Por otro lado cuando la imagen se suaviza antes de binarizar, el ruido se reduce y las orillas se observan mas fluidas.
<table>
<thead>
  <tr>
    <th>Solo Binarizado</th>
    <th>Suavizado + Binarizado</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><img src="grass-1/2-binarizado-sin-suavizar.png"></td>
    <td><img src="grass-1/3-binarizado.png"></td>
  </tr>
</tbody>
</table>

## Deteccion de Bordes

El siguiente paso es la deteccion de bordes. 

Este paso se considero con Canny pero los bordes resultantes no daban resultados satisfactorios por lo que se procedio con un metodo de aplicacion de mascara.

Primero se dilata la imagen binarizada (del paso anterior) con un kernel de 5x5
<table><thead><tr><th>
Dilatacion de imagen binarizada
</th></tr></thead><tbody><tr><td>
<img src="grass-1/4-dilatado.png">
</td></tr></tbody></table>

Luego se toma la diferencia absoluta entre la imagen dilatada y la imagen binarizada. 
> La imagen binarizada actua como mascara
<table><thead><tr><th>
Diferencia absoluta: Dilatacion - Binarizacion
</th></tr></thead><tbody><tr><td>
<img src="grass-1/5-diff-dilatado-binarizado.png">
</td></tr></tbody></table>

Finalmente se invierte el color blanco con el negro para tener una imagen resultante con areas blancas y bordes negros.
<table><thead><tr><th>
Inversion de color
</th></tr></thead><tbody><tr><td>
<img src="grass-1/6-bordes-en-negro.png">
</td></tr></tbody></table>

## Diferenciacion de grama y no grama

El paso anterior, la deteccion de bordes, resulta en una imagen donde no se distingue que es el fondo (areas negras) y que es grama (areas blancas).

Este es un problema ya que al hacer la deteccion de contornos solamente se quiere detectar contornos que correspondan a tallos de grama - areas blancas.

Ademas de esto, algunos bordes no son continuos. Se puede observar que donde dos o mas tallos de grama se traslapan se crea un borde que es el perimetro de estos multiples tallos.

Para corregir esto se erosiona la imagen con un kernel de 7x7. Esto tiene el efecto de dilatar las areas negras.

> La funcion de dilatacion engrosa o dilata las areas blancas. La funcion de erosion adelgaza o erosiona las areas blancas. Esto es lo mismo que dilatar las areas negras.
<table><thead><tr><th>
Dilatacion de bordes negros con erosion
</th></tr></thead><tbody><tr><td>
<img src="grass-1/7-bordes-en-negro-dilatado.png">
</td></tr></tbody></table>

Luego se cubren las areas que se sabe de seguro que no son grama. 

> De la imagen binarizada se sabe que todo pixel negro no es grama asi que se utiliza nuevamente como mascara para colocar en color negro los espacios que se sabe deben ser el fondo de la imagen

<table><thead><tr><th>
Remover areas que no son grama
</th></tr></thead><tbody><tr><td>
<img src="grass-1/8-remover-areas-sin-grama.png">
</td></tr></tbody></table>

## Deteccion de contornos

Finalmente se buscan los contornos en la imagen. 

> Un contorno es un perimetro cerrado

Dado a que el proceso de deteccion de bordes no es perfecto se tienen algunas pequeñas areas blancas. Estas areas blancas son resultado del cruce de tallos de grama. 

Se experimento la dilatacion de bordes negros utilizando kernels mas grandes que 7x7 pero se observo que esto resultaba en la reduccion de las areas blancas que si son significativas.

Para discriminar estos contornos minusculos se consideran solamente los contornos con mas de 50 pixeles de area.

> El umbral de 50 pixeles de area se definio mediante ensayo y error

A continuacion se muestra la comparacion. Se observa que los contornos que corresponden a areas muy pequeñas han sido eliminados.

<table>
<thead>
  <tr>
    <th>Todos los contornos</th>
    <th>Contornos significativos</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><img src="grass-1/9-contornos-full.png"></td>
    <td><img src="grass-1/10-contornos-significativos.png"></td>
  </tr>
</tbody>
</table>

# Resultados

Para poder evaluar la exactitud y precision del proceso de deteccion de contornos, en la imagen de muestra se han contado los tallos de grama a simple vista y se han marcado con una linea roja.

Durante la implementacion del proceso se observo que es muy complicado detectar claramente tallos de grama individuales.

La principal dificultad es que los tallos de grama se traslapan entre si de tal manera que al binarizar la imagen se crean formas que ya no parecen tallos de grama. 

El desorden de la grama es una fuente significativa de incertidumbre en el proceso de conteo.

Por esta razon se resolvio el problema como un metodo de aproximacion promedio.

> Todas las transformaciones realizadas y sus metricas (como el tamaño de kernels, umbral de binarizacion, entre otros) han sido ajustados mediante ensayo y error de manera que el numero de contornos encontrados se ajuste lo mejor posible al numero de tallos de grama contados manualmente.

A continuacion se muestra la comparacion entre el valor esperado y el valor calculado por la aplicacion.

## Muestra 1
<table>
<thead>
  <tr>
    <th>Tallos de grama contados manualmente - 55</th>
    <th>Contornos significativos encontrados - 53</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><img src="grass-1/grass-55-tallos.png"></td>
    <td><img src="grass-1/10-contornos-significativos.png"></td>
  </tr>
</tbody>
</table>

## Muestra 2
<table>
<thead>
  <tr>
    <th>Tallos de grama contados manualmente - 53</th>
    <th>Contornos significativos encontrados - 50</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><img src="grass-2/grass-53-tallos.png"></td>
    <td><img src="grass-2/10-contornos-significativos.png"></td>
  </tr>
</tbody>
</table>

## Muestra 3
<table>
<thead>
  <tr>
    <th>Tallos de grama contados manualmente - 72</th>
    <th>Contornos significativos encontrados - 62</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><img src="grass-3/grass-72-tallos.png"></td>
    <td><img src="grass-3/10-contornos-significativos.png"></td>
  </tr>
</tbody>
</table>

## Muestra 4
<table>
<thead>
  <tr>
    <th>Tallos de grama contados manualmente - 133</th>
    <th>Contornos significativos encontrados - 72</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><img src="grass-4/grass-133-tallos.png"></td>
    <td><img src="grass-4/10-contornos-significativos.png"></td>
  </tr>
</tbody>
</table>

## Muestra 5
<table>
<thead>
  <tr>
    <th>Tallos de grama contados manualmente - 68</th>
    <th>Contornos significativos encontrados - 64</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><img src="grass-5/grass-68-tallos.png"></td>
    <td><img src="grass-5/10-contornos-significativos.png"></td>
  </tr>
</tbody>
</table>
