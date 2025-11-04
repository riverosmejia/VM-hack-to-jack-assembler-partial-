# --- codewriter.py ---

class CodeWriter:
    """
    Esta clase traduce los comandos de una máquina virtual (VM) 
    al lenguaje ensamblador Hack. 
    Se usa como parte del traductor VM -> ASM del proyecto Nand2Tetris.
    """
    
    def __init__(self, output_file):
        # Archivo de salida donde se escribirá el código ensamblador
        self.output_file = output_file
        # Nombre actual del archivo VM (sirve para manejar variables estáticas)
        self.vm_filename = "" 
        # Contador de etiquetas únicas (para saltos y comparaciones)
        self.label_counter = 0
        
        # Mapa de segmentos de memoria virtual a símbolos reales en Hack
        self.segment_map = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }

    def set_vm_filename(self, filename):
        """
        Define el nombre del archivo VM actual.
        Se usa para los símbolos estáticos (FileName.index)
        """
        self.vm_filename = filename

    # =======================================================
    #  COMANDOS: PUSH y POP
    # =======================================================
    
    def write_push_pop(self, command, segment, index):
        """
        Traduce un comando de tipo push o pop al código ASM correspondiente.
        Ej: push local 0, pop argument 2, etc.
        """

        asm_lines = []
        
        if command == "push":
            asm_lines = self._get_push_asm(segment, index)
        elif command == "pop":
            asm_lines = self._get_pop_asm(segment, index)
        
        # Escribe las líneas de ensamblador generadas en el archivo de salida
        for line in asm_lines:
            self.output_file.write(line + "\n")

    def _get_push_asm(self, segment, index):
        """
        Genera las instrucciones ASM para un comando PUSH.
        Obtiene un valor de un segmento y lo coloca en la pila.
        """
        
        # --- PUSH CONSTANTE ---
        if segment == "constant":
            # Carga el número directamente y lo empuja a la pila
            return [
                f"// push constant {index}",
                f"@{index}",   # A = index
                "D=A",         # D = index
                "@SP", "A=M",  # A apunta a la dirección actual de SP
                "M=D",         # *SP = D
                "@SP", "M=M+1" # SP++
            ]
        
        # --- PUSH DE SEGMENTOS BASADOS EN PUNTEROS (local, argument, this, that) ---
        elif segment in self.segment_map:
            symbol = self.segment_map[segment]
            return [
                f"// push {segment} {index}",
                f"@{index}", "D=A",      # D = index
                f"@{symbol}", "A=M+D",   # A = base(segmento) + index
                "D=M",                   # D = valor en esa dirección
                "@SP", "A=M", "M=D",     # *SP = D
                "@SP", "M=M+1"           # SP++
            ]
        
        # --- PUSH TEMP (RAM[5] a RAM[12]) ---
        elif segment == "temp":
            base = 5
            return [
                f"// push temp {index}",
                f"@{index}", "D=A", f"@{base}", "A=D+A", # Dirección = base + index
                "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"
            ]
        
        # --- PUSH POINTER (THIS o THAT directamente) ---
        elif segment == "pointer":
            symbol = "THIS" if index == "0" else "THAT"
            return [
                f"// push pointer {index}",
                f"@{symbol}", "D=M",
                "@SP", "A=M", "M=D", "@SP", "M=M+1"
            ]
        
        # --- PUSH STATIC (@FileName.index) ---
        elif segment == "static":
            symbol = f"{self.vm_filename}.{index}"
            return [
                f"// push static {index}",
                f"@{symbol}", "D=M",
                "@SP", "A=M", "M=D", "@SP", "M=M+1"
            ]
        return []

    def _get_pop_asm(self, segment, index):
        """
        Genera las instrucciones ASM para un comando POP.
        Extrae el valor del tope de la pila y lo guarda en el segmento indicado.
        """
        
        # --- POP DE SEGMENTOS BASADOS EN PUNTEROS ---
        if segment in self.segment_map:
            symbol = self.segment_map[segment]
            return [
                f"// pop {segment} {index}",
                f"@{index}", "D=A", f"@{symbol}", "D=M+D",  # D = dirección destino
                "@R13", "M=D",                              # Guarda dirección en R13
                "@SP", "M=M-1", "A=M", "D=M",               # D = *SP (valor a guardar)
                "@R13", "A=M", "M=D"                        # RAM[dest] = D
            ]
        
        # --- POP TEMP (RAM[5..12]) ---
        elif segment == "temp":
            base = 5
            return [
                f"// pop temp {index}",
                f"@{index}", "D=A", f"@{base}", "D=D+A",
                "@R13", "M=D", "@SP", "M=M-1", "A=M", "D=M",
                "@R13", "A=M", "M=D"
            ]

        # --- POP POINTER (THIS o THAT) ---
        elif segment == "pointer":
            symbol = "THIS" if index == "0" else "THAT"
            return [
                f"// pop pointer {index}",
                "@SP", "M=M-1", "A=M", "D=M",
                f"@{symbol}", "M=D"
            ]
        
        # --- POP STATIC (FileName.index) ---
        elif segment == "static":
            symbol = f"{self.vm_filename}.{index}"
            return [
                f"// pop static {index}",
                "@SP", "M=M-1", "A=M", "D=M",
                f"@{symbol}", "M=D"
            ]
        return []
    
    # =======================================================
    #  COMANDOS ARITMÉTICOS Y LÓGICOS
    # =======================================================

    def write_arithmetic(self, command):
        """
        Traduce comandos aritméticos/lógicos VM a ASM.
        Ej: add, sub, neg, eq, gt, lt, and, or, not
        """
        asm_lines = []
        
        # --- OPERACIONES BINARIAS (add, sub, and, or) ---
        if command in ["add", "sub", "and", "or"]:
            op = {"add": "M=D+M", "sub": "M=M-D", "and": "M=M&D", "or": "M=M|D"}[command]
            asm_lines = [
                f"// {command}",
                "@SP", "M=M-1", "A=M", "D=M",   # D = y (pop)
                "@SP", "M=M-1", "A=M", op,      # x = *SP, realiza x op y
                "@SP", "M=M+1"                  # SP++
            ]

        # --- OPERACIONES UNARIAS (neg, not) ---
        elif command in ["neg", "not"]:
            op = {"neg": "M=-M", "not": "M=!M"}[command]
            asm_lines = [
                f"// {command}",
                "@SP", "A=M-1", op              # Opera directamente sobre el tope de la pila
            ]
            
        # --- COMPARACIONES (eq, gt, lt) ---
        elif command in ["eq", "gt", "lt"]:
            label_id = self.label_counter
            self.label_counter += 1

            jump_symbol = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
            label_true = f"JUMP_TRUE_{label_id}"
            label_end = f"JUMP_END_{label_id}"

            asm_lines = [
                f"// {command}",
                "@SP", "M=M-1", "A=M", "D=M",   # D = y
                "@SP", "M=M-1", "A=M", "D=M-D", # D = x - y
                f"@{label_true}", f"D;{jump_symbol}", # Si cumple condición, salta
                "@SP", "A=M", "M=0",            # Falso (0)
                f"@{label_end}", "0;JMP",       # Salta al final
                f"({label_true})",
                "@SP", "A=M", "M=-1",           # Verdadero (-1)
                f"({label_end})",
                "@SP", "M=M+1"
            ]
            
        # Escribe las líneas generadas al archivo
        for line in asm_lines:
            self.output_file.write(line + "\n")

    # =======================================================
    #  COMANDOS DE CONTROL DE FLUJO
    # =======================================================

    def write_label(self, label):
        """Define una etiqueta (label) en ASM."""
        asm_lines = [
            f"// label {label}",
            f"({label})"
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")

    def write_goto(self, label):
        """Salta incondicionalmente a una etiqueta."""
        asm_lines = [
            f"// goto {label}",
            f"@{label}",
            "0;JMP"
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")

    def write_if(self, label):
        """Salta a una etiqueta si el valor en el tope de la pila es distinto de 0."""
        asm_lines = [
            f"// if-goto {label}",
            "@SP", "M=M-1",       # SP--
            "A=M", "D=M",         # D = *SP
            f"@{label}", "D;JNE"  # Si D != 0, salta
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")

    # =======================================================
    #  INICIALIZACIÓN DEL PROGRAMA (Bootstrap)
    # =======================================================

    def write_init(self):
        """
        Inicializa el puntero de pila o Stack Pointer(SP) en 256.
        Esta parte siempre se ejecuta primero en el programa Hack.
        """
        asm_lines = [
            "// Bootstrap: SP=256",
            "@256", "D=A", "@SP", "M=D"
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")
