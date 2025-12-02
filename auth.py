import bcrypt

USER_DATA_FILE: str = "users.txt"

def hash_password(plain_text_password: str) -> str:
    """
    Hashes a password using bcrypt with automatic salting.
    Returns the hashed password as a UTF-8 string.
    """
    password_bytes: bytes = plain_text_password.encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    hashed: bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored bcrypt hash.
    Returns True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(plain_text_password.encode("utf-8"), hashed_password.encode("utf-8"))

def user_exists(username: str) -> bool:
    try:
        with open(USER_DATA_FILE, "r") as f:
            return any(line.startswith(username + ",") for line in f)
    except FileNotFoundError:
        return False

def validate_username(username: str) -> tuple[bool, str]:
    if not (3 <= len(username) <= 20) or not username.isalnum():
        return False, "Username must be 3-20 alphanumeric characters."
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    if not (6 <= len(password) <= 50):
        return False, "Password must be 6-50 characters."
    return True, ""

def validate_role(role: str) -> tuple[bool, str]:
    allowed_roles = {"admin", "cyber", "data", "it"}
    if role.lower() not in allowed_roles:
        return False, "Role must be one of: admin, cyber, data, it."
    return True, ""

def register_user(username: str, password: str, role: str) -> bool:
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False
    hashed: str = hash_password(password)
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashed},{role.lower()}\n")
    print(f"Success: User '{username}' registered with role '{role}'.")
    return True

def login_user(username: str, password: str) -> bool:
    try:
        with open(USER_DATA_FILE, "r") as f:
            for line in f:
                stored_username, stored_hash, stored_role = line.strip().split(",")
                if stored_username == username:
                    if verify_password(password, stored_hash):
                        print(f"Success: Welcome, {username}! Your role is '{stored_role}'.")
                        return True
                    else:
                        print("Error: Invalid password.")
                        return False
        print("Error: Username not found.")
        return False
    except FileNotFoundError:
        print("Error: No users registered yet.")
        return False

def display_menu() -> None:
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n [1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main() -> None:
    print("\nWelcome to the Authentication System!")

    while True:
        display_menu()
        choice: str = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            print("\n--- USER REGISTRATION ---")
            username: str = input("Enter a username: ").strip()
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password: str = input("Enter a password: ").strip()
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password_confirm: str = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            role: str = input("Enter role (admin / cyber / data / it): ").strip().lower()
            is_valid, error_msg = validate_role(role)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            register_user(username, password, role)

        elif choice == '2':
            print("\n--- USER LOGIN ---")
            username: str = input("Enter your username: ").strip()
            password: str = input("Enter your password: ").strip()
            login_user(username, password)
            input("\nPress Enter to return to main menu...")

        elif choice == '3':
            print("\nThank you for using the authentication system.")
            break
        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()

