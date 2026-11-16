# Subject-focused narration revision

All scene scripts were reviewed. Quoted Spanish passages below are source narration. The current downloadable MP4 is locally assembled with actual Google Vids speech; the complete native final export is pending the browser upload permission.

## method

Use the opening for the research objective rather than announcing how the video will read the paper.

Previous narration:

> Este es SEAL, un paper sobre modelos que aprenden a preparar sus propias actualizaciones de conocimiento. Vamos a leer sus figuras y sus resultados directamente. En la figura uno, el modelo recibe información y propone varias autoediciones: materiales e instrucciones para aprender. Cada candidata se utiliza para actualizar una copia del modelo. Después se evalúa esa copia en una tarea. El resultado sirve como recompensa para mejorar la generación de futuras autoediciones. Hay dos procesos distintos: aprender del material generado y aprender a generar material que realmente ayude.

Revised narration:

> SEAL investiga cómo un modelo puede preparar sus propias actualizaciones de conocimiento. El objetivo es adaptar sus pesos a nueva información y tareas. En la figura uno, el modelo recibe información y propone varias autoediciones: materiales e instrucciones para aprender. Cada candidata se utiliza para actualizar una copia del modelo. Después se evalúa esa copia en una tarea. El resultado sirve como recompensa para mejorar la generación de futuras autoediciones. Hay dos procesos distintos: aprender del material generado y aprender a generar material que realmente ayude.

## few-shot

Replace color/pointer commentary with the role of adapting the learning procedure to few examples.

Previous narration:

> La figura tres muestra otra aplicación. Ahora la entrada contiene ejemplos de pequeñas cuadrículas del conjunto ARC. La autoedición decide aumentos de datos, como rotaciones, y también parámetros de entrenamiento. Esas decisiones producen la adaptación del modelo, que después intenta resolver una entrada nueva. Aquí evolucionan las instrucciones de aprendizaje, además de los datos. Los colores de las cuadrículas pertenecen al problema original; el punto rojo identifica la parte del procedimiento que estamos explicando.

Revised narration:

> La figura tres muestra otra aplicación. Ahora la entrada contiene ejemplos de pequeñas cuadrículas del conjunto ARC. La autoedición decide aumentos de datos, como rotaciones, y también parámetros de entrenamiento. Esas decisiones producen la adaptación del modelo, que después intenta resolver una entrada nueva. Aquí evolucionan las instrucciones de aprendizaje, además de los datos. Así, el modelo puede elegir cómo aprovechar los pocos ejemplos disponibles para adaptarse a una tarea nueva.

## arc-table

Replace a statement that the chart repeats rows with the 52.5 percentage-point comparison; retain the selected-sample and denominator limitations.

Previous narration:

> Leamos la tabla uno. Sin adaptación, el resultado es cero. Con autoediciones sin aprendizaje previo por refuerzo, llega al veinte por ciento. SEAL alcanza setenta y dos coma cinco. La configuración humana de referencia alcanza cien. El gráfico de la derecha traduce exactamente esas filas. Pero esta cifra necesita contexto: se evaluaron ocho tareas seleccionadas de ARC, y la métrica cuenta autoediciones que terminan en una solución correcta. No significa que SEAL resuelva el setenta y dos por ciento de todo ARC.

Revised narration:

> Leamos la tabla uno. Sin adaptación, el resultado es cero. Con autoediciones sin aprendizaje previo por refuerzo, llega al veinte por ciento. SEAL alcanza setenta y dos coma cinco. La configuración humana de referencia alcanza cien. Son cincuenta y dos coma cinco puntos porcentuales más que sin refuerzo. Pero esta cifra necesita contexto: se evaluaron ocho tareas seleccionadas de ARC, y la métrica cuenta autoediciones que terminan en una solución correcta. No significa que SEAL resuelva el setenta y dos por ciento de todo ARC.
