class AFDMatricula:
    def __init__(self):
        # Estados del autómata
        self.estados = {
            'q0': 'inicio',
            'q1': 'primer_digito_año',
            'q2': 'segundo_digito_año',
            'q3': 'tercer_digito_año',
            'q4': 'cuarto_digito_año',
            'q5': 'primer_guion',
            'q6': 'primera_letra_tipo',
            'q7': 'segunda_letra_tipo',
            'q8': 'segundo_guion',
            'q9': 'primer_digito_codigo',
            'q10': 'segundo_digito_codigo',
            'q11': 'tercer_digito_codigo',
            'q12': 'cuarto_digito_codigo',
            'qf': 'aceptacion'
        }
        
        self.estado_actual = 'q0'
        self.caracter_actual = 0
        
    def es_digito(self, char):
        return char.isdigit()
        
    def es_letra(self, char):
        return char.isalpha() and char.isupper()
        
    def procesar_caracter(self, char):
        if self.estado_actual == 'q0' and self.es_digito(char):
            self.estado_actual = 'q1'
        elif self.estado_actual == 'q1' and self.es_digito(char):
            self.estado_actual = 'q2'
        elif self.estado_actual == 'q2' and self.es_digito(char):
            self.estado_actual = 'q3'
        elif self.estado_actual == 'q3' and self.es_digito(char):
            self.estado_actual = 'q4'
        elif self.estado_actual == 'q4' and char == '-':
            self.estado_actual = 'q5'
        elif self.estado_actual == 'q5' and self.es_letra(char):
            self.estado_actual = 'q6'
        elif self.estado_actual == 'q6' and self.es_letra(char):
            self.estado_actual = 'q7'
        elif self.estado_actual == 'q7' and char == '-':
            self.estado_actual = 'q8'
        elif self.estado_actual == 'q8' and self.es_digito(char):
            self.estado_actual = 'q9'
        elif self.estado_actual == 'q9' and self.es_digito(char):
            self.estado_actual = 'q10'
        elif self.estado_actual == 'q10' and self.es_digito(char):
            self.estado_actual = 'q11'
        elif self.estado_actual == 'q11' and self.es_digito(char):
            self.estado_actual = 'qf'
        else:
            return False
        return True
        
    def validar_cadena(self, cadena):
        self.estado_actual = 'q0'
        self.caracter_actual = 0
        
        for i, char in enumerate(cadena):
            self.caracter_actual = i
            if not self.procesar_caracter(char):
                return False, i, f"Carácter inválido: {char}"
                
        return self.estado_actual == 'qf', self.caracter_actual, "La cadena no está completa"
        
    def validar_archivo(self, ruta_archivo):
        resultados = []
        try:
            with open(ruta_archivo, 'r') as f:
                for i, linea in enumerate(f, 1):
                    linea = linea.strip()
                    es_valida, pos_error, mensaje = self.validar_cadena(linea)
                    if not es_valida:
                        resultados.append(f"Error en línea {i}, posición {pos_error + 1}: {mensaje}")
                    else:
                        resultados.append(f"Línea {i}: Matrícula válida")
            return resultados
        except FileNotFoundError:
            return ["Error: No se encontró el archivo"]
        except Exception as e:
            return [f"Error al procesar el archivo: {str(e)}"] 