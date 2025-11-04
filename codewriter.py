# --- codewriter.py ---

class CodeWriter:
    """
    Traduce comandos VM a código ensamblador Hack.
    """
    
    def __init__(self, output_file):
        self.output_file = output_file
        self.vm_filename = "" 
        self.label_counter = 0 # Para etiquetas únicas de comparaciones
        
        # Mapeo de segmentos a sus símbolos base
        self.segment_map = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }

    def set_vm_filename(self, filename):
        self.vm_filename = filename

    # =======================================================
    # Subgrupo A: PUSH y POP
    # =======================================================
    
    def write_push_pop(self, command, segment, index):

        asm_lines = []
        
        if command == "push":
            asm_lines = self._get_push_asm(segment, index)
        elif command == "pop":
            asm_lines = self._get_pop_asm(segment, index)
        
        for line in asm_lines:
            self.output_file.write(line + "\n")

    def _get_push_asm(self, segment, index):
        # Implementación de PUSH (constant, local, argument, this, that, temp, pointer, static)
        
        if segment == "constant":
            # 
            return [
                f"// push constant {index}",
                f"@{index}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"
            ]
        
        elif segment in self.segment_map:
            symbol = self.segment_map[segment] 
            # 
            return [
                f"// push {segment} {index}",
                f"@{index}", "D=A", f"@{symbol}", "A=M", "D=D+A", # D = addr
                "A=D", "D=M", # D = RAM[addr]
                "@SP", "A=M", "M=D", # *SP = D
                "@SP", "M=M+1"
            ]
        
        # Temp (RAM[5] a RAM[12]) y Pointer (RAM[3]=THIS, RAM[4]=THAT)
        elif segment == "temp":
            base = 5
            return [
                f"// push temp {index}",
                f"@{index}", "D=A", f"@{base}", "D=D+A",
                "A=D", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"
            ]
        elif segment == "pointer":
            symbol = "THIS" if index == "0" else "THAT"
            return [
                f"// push pointer {index}",
                f"@{symbol}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"
            ]
        
        # Static (@FileName.i)
        elif segment == "static":
            symbol = f"{self.vm_filename}.{index}"
            return [
                f"// push static {index}",
                f"@{symbol}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"
            ]
        return []

    def _get_pop_asm(self, segment, index):
        # Implementación de POP
        
        # Pop a segmentos basados en puntero (local, argument, this, that)
        if segment in self.segment_map:
            symbol = self.segment_map[segment] 
            # 
            return [
                f"// pop {segment} {index}",
                f"@{index}", "D=A", f"@{symbol}", "A=M", "D=D+A", # D = addr
                "@R13", "M=D", # R13 = addr (Guardar la dirección de destino)
                "@SP", "M=M-1", # SP--
                "A=M", "D=M", # D = *SP (Valor a guardar)
                "@R13", "A=M", "M=D" # RAM[addr] = D
            ]
        
        # Pop a segmentos Temp, Pointer y Static (más directos)
        elif segment == "temp":
            base = 5
            return [
                f"// pop temp {index}",
                f"@{index}", "D=A", f"@{base}", "D=D+A",
                "@R13", "M=D", "@SP", "M=M-1", 
                "A=M", "D=M", "@R13", "A=M", "M=D"
            ]
        elif segment == "pointer":
            symbol = "THIS" if index == "0" else "THAT"
            return [
                f"// pop pointer {index}",
                "@SP", "M=M-1", "A=M", "D=M", f"@{symbol}", "M=D"
            ]
        elif segment == "static":
            symbol = f"{self.vm_filename}.{index}"
            return [
                f"// pop static {index}",
                "@SP", "M=M-1", "A=M", "D=M", f"@{symbol}", "M=D"
            ]
        return []
    
    # =======================================================
    # Subgrupo B: Aritmética
    # =======================================================

    def write_arithmetic(self, command):
        asm_lines = []
        
        # Comandos binarios (add, sub, and, or)
        if command in ["add", "sub", "and", "or"]:
            op = {"add": "M=M+D", "sub": "M=M-D", "and": "M=M&D", "or": "M=M|D"}[command]
            # 
            asm_lines = [
                f"// {command}",
                "@SP", "M=M-1", "A=M", "D=M", # Pop 'y' (D=y)
                "@SP", "M=M-1", "A=M", op,    # Pop 'x', calcula x op y
                "@SP", "M=M+1" # Push resultado
            ]

        # Comandos unarios (neg, not)
        elif command in ["neg", "not"]:
            op = {"neg": "M=-M", "not": "M=!M"}[command]
            asm_lines = [
                f"// {command}",
                "@SP", "A=M-1", op # Operación in-place en la cima de la pila
            ]
            
        # Comandos de comparación (eq, gt, lt)
        elif command in ["eq", "gt", "lt"]:
            label_id = self.label_counter
            self.label_counter += 1
            jump_symbol = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
            label_true = f"JUMP_TRUE_{label_id}"
            label_end = f"JUMP_END_{label_id}"
            # 
            asm_lines = [
                f"// {command}",
                "@SP", "M=M-1", "A=M", "D=M", # D = y
                "@SP", "M=M-1", "A=M", "D=M-D", # D = x - y
                f"@{label_true}", f"D;{jump_symbol}",
                "@SP", "A=M", "M=0", # Falso (0)
                f"@{label_end}", "0;JMP",
                f"({label_true})",
                "@SP", "A=M", "M=-1", # Verdadero (-1)
                f"({label_end})",
                "@SP", "M=M+1"
            ]
            
        for line in asm_lines:
            self.output_file.write(line + "\n")

    # =======================================================
    # Subgrupo C: Control de Flujo
    # =======================================================

    def write_label(self, label):
        asm_lines = [
            f"// label {label}",
            f"({label})"
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")

    def write_goto(self, label):
        asm_lines = [
            f"// goto {label}",
            f"@{label}",
            "0;JMP"
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")

    def write_if(self, label):
        asm_lines = [
            f"// if-goto {label}",
            "@SP", "M=M-1", # Pop
            "A=M", "D=M", # D = valor
            f"@{label}",
            "D;JNE" # Saltar si D != 0
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")

    def write_init(self):
        """
        Inicializa el puntero de pila (SP) en 256.
        """
        asm_lines = [
            "// Bootstrap: SP=256",
            "@256",
            "D=A",
            "@SP",
            "M=D"
        ]
        for line in asm_lines:
            self.output_file.write(line + "\n")
