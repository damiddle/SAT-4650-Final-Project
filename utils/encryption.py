from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)

ACTIVE_KEY_VAR_NAME = "ACTIVE_ENCRYPTION_KEY"
OLD_KEY_VAR_NAME = "OLD_ENCRYPTION_KEY"

_active_key_cache = None


def generate_encryption_key():
    """Generates an encryption key and stores it into the .env file for use

    Raises:
        RuntimeError: Key already exists in active key variable
    """
    key = Fernet.generate_key().decode("utf-8")
    env_lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as file:
            env_lines = file.readlines()
    for line in env_lines:
        if line.startswith(ACTIVE_KEY_VAR_NAME):
            raise RuntimeError(
                "Encryption key already exists. Delete or update the .env file manually."
            )
    with open(ENV_FILE_PATH, "a") as file:
        file.write(f"\n{ACTIVE_KEY_VAR_NAME} = '{key}'\n")
    print("Encryption key generated and stored in .env file.")


def load_encryption_key(version="Active"):
    """Loads the encryption key from the .env file

    Args:
        version (str, optional): Active key or old key. Defaults to "Active".

    Raises:
        RuntimeError: There is no encryption key present

    Returns:
        bytes: Encryption key
    """
    global _active_key_cache

    if version == "Active":
        if _active_key_cache is not None:
            return _active_key_cache
        key = os.getenv(ACTIVE_KEY_VAR_NAME)
        if not key:
            raise RuntimeError(
                "Encryption key not found in .env file. Generate it first."
            )
        _active_key_cache = key.encode("utf-8")
        return _active_key_cache
    elif version == "Old":
        key = os.getenv(OLD_KEY_VAR_NAME)
        if not key:
            raise RuntimeError("Old encryption key not found in .env file.")
        return key.encode("utf-8")
    else:
        raise ValueError("Invalid key version specified. Use 'Active' or 'Old'.")


def encrypt_data(data):
    """Encrypts data with encryption key

    Args:
        data (str): Data to encrypt

    Raises:
        TypeError: Data is not a string

    Returns:
        str: Encrypted data
    """
    if not isinstance(data, str):
        raise TypeError("Data must be a string")
    key = Fernet(load_encryption_key())
    encrypted = key.encrypt(data.encode("utf-8")).decode("utf-8")
    return encrypted


def decrypt_data(encrypted_data):
    """Decrypts given data

    Args:
        encrypted_data (str): Encrypted data

    Raises:
        TypeError: Data is not a string

    Returns:
        str: Decrypted string
    """
    if not isinstance(encrypted_data, str):
        raise TypeError("Encrypted data must be a string")
    key = Fernet(load_encryption_key())
    try:
        decrypted = key.decrypt(encrypted_data.encode("utf-8")).decode("utf-8")
        return decrypted
    except Exception as e:
        print(f"Decryption failed: {e}")
        raise Exception("Decryption failed") from e
