# Subject-focused narration revision

All scene scripts were reviewed. Quoted Spanish passages below are source narration. The current downloadable MP4 is locally assembled with actual Google Vids speech; the complete native final export is pending the browser upload permission.

## parallel-work

Replace a production disclaimer with the thread/block mechanism and the use of its results.

Previous narration:

> Veámoslo como un reparto de trabajo. La CPU prepara los datos y lanza un kernel: una función que ejecutan muchos hilos. Los hilos se organizan en bloques. La GPU calcula partes de la operación y entrega resultados. La animación representa el mecanismo; no mide una aceleración concreta.

Revised narration:

> La CPU prepara los datos y lanza un kernel: una función que ejecutan muchos hilos. Cada hilo calcula una parte del trabajo; los hilos se organizan en bloques. Al multiplicar matrices, muchos de esos cálculos pueden avanzar en paralelo. La GPU entrega los resultados, que se utilizan para continuar el entrenamiento.

## alexnet-model

Replace a comment about the simplified drawing with the learned hierarchy used for classification.

Previous narration:

> En 2012, tres investigadores de la Universidad de Toronto presentaron AlexNet: Alex Krizhevsky, Ilya Sutskever y Geoffrey Hinton. Son los coautores de una red profunda entrenada eficientemente en GPU. Su arquitectura tenía cinco capas convolucionales y tres totalmente conectadas. Los píxeles atravesaban etapas que aprendían características hasta producir categorías. El esquema simplifica las ocho capas con pesos.

Revised narration:

> En 2012, tres investigadores de la Universidad de Toronto presentaron AlexNet: Alex Krizhevsky, Ilya Sutskever y Geoffrey Hinton. Son los coautores de una red profunda entrenada eficientemente en GPU. Su arquitectura tenía cinco capas convolucionales y tres totalmente conectadas. Los píxeles atraviesan capas que aprenden patrones simples y los combinan en características más complejas. Las capas finales utilizan esa información para asignar categorías.
