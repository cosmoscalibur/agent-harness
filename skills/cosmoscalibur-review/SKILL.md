---
name: cosmoscalibur-review
description: >-
  Heurísticas personales de code review de @cosmoscalibur, sintetizadas de
  revisiones manuales reales sobre varios repos. Complementa (no reemplaza)
  al skill genérico `review`: úsalo como una pasada adicional después de esa
  revisión estándar, o cuando @cosmoscalibur pida revisar con "su estilo".
  Independiente de stack — para convenciones específicas de Django/DRF, usa
  además `django-review` cuando el repo lo sea.
---

# Code Review — estilo cosmoscalibur

Estas reglas se extrajeron de comentarios de revisión reales sobre PRs de
varios repos, no son teoría genérica. Cada una nació de un caso concreto de
código real, generalizado aquí para que aplique más allá del repo puntual
donde se observó. Úsalas **después** de correr `review` (o el pase estándar
equivalente) — esta es una capa de criterio adicional, no un reemplazo de las
pasadas de corrección/rendimiento/adversarial. Si el repo es Django/DRF, corre
también `django-review` después de esta.

## Reglas

- **Defensividad injustificada en superficies internas.** Un endpoint o
  función interna cuyo único caller es código que controlas end-to-end (no un
  tercero) no necesita un `try/except` genérico, ni un casteo defensivo, ni
  una validación de payload "por si acaso" alrededor de algo que "podría
  fallar", si no hay evidencia real (un incidente medido, no hipotético) de
  que ese escenario ocurre. El costo de la protección injustificada no es solo
  código de más: convierte un fallo real en un error silencioso que el equipo
  ignora, y deja ciego a soporte/ingeniería cuando el caller realmente rompe
  el contrato. Reventar es preferible a tragar el error, salvo que (a) haya
  evidencia de incidencia real y (b) el consumidor tenga manejo adecuado de
  ese fallo sin afectar al usuario final. Aplica igual a validación de payload
  que a I/O (un `try/except` alrededor de un side-effect que nunca ha fallado
  en producción). Ver `django-review` para el caso concreto de un endpoint
  DRF.

  - **Caveat que importa — verifica esto ANTES de pedir que se quite un
    guard: ¿remover el guard produce una falla real, o deja pasar el dato
    inválido sin ninguna falla?** "Dejar que reviente" solo es la alternativa
    correcta cuando el dato inválido rompe algo por su cuenta más adelante
    (un cast numérico sobre texto no numérico lanza una excepción; un objeto
    nulo sobre el que se accede un atributo también). Si el dato inválido es
    del MISMO TIPO que uno válido pero fuera de rango de negocio (un año que
    sigue siendo un entero válido para la columna, un id que no corresponde a
    nada pero tiene el formato correcto), quitar el check no causa ningún
    reventón — causa que el dato malo se persista silenciosamente con una
    respuesta exitosa. Eso es estrictamente peor que el error que se estaba
    tratando de eliminar.

    No es una regla binaria "si no revienta solo, el guard se queda" — la
    decisión depende de qué tan probable es el escenario, con tres salidas
    posibles, no dos:
    1. **Genuinamente improbable** (el emisor del dato es un cliente que
       controlas y nunca lo generaría): está bien eliminar el guard sin
       reemplazo. Aceptar el riesgo residual es una decisión válida.
    2. **Probabilidad real pero baja, y no revienta solo**: eliminar el
       guard sin más no basta — hace falta loguear manualmente la anomalía
       (una excepción/warning explícito cuando el dato fuera de rango
       aparece) para tener visibilidad, aunque no se rechace la request.
    3. **Probabilidad no despreciable**: ahí sí se mantiene el rechazo — la
       validación no era defensividad de sobra, es una regla de negocio real.
    Antes de aceptar que un guard se quite bajo el principio de "no seas
    defensivo", pregunta las dos cosas en orden: primero "¿qué tan probable
    es este escenario, con qué evidencia?", y solo si la respuesta es
    "improbable" preguntas "¿qué línea de código de verdad explota si pasa
    de todos modos?" — si ninguna explota y la probabilidad no es
    despreciable, el punto medio (logging manual sin rechazar) es una
    respuesta legítima que no habías considerado solo con "mantener vs.
    eliminar".

  - **Ajuste cuando el riesgo es sobre un patrón compartido, no de un
    endpoint puntual.** Si el escenario aceptado como riesgo es sobre un
    patrón de entrada que comparten *todos* los endpoints de una entidad (no
    uno aislado), la protección pertenece a la capa compartida (permisos),
    no reimplementada por feature — reimplementarla por endpoint es la misma
    defensividad injustificada, solo que repetida N veces en vez de una.

