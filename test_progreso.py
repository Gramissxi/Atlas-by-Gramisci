from services.progreso_usuario import (
    actualizar_progreso,
    obtener_progreso
)

actualizar_progreso(
    tema_actual="SQL avanzado",
    paso_actual=1,
    avance_porcentaje=10
)

print(
    obtener_progreso()
)