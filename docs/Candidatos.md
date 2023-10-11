## Selección de Candidatos

Se evalúan las firmas de las funciones sobrecargadas y se asignan puntajes en base a la coincidencia de los argumentos provistos frente a los parámetros esperados.


Se itera sobre todas las sobrecargas registradas en `self.sobrecargas`, donde cada sobrecarga está representada por una firma y su función correspondiente.

### 1. Puntaje de Longitud

- Se evalúa la coincidencia en la longitud de argumentos entre la firma de la función y los argumentos proporcionados.
  - Si la firma de la función no tiene parámetros o no se proporcionaron argumentos;, y, si la cantidad de parámetros de la firma no coincide con la suma de argumentos posicionales y nominales; se ignora la firma y se pasa a la siguiente. 
  - Si la cantidad de argumentos posicionales y nominales coincide exactamente con la cantidad de parámetros de la firma y la firma no tiene parámetros variables ni argumentos por defecto, se asigna un puntaje alto de `3`. *Esto indica que la firma es una coincidencia perfecta en términos de longitud de argumentos.*
  - Si la cantidad de argumentos posicionales y nominales coincide exactamente con la cantidad de parámetros de la firma, pero la firma tiene argumentos por defecto o parámetros variables, se asigna un puntaje moderado de `2`.
  - Si la cantidad de argumentos proporcionados es igual o menor a la cantidad de parámetros de la firma, y la firma tiene argumentos por defecto o parámetros variables, se asigna un puntaje de `1`. *Esto indica una coincidencia parcial en términos de longitud de argumentos.*
  - En cualquier otro caso, se ignora la firma y se pasa a la siguiente.

### 2. Puntaje de firma

- Se evalúa la coincidencia de tipos en función de la firma de la función y los tipos de los argumentos proporcionados.
  - Se utiliza la función `validarFirma` para determinar si los tipos de los argumentos coinciden con los tipos esperados por la firma de la función.
  - Se asigna un puntaje basado en la coincidencia de tipos. Si la validación de la firma tiene éxito, se obtiene un puntaje positivo en función de la adecuación de tipos.
  - Si la validación de la firma no tiene éxito (es decir, retorna `False`), se ignora la sobrecarga y se pasa a la siguiente.

### 3. Construcción de la Lista de Candidatos

- Para cada sobrecarga válida, se crea un objeto `Candidato`, que almacena la función sobrecargada, la firma correspondiente y el puntaje calculado. Prima el puntaje de tipado por sobre el de longitud.
- Los candidatos se agregan a la lista `candidatos`.

### 4. Selección del Mejor Candidato

- Se verifica si hay candidatos en la lista. Si no hay candidatos válidos, se genera una excepción de tipo `TypeError`.
- Si hay varios candidatos, se ordenan en función de sus puntajes, priorizando los puntajes más altos. El candidato con el puntaje más alto se selecciona como la mejor función sobrecargada.

### 5. Resultado
- Se llama al candidato preferido con los argumentos proporcionados, y su resultado se retorna.