- **Sospecha de justificación de negocio inventada por el agente para
  respaldar una decisión técnica ya tomada.** Cuando una elección técnica
  (soft-delete, una restricción de borrado en cascada, una interfaz de
  administración) se justifica con una palabra de negocio ("auditoría",
  "control de calidad") que no aparece en ningún requerimiento/ticket real,
  sospecha que el agente construyó el requerimiento para justificar la
  decisión, no al revés — ver `agent-harness.md` §1. Verificación concreta:
  si la "auditoría" fuera real, ¿se conserva historial de ediciones, no solo
  el estado de borrado? Si el contenido es editable sin versión previa, la
  narrativa de auditoría ya se contradice a sí misma. Verifica también que la
  restricción no esté resolviendo un problema que el sistema ya resuelve de
  otra forma (una restricción contra un borrado duro de usuario que en la
  práctica no ocurre, cuando el modelo de usuario ya tiene su propio
  soft-delete vía un flag de estado). Y cuando invalides esa premisa, reabre
  lo que dependía de ella: la alternativa que el PR ya descartó citando esa
  misma necesidad (p. ej. JSON en el padre en vez de una tabla de filas)
  merece reconsiderarse, no darse por cerrada solo porque el PR la mencionó
  una vez.

- **Arquitectura primero, con evidencia estructural — a cualquier nivel de
  granularidad.** Antes de aceptar una superficie completa (una interfaz de
  administración, un endpoint, un servicio) como necesaria, pregunta si otra
  ya resuelve el caso de uso. Antes de aceptar un patrón de código inusual
  (un mixin no visto en el repo, la sobreescritura explícita de un default
  del framework) como un idiom razonable, corre una búsqueda estructural
  (`ast-grep`/`grep`) para confirmar que es genuinamente inédito antes de
  discutirlo como tal — ver `agent-harness.md` §4.

- **Tras un cambio de firma (rename de método, parámetros nuevos/distintos,
  cambio de tipo), audita *todos* los call sites — con LSP, no grep.** Usa
  `LSP prepareCallHierarchy` + `incomingCalls` sobre la definición del
  método: devuelve cada call site real con el nombre de la función que lo
  envuelve, sin ruido de imports, strings en `__all__`, ni coincidencias de
  texto en comentarios — grep sí trae ese ruido, y además puede fallar en
  silencio si el método se invoca a través de una variable/alias. Si `LSP`
  no está disponible para el lenguaje, `findReferences` es la alternativa
  (menos preciso: no agrupa por función llamante, y sí cuenta menciones no
  ejecutables). **Ojo con la primera consulta tras iniciar el servidor**:
  puede devolver resultados incompletos (no vacíos — ese es el caso
  engañoso) mientras termina de indexar el workspace; si el conteo se ve
  bajo para un símbolo que sabes que se usa en varios módulos, repite la
  consulta una vez antes de confiar en el resultado. Verificado en la
  práctica: una primera llamada a `findReferences` devolvió 2 de 10
  referencias reales; la segunda, ya con el índice completo, las 10. Ver
  `django-review` para el caso concreto de un rename que se coló sin este
  chequeo.

