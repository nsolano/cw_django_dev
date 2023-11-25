"""
Este script crea varios usuarios utilizando las credenciales 
proporcionadas en la lista CREDENTIALS.
Cada conjunto de credenciales consiste en un nombre de usuario, 
una contraseña y una dirección de correo electrónico.
Se utiliza la función create_user para crear cada usuario y se 
imprime un mensaje indicando que el usuario ha sido creado.
"""

from django.contrib.auth import get_user_model

CREDENTIALS = [
    ("usuario1", "password1", "usuario1@ejemplo.com"),
    ("usuario2", "password2", "usuario2@ejemplo.com"),
    ("usuario3", "password3", "usuario3@ejemplo.com"),
]

USER = get_user_model()


def create_user(username, password, email):
    """
    Crea un nuevo usuario con las credenciales proporcionadas.

    Parameters:
    - username (str): Nombre de usuario del nuevo usuario.
    - password (str): Contraseña del nuevo usuario.
    - email (str): Correo electrónico del nuevo usuario.
    """

    user = USER.objects.create_user(username=username,
                                    password=password, email=email)
    user.save()


for credential in CREDENTIALS:
    create_user(*credential)
    print(f"Created {credential}")
