from app.data.schema import init_schema

def main():
    print("🚀 Testing database schema creation...")

    try:
        init_schema()
        print(" SUCCESS: All tables were created without errors!")

    except Exception as e:
        print("❌ ERROR: Something went wrong while creating tables.")
        print(f"Details: {e}")

if __name__ == "__main__":
    main()
