from cryptography.fernet import Fernet
import os


def generate_encryption_key():
    """Generates a Fernet encryption key and writes it to a text file as a String"""

    key = Fernet.generate_key()
    with open(
        os.path.join(os.path.dirname(__file__), "encryption_key.txt"), "wb"
    ) as file:
        file.write(key)


def verify_login(user, password):
    pass


def encrypt_password(password):
    """Encrypts a password

    Args:
        password (String): Plaintext password

    Returns:
        String: Encrypted password
    """

    key = Fernet(get_key())

    return key.encrypt(bytes(password, encoding="utf8")).decode("utf8")


def decrypt_password(password):
    """Decrypts a password

    Args:
        password (String): Encrypted password to decrypt

    Returns:
        String: Decrypted password
    """

    key = Fernet(get_key())

    # Correctly encode to bytes before decryption
    if isinstance(password, str):
        password = password.encode("utf8")

    return key.decrypt(password).decode("utf8")


def get_key():
    """Returns the encryption key from a text file

    Returns:
        Bytes: Encryption key
    """

    with open(
        os.path.join(os.path.dirname(__file__), "encryption_key.txt"), "rb"
    ) as file:
        return file.read()
