"""Las pruebas herméticas nunca dependen de una clave real: el cifrado exige CIFRADO_CLAVE y aquí se fija una de prueba.
Se fija al importar (no en un fixture) porque la composición crea la aplicación al importarse."""
import base64
import os

os.environ.setdefault("CIFRADO_CLAVE", base64.b64encode(b"clave-de-pruebas-de-32-bytes!!!!").decode())