- **Un guard que "no debería pasar nunca" oculta el bug, no lo previene.**
  Si un valor debería existir siempre por construcción del flujo (viene de
  una URL con id garantizado, de una operación que ya se validó antes, de un
  registro creado en el mismo request), un `if x is None: return` silencioso
  sobre ese valor no es manejo de error — es enmascarar un bug real detrás de
  un no-op. Antes de aceptar ese guard, pide el escenario concreto donde el
  valor sí puede faltar; si no existe, el código debe fallar ruidosamente
  (dejar que reviente, o usar un lookup que falle en vez de uno que degrade a
  `None`) para que el bug se vea la primera vez que ocurre, no se pierda como
  un retorno silencioso.

- **No revalides una invariante que el caller ya garantiza.** Si un
  método/servicio documenta que es exclusivo de un contexto (p. ej. "solo
  para el flujo X"), y **todos** sus call sites ya filtran por ese contexto
  antes de invocarlo, no dupliques la misma validación adentro. Esa
  redundancia no es "doble seguridad" gratuita: implica que el componente en
  realidad es más genérico de lo que su documentación dice, y añade una
  segunda fuente de verdad para la misma regla que puede desalinearse con la
  primera. La responsabilidad del gate vive en un solo lugar — verifica cuál
  es el más natural (normalmente el caller, que ya sabe por qué invoca) y
  deja que el resto confíe en él.

- **Pasa lo que se usa, no el objeto completo.** Si una función solo lee el
  `id` (o dos o tres campos puntuales) de un objeto relacionado, que reciba
  esos valores directamente en la firma — no el objeto entero. No lo trates
  como un caso aparte solo porque el objeto ya lo tenías en memoria (p. ej.
  el usuario de la sesión actual): pasar el objeto completo cuando el `id`
  basta es el mismo acoplamiento innecesario, tenga la forma de un parámetro
  de función o de un filtro de consulta. Ver `django-review` para la versión
  disfrazada de este patrón en filtros de ORM.

- **Sin consultas redundantes cuando el caller ya tiene el dato.** Antes de
  aceptar que un método interno "re-consulte por aislamiento" un registro que
  el caller ya cargó, evalúa si el caller puede simplemente ampliar su propia
  selección de campos/relaciones para incluir lo que hace falta. El
  aislamiento entre capas no justifica pagar una consulta extra si el dato ya
  está en memoria un nivel más arriba.

- **Una sola fuente de verdad para el mismo concepto de negocio.** Si dos
  funciones distintas necesitan evaluar la misma condición de dominio (p. ej.
  "¿esta declaración ya quedó presentada/finalizada?"), deben apoyarse en el
  mismo predicado compartido, no reimplementar cada una su propia versión de
  la condición. Que diverjan — aunque sea en un solo campo omitido — es un
  bug de inconsistencia esperando a manifestarse, no un nit de estilo. La
  regla se confirma también entre métodos, no solo entre archivos: dos
  métodos que evalúan la misma condición (p. ej. "es propietario y es
  administrador") con lógica escrita dos veces por separado es
  sobre-desagregación prematura, no separación de responsabilidades —
  sepáralos solo cuando la regla real diverja.

- **Un TODO/nota de trabajo pendiente vive en un solo sitio — el más
  natural para encontrarlo, no todos los que lo tocan.** Mismo principio que
  la fuente de verdad de arriba, pero para documentación en vez de lógica.
  Si un campo necesita una nota de "esto hay que migrarlo/limpiarlo", esa
  nota va donde alguien revisaría ese campo primero (típicamente el modelo
  que lo define), no repetida — ni siquiera parcialmente — en cada
  servicio/vista que lo consume. Un TODO repartido en dos archivos, ninguno
  siendo "el" completo, es sobredocumentación: cuando alguien lo resuelve en
  un sitio, el otro queda desactualizado y nadie nota la desalineación hasta
  la siguiente revisión. Antes de agregar una nota de pendiente en un
  archivo nuevo, pregunta si ya existe (o debería existir) en un lugar más
  natural, y consolida ahí en vez de duplicar.

- **Un campo/toggle legacy que un cambio reemplaza necesita una decisión
  explícita sobre su ciclo de vida.** No basta con que el nuevo mecanismo
  "gane" en la lógica nueva si el campo viejo sigue siendo escribible en
  otro lado. El PR debe decidir y dejar constancia: ¿se da de baja (con TODO
  de migración/backfill), o hay una razón real para que siga vivo en
  paralelo? Ambigüedad sin decisión documentada no es aceptable — aunque la
  decisión sea "se deja como TODO con cifras concretas medidas" (backfill
  pendiente cuantificado), eso ya es una respuesta válida; "no se mencionó"
  no lo es.

  - **"Legacy" y "necesita backfill antes de poder ignorarse" son
    contradictorios — no dejes pasar la etiqueta sin el matiz.** Si un campo
    de verdad no importa, no hace falta migrar su dato a ningún lado; si
    hace falta un backfill para no perder información real (cifras medidas
    en producción/STG, no una suposición), ese campo sigue siendo una fuente
    de verdad viva hoy, aunque esté camino a desaparecer. Llamarlo "legacy"
    sin esa aclaración subestima el riesgo de la ventana entre "se ignora en
    código" y "el backfill corrió".
  - **No agregues código ni tests nuevos que dependan de un campo ya marcado
    para baja.** Si algo se está desmontando, la superficie que lo toca debe
    reducirse, no crecer — incluye tests: escribir un test nuevo que
    instancia el campo legacy (aunque sea para probar que ahora se ignora)
    es una dependencia nueva sobre algo que se supone va de salida. La
    garantía de que se ignora debería bastarle al código/TODO existente sin
    necesitar cobertura adicional que cementa su presencia.

- **Un patrón copiado de otro módulo necesita que su justificación de fondo
  también aplique aquí.** Si el PR adopta un patrón existente (soft-delete
  porque otro modelo lo usa, un `try/except` porque otro endpoint lo tiene)
  citando el precedente como razón, verifica que la necesidad real detrás de
  ese precedente (auditoría, trazabilidad, incidente conocido) exista también
  en el caso nuevo. La analogía sin ese chequeo es copiar la forma sin la
  función.

- **YAGNI en representaciones sin consumidor.** No agregues `__str__`,
  propiedades derivadas, o una representación de API "por convención"/"por
  si se necesita" si nada las consume todavía (ni una interfaz de
  administración, ni logs, ni un endpoint). Si no se usa, no se define — se
  agrega cuando aparezca el primer consumidor real.

- **Simplifica lo que se usa una sola vez.** Una variable intermedia que
  solo se lee una vez y no aporta claridad de nombre puede asignarse/pasarse
  directo en el punto de uso.

- **Revisa la reversibilidad de cada estado terminal en una máquina de
  estados.** Para cualquier estado que no tiene transición manual de salida
  (un "no aplica"/"terminado"), confirma explícitamente si existe un camino
  de vuelta razonable — aunque sea automático en vez de manual — o si su
  ausencia está justificada. No lo des por sentado solo porque el mapa de
  transiciones "se ve completo".

- **Las convenciones de nombrado de dominio ya acordadas se hacen cumplir,
  no se repiten como sugerencia.** Si el equipo ya estableció un prefijo o
  patrón de nombrado para un dominio específico (p. ej. un prefijo que marca
  "exclusivo de un producto/flujo concreto"), un componente nuevo de ese
  dominio que no lo sigue es una desviación a corregir en el mismo PR, no una
  preferencia de estilo opcional para después. La taxonomía no es solo de
  carpetas ni de prefijos de negocio: antes de nombrar algo `*Service`,
  confirma que cumple el patrón semántico que ese término ya tiene en el
  repo, no solo que vive en `services/`.

- **Si aceptas el principio de "no seas defensivo si controlas el input",
  aplícalo a todo el diff, no solo al primer sitio donde lo notaste.** Es
  común que un fix quite un `try/except` de una línea pero deje un
  `.get(..., default)` o un `or []` dos líneas abajo, sobre exactamente la
  misma premisa (el caller es tuyo, la config es tuya). Después de encontrar
  el primer caso de defensividad injustificada, vuelve a barrer el mismo
  método/archivo preguntando la misma cosa de cada guard restante: ¿qué
  escenario real lo activaría? Un fallback sobre configuración transversal
  que la aplicación entera necesita (settings, feature flags de
  infraestructura) es el caso más engañoso: si faltara, ya habría roto otras
  partes del sistema antes de llegar a tu guard, así que el fallback no
  previene nada — solo posterga el error a un punto donde es más difícil de
  diagnosticar.

- **Un docstring/comentario no mezcla idiomas dentro del mismo bloque.** Si
  el archivo/módulo ya está escrito en español, un término técnico en inglés
  suelto ("backfill", "legacy") está bien si no tiene traducción natural o es
  jerga ya asumida por el equipo, pero evita alternar frases completas entre
  los dos idiomas en el mismo párrafo — léelo de corrido y confirma que no
  suena a spanglish.

- **Documentación como ruido — señales de nota personal del agente.** Cada
  capa documenta su propia responsabilidad: un campo de ayuda de UI
  (`help_text` en Django, `description` en otros frameworks) es significado
  de negocio, no formato ni la regla que ya lo gobierna (eso vive en el
  validador); la razón de una decisión de implementación vive en el código
  que la implementa, no repetida en un doc de dominio y el changelog. El
  listón no es "a mí me costó entenderlo", es "un mantenedor futuro lo
  necesita y no puede obtenerlo de otra parte" — ver `agent-harness.md` §2.
  Señales concretas de que un párrafo es nota personal del agente, no
  documentación: comparar con un modelo sin relación funcional, fijar una
  versión de librería inline, explicar el framework/ORM en vez de la
  decisión propia, o un prefijo tipo "Resumen:" en un docstring técnico (la
  documentación técnica declara hechos, no resume para un lector no
  técnico). Explicar en el punto de consumo la lógica que vive en otro
  módulo (p. ej. permisos) es la misma falla de capa mal ubicada.

- **El diseño debe servir el objetivo real de negocio, no solo ser
  consistente internamente.** Cardinalidad no restringida es una decisión de
  producto a confirmar explícitamente, y la pregunta correcta es la más
  fina, no la más obvia: no "¿puede haber N registros por cliente?" (obvio),
  sino "¿puede el mismo autor dejar N registros en el mismo periodo, o
  debería ser 1?". Lo mismo aplica a UX/API: un flag como `can_edit`
  necesita trazarse a un flujo real resuelto (¿qué pasa si el registro está
  mal y no lo puede corregir el autor — escala a soporte?), y ocultar datos
  en el backend que el frontend podría simplemente no renderizar no es una
  ganancia de diseño sin una razón de negocio o seguridad real detrás — es
  un problema adicional para quien necesite ese dato después. Y el nombre no
  debe contradecir las restricciones reales: un campo llamado "de texto
  libre" contradicho por un máximo de longitud y una validación de
  no-solo-espacios — reserva "libre" para lo que de verdad no tiene
  restricciones más allá de ser texto — ver el product-intent pass de
  `review`.

## Formato

Igual que `review`: `<archivo>:L<línea>: <problema>. <fix>.` Clasifica cada
hallazgo (bug, riesgo, nit, pregunta) — estas reglas producen sobre todo
hallazgos de tipo "riesgo" (defensividad/guards que ocultan bugs) y "nit"
(convenciones, simplificación), pero trátalas con la misma seriedad que
correctitud funcional cuando el patrón señalado ya causó — o puede causar —
una inconsistencia real de datos o de comportamiento (ver "una sola fuente de
verdad").
