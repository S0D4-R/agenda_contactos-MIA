import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> None:
    try:
        from ui.app import App
    except ImportError as e:
        print(f"Error al importar módulos: {e}")
        print("Asegúrate de instalar las dependencias: pip install fpdf2")
        sys.exit(1)

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
