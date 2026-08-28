---
name: django-review
description: >-
  Convenciones de code review para proyectos Django/DRF — manejo de
  excepciones por defecto de DRF, patrones de ORM (filtros, select_related/
  only), restricciones de base de datos, nulabilidad de campos, imports, y
  tests que prueban configuración de admin en vez de lógica propia. Los
  nombres de modelos/servicios en los ejemplos están generalizados para
  aplicar a cualquier proyecto Django, no a un repo puntual. Complementa
  `cosmoscalibur-review` (estilo personal, independiente de stack) — corre
  esta pasada después de esa cuando el repo sea Django/DRF.
---

# Code Review — convenciones Django/DRF

Estas reglas nacieron de revisiones reales sobre backends Django/DRF en
producción. Úsalas **después** de `review` y `cosmoscalibur-review` — esta es
la capa de convenciones específicas del framework/ORM, no un reemplazo de las
pasadas de corrección/rendimiento/adversarial ni del criterio general de
estilo.

## Reglas

- **Antes de aceptar manejo de excepciones manual en una vista DRF, verifica
  qué hace el manejador por defecto.** Si el proyecto no tiene
  `EXCEPTION_HANDLER` custom en `REST_FRAMEWORK` (settings), cualquier
  `rest_framework.exceptions.ValidationError`/`ParseError`/etc. no atrapada
  ya se convierte sola en la respuesta 4xx correcta con `.detail` como body.
  Un `try/except ValidationError: return Response(error.detail, status=400)`
  agregado "para que el contrato se lea en el endpoint" no cambia nada
  observable — es código muerto que reimplementa gratis lo que DRF ya hace.
  Antes de aprobar manejo de excepciones nuevo en una vista, confirma que
  produce algo distinto de lo que pasaría sin él.

- **Pasa lo que se usa, no el objeto completo — también en filtros de ORM.**
  Ver la regla equivalente en `cosmoscalibur-review` para firmas de función;
  el mismo patrón aparece disfrazado en un `Model.objects.filter(fk=objeto_completo)`
  / `get_object_or_404(Model, fk=objeto_completo)`: Django acepta la
  instancia completa como comodidad, pero eso no cambia que el filtro solo
  necesita el id — usa `fk_id=objeto.id` explícito. No lo trates como un
  caso aparte solo porque el objeto ya lo tenías en memoria (p. ej.
  `request.user`): pasar el objeto completo cuando el `id` basta es el mismo
  acoplamiento innecesario, tenga la forma de un parámetro de función o de
  un kwarg de `.filter()`/`get_object_or_404()`. A veces también esconde una
  consulta de más (carga diferida de campos que el caller nunca
  seleccionó).

- **Sin consultas redundantes cuando el caller ya tiene el dato.** Ver la
  regla equivalente en `cosmoscalibur-review`; en Django esto se ve como un
  método interno que "re-consulta por aislamiento" un registro relacionado
  que el caller ya cargó (p. ej. volver a traer un objeto padre dentro de un
  servicio). Antes de aceptarlo, evalúa si el caller puede simplemente
  ampliar su propio `.only()`/`select_related()`/`prefetch_related()` para
  incluir los campos/relaciones que hacen falta, en vez de pagar una query
  extra por "aislamiento entre capas".

- **Una restricción de DB que el motor de producción no aplica es código
  muerto, no documentación de intención.** Si una constraint de Django
  (`UniqueConstraint` condicional, `CheckConstraint`, etc.) depende de una
  capacidad que el motor de base de datos del proyecto no soporta (p. ej.
  MySQL sin soporte para el tipo de check declarado), señálalo así
  explícitamente — no es suficiente dejarla declarada "por si se migra a
  Postgres" o como documentación; en la práctica no protege nada en runtime
  y puede dar falsa confianza a quien lee el modelo.

- **Consistencia de imports dentro de un archivo nuevo.** Mezclar imports
  absolutos y relativos en el mismo archivo nuevo es desorden introducido,
  no legacy heredado (el relativo es remanente de Python 2; el absoluto es
  el estándar actual). La única razón legítima para uno relativo es evitar
  un import circular real — verifícalo antes de aceptarlo.

- **Tests que protegen configuración, no lógica.** Un test sobre
  `list_display`/`Meta` del admin de Django sin reglas propias detrás
  (ningún `get_queryset`/`save_model` custom que el test ejercite) prueba
  que el framework funciona, no tu código.

- **Convención de nulabilidad según el tipo de campo.** Campos numéricos:
  `null=True`; campos de texto: `blank=True`, evitando `null=True` (dos
  estados para "vacío" — cadena vacía y `NULL` — es la inconsistencia que
  esta convención evita).

## Casos concretos

Ilustraciones de reglas generales de `cosmoscalibur-review`, tal como se
observaron en un backend Django/DRF real (nombres de modelos/servicios
generalizados):

- **Defensividad injustificada, versión DRF.** Un `try/except DatabaseError`
  alrededor de un side-effect que nunca ha fallado en producción, o un
  `int(request.data[...])` casteado a `ParseError` "por si acaso" sin
  evidencia de que el frontend (que consumes end-to-end) vaya a mandar algo
  distinto — ver la regla de defensividad en `cosmoscalibur-review`. Caso
  real del caveat "¿esto revienta solo o no?": al resolver dos preguntas
  legítimas sobre defensividad excesiva en un endpoint, se borró junto con
  ellas la única validación de rango de un año fiscal de negocio — sin
  reemplazo, sin que nada más fallara en su lugar — reintroduciendo el bug
  de persistir un registro para un periodo fiscal inexistente que el propio
  autor del código había prevenido explícitamente antes. Un año fuera de
  rango sigue siendo un entero válido para la columna: nada revienta solo.

- **Arquitectura primero, versión DRF.** Antes de aceptar una interfaz de
  administración o un endpoint nuevo, pregunta si otra ya resuelve el caso
  de uso. Antes de aceptar un mixin no visto en el repo o un
  `http_method_names` explícito como idiom razonable, corre `ast-grep`/`grep`
  para confirmar que es genuinamente inédito.

- **Rename sin auditar call sites, versión Django.** Un rename de servicio
  con cambio de firma (de recibir la instancia de usuario a recibir solo su
  `id`) actualizó la clase y la mayoría de sus llamadas, pero dejó una
  pasando `self.request.user` (el objeto) en vez de `.id` dentro de una
  función anidada — los tests unitarios no lo atraparon porque llaman al
  método directo con el tipo correcto, y nadie lo vio hasta una segunda
  pasada de revisión manual. Ver la regla de auditoría de call sites con LSP
  en `cosmoscalibur-review`.

- **Justificación de negocio inventada, versión ORM.** Un `on_delete=PROTECT`
  contra el borrado duro de un usuario que en la práctica no ocurre, cuando
  el modelo de usuario ya tiene su propio soft-delete vía un flag
  `is_active` — ver la regla de sospecha de justificación inventada en
  `cosmoscalibur-review`.

- **Documentación como ruido, versión Django.** `help_text` es significado
  de negocio, no formato ni la regla que ya lo gobierna (eso vive en el
  validador/serializer). Explicar en una vista la lógica de permisos que
  vive en la clase de permisos es la misma falla de capa mal ubicada — ver
  la regla de documentación-como-ruido en `cosmoscalibur-review`.

## Formato

Igual que `review`: `<archivo>:L<línea>: <problema>. <fix>.` Clasifica cada
hallazgo (bug, riesgo, nit, pregunta).
