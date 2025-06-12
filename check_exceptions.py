from model import session, ExceptionLog

def print_exceptions():
    exceptions = session.query(ExceptionLog).all()

    if not exceptions:
        print("No exceptions found in the database.")
        return

    print("=== Registered Exceptions ===")
    for e in exceptions:
        print(f"[{e.timestamp}] User: {e.user_id} | Type: {e.exception_type} | Level: {e.exception_level}")
        print(f"→ Details: {e.details}")
        print("-" * 50)

# Run the function
if __name__ == "__main__":
    print_exceptions()
