# VM-hack-to-jack-assembler (partial)

## Qué es

Proyecto parcial en Python que convierte código VM (Hack VM) en código objetivo (salida preparada por el codewriter). Es una implementación parcial: parsea instrucciones VM y genera las traducciones básicas que están implementadas en codewriter.py. Ideal como base para completar un traductor VM → Jack/Hack-assembly según el libro/capítulos de Nand2Tetris.

## Qué hace (resumen)

Lee archivos .vm.

Parsea instrucciones VM (archivo: vm_parser.py).

Traduce las instrucciones soportadas a la salida objetivo mediante codewriter.py.

main.py orquesta la ejecución (lectura de entrada, llamada al parser y al codewriter, escritura de salida).

## Estado:

parcial — Traduce los comandos pop, push, add, sub, eq,label, goto, if-goto.

## Estructura del repo:

main.py — punto de entrada / CLI.

vm_parser.py — lector y analizador de instrucciones VM.

codewriter.py — generación del código de salida (ensamblador/Jack).

.gitignore

**pycache**/

## Requisitos:

Python 3.8+ (probado con 3.8/3.10).

No se usan paquetes externos (si requirements.txt aparece, instálalos con pip install -r requirements.txt).

## Cómo arrancar (paso a paso)

- Clona el repo:

  git clone https://github.com/riverosmejia/VM-hack-to-jack-assembler-partial-.git

  cd VM-hack-to-jack-assembler-partial-

- Verifica tu Python:

  ```bash
  python --version
  ```

  ó

  ```bash
  python3 --version
  ```

- Ejecuta el traductor (comando genérico — ajusta si main.py usa flags distintas):

-- Forma común: un archivo VM -> archivo de salida

    ```bash
    python main.py path/to/input.vm
    ```

-- si main soporta salida explícita:

    ```bash
    python main.py path/to/input.vm -o path/to/output.jack
    ```

## Tester.vm

Hay un archivo dentro del repositorio llamado "Tester.vm", este tiene la estructura del como puedes usar el programa
