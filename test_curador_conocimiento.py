from agents.curador_conocimiento import CuradorConocimiento


texto = """
Programacion I

Variables
Tipos de datos
Condicionales
Bucles
Funciones
Archivos
"""

curador = CuradorConocimiento()
resultado = curador.ejecutar(texto)

print(resultado)
