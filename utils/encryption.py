"""
Module for data encryption and decryption.

Provides functions to generate encryption keys, load keys from the .env file,
and encrypt/decrypt data using Fernet symmetric encryption.
"""

import os
import logging
from cryptography.fernet import Fernet
from dotenv import load_dotenv

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)

logger = logging.getLogger(__name__)

ACTIVE_KEY_VAR_NAME = "ACTIVE_ENCRYPTION_KEY"
OLD_KEY_VAR_NAME = "OLD_ENCRYPTION_KEY"

_active_key_cache = None


def generate_encryption_key():
    """Generates a new encryption key and appends it to the .env file.

    Raises:
        RuntimeError: If an active encryption key already exists.
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


def load_encryption_key(version="Active"):
    """Loads the encryption key from the .env file.

    Args:
        version (str, optional): Which key version to load: "Active" or "Old".
                                 Defaults to "Active".

    Returns:
        bytes: The encryption key encoded in UTF-8.

    Raises:
        RuntimeError: If the requested key cannot be found.
        ValueError: If an invalid version is specified.
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
    """Encrypts a string using the active encryption key.

    Args:
        data (str): The plain text data to encrypt.

    Returns:
        str: The encrypted string.

    Raises:
        TypeError: If data is not a string.
    """
    if not isinstance(data, str):
        raise TypeError("Data must be a string")

    key = Fernet(load_encryption_key())
    encrypted = key.encrypt(data.encode("utf-8")).decode("utf-8")

    return encrypted


def decrypt_data(encrypted_data):
    """Decrypts an encrypted string using the active encryption key.

    Args:
        encrypted_data (str): The data to decrypt.

    Returns:
        str: The decrypted plain text.

    Raises:
        TypeError: If encrypted_data is not a string.
        Exception: If decryption fails.
    """

    if not isinstance(encrypted_data, str):
        raise TypeError("Encrypted data must be a string")

    key = Fernet(load_encryption_key())

    try:
        decrypted = key.decrypt(encrypted_data.encode("utf-8")).decode("utf-8")

        return decrypted
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise Exception("Decryption failed") from e
