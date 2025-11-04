import sys
import os
from vm_parser import Parser    
from codewriter import CodeWriter 

def main():
    """
    Programa principal del traductor VM.
    """
    
    if len(sys.argv) != 2:
        print("Uso: python main.py <Test.vm>")
        sys.exit(1)

    input_path = sys.argv[1]
    
    base_filename = os.path.splitext(os.path.basename(input_path))[0]
    output_filename = input_path.replace(".vm", ".asm")
    
    print(f"Traduciendo {input_path} -> {output_filename}...")

    try:
        with open(input_path, "r") as input_file, \
             open(output_filename, "w") as output_file:
            
            parser = Parser(input_file)
            writer = CodeWriter(output_file)
            writer.write_init()
            writer.set_vm_filename(base_filename) # Para variables 'static'

            while parser.has_more_commands():
                parser.advance() 
                
                cmd_type = parser.command_type()
                
                if cmd_type == "C_PUSH" or cmd_type == "C_POP":
                    # Subgrupo A
                    command = parser.command_parts[0] 
                    segment = parser.arg1()
                    index = parser.arg2()
                    writer.write_push_pop(command, segment, index)
                
                elif cmd_type == "C_ARITHMETIC":
                    # Subgrupo B
                    command = parser.arg1()
                    writer.write_arithmetic(command)
                
                elif cmd_type == "C_LABEL":
                    # Subgrupo C
                    writer.write_label(parser.arg1())

                elif cmd_type == "C_GOTO":
                    # Subgrupo C
                    writer.write_goto(parser.arg1())
                    
                elif cmd_type == "C_IF":
                    # Subgrupo C
                    writer.write_if(parser.arg1())
                    
            print("Traducción completada.")

    except FileNotFoundError:
        print(f"Error: El archivo {input_path} no existe.")

if __name__ == "__main__":
    main()