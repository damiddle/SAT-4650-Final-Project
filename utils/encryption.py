from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

ENV_FILE_PATH = ".env"
ACTIVE_KEY_VAR_NAME = "ACTIVE_ENCRYPTION_KEY"
OLD_KEY_VAR_NAME = "OLD_ENCRYPTION_KEY"


def generate_encryption_key():
    """Generates a Fernet encryption key and stores it in the .env file."""
    key = Fernet.generate_key().decode("utf-8")  # Convert from bytes to string

    # Load existing .env content
    env_lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r") as file:
            env_lines = file.readlines()

    # Check if key already exists
    for line in env_lines:
        if line.startswith(ACTIVE_KEY_VAR_NAME):
            raise RuntimeError(
                "Encryption key already exists. Delete or update the .env file manually."
            )

    # Append new key if not found
    with open(ENV_FILE_PATH, "a") as file:
        file.write(f"\n{ACTIVE_KEY_VAR_NAME} = '{key}'\n")

    print("Encryption key generated and stored in .env file.")


def load_encryption_key(version="Active"):
    """Loads the encryption key from environment variables."""
    if version == "Active":
        key = os.getenv(ACTIVE_KEY_VAR_NAME)

    elif version == "Old":
        key = os.getenv(OLD_KEY_VAR_NAME)

    if not key:
        raise RuntimeError("Encryption key not found in .env file. Generate it first.")

    return key.encode("utf-8")  # Convert string back to bytes


def encrypt_data(data):
    """Encrypts a string using the encryption key."""
    if not isinstance(data, str):
        raise TypeError("Data must be a string")

    key = Fernet(load_encryption_key())
    return key.encrypt(data.encode("utf-8")).decode("utf-8")


def decrypt_data(encrypted_data):
    """Decrypts a previously encrypted string."""
    if not isinstance(encrypted_data, str):
        raise TypeError("Encrypted data must be a string")

    key = Fernet(load_encryption_key())

    try:
        return key.decrypt(encrypted_data.encode("utf-8")).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")
