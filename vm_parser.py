# --- vm_parser.py ---

class Parser:
    """
    Lee un archivo .vm, elimina comentarios/espacios y proporciona
    acceso a los componentes del comando.
    """
    
    def __init__(self, input_file):
        """
        Abre el archivo de entrada .vm y se prepara para analizarlo.
        
        Args:
            input_file: Un objeto de archivo abierto (en modo 'r').
        """
        self.lines = input_file.readlines() 
        self.current_line_index = -1
        self.current_command = ""
        self.command_parts = []
        
        self.arithmetic_commands = [
            "add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"
        ]

    def has_more_commands(self):
        """
        Verifica si hay más comandos en la entrada.
        """
        for i in range(self.current_line_index + 1, len(self.lines)):
            line = self._clean_line(self.lines[i])
            if line:
                return True
        return False

    def advance(self):
        """
        Lee el siguiente comando de la entrada y lo convierte
        en el "comando actual".
        """
        self.current_line_index += 1
        line = self._clean_line(self.lines[self.current_line_index])
        
        # Sigue avanzando si la línea está vacía
        while not line and self.current_line_index < len(self.lines) - 1:
            self.current_line_index += 1
            line = self._clean_line(self.lines[self.current_line_index])
                
        self.current_command = line
        self.command_parts = self.current_command.split()

    def _clean_line(self, line):
        """
        Elimina comentarios y espacios en blanco de una línea.
        """
        line = line.strip()
        if "//" in line:
            line = line[:line.find("//")].strip()
        return line

    def command_type(self):
        """
        Devuelve el tipo del comando VM actual.
        (C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF)
        """
        if not self.command_parts: return None
        
        cmd = self.command_parts[0]
        
        if cmd in self.arithmetic_commands:
            return "C_ARITHMETIC"
        if cmd == "push":
            return "C_PUSH"
        if cmd == "pop":
            return "C_POP"
        if cmd == "label":
            return "C_LABEL"
        if cmd == "goto":
            return "C_GOTO"
        if cmd == "if-goto":
            return "C_IF"
        # Faltan C_FUNCTION, C_RETURN, C_CALL
        
        return "C_UNKNOWN"

    def arg1(self):
        """
        Devuelve el primer argumento del comando actual.
        """
        if self.command_type() == "C_ARITHMETIC":
            return self.command_parts[0]
        else:
            return self.command_parts[1]

    def arg2(self):
        """
        Devuelve el segundo argumento del comando actual.
        """
        return self.command_parts[2]