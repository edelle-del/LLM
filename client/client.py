import requests


def main() -> None:
    print("Simple LLM Microservices Client")
    print("This will call the Python gateway, which calls the Java LLM service.\n")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    url = "http://localhost:8000/api/generate"
    while True:
        prompt = input("Enter a prompt: ").strip()
        if not prompt:
            print("Please enter a prompt (or type 'exit' to quit).")
            continue

        if prompt.lower() in {"exit", "quit"}:
            print("Ending conversation.")
            break

        try:
            response = requests.post(url, json={"prompt": prompt}, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"Error calling API at {url}: {exc}")
            continue

        try:
            data = response.json()
        except ValueError:
            print("API did not return valid JSON.")
            print("Raw response:", response.text)
            continue

        result = data.get("result")
        if result is None:
            print("API response did not contain a 'result' field.")
            print("Full JSON:", data)
            continue

        print("\n=== LLM Response ===")
        print(result)
        print()


if __name__ == "__main__":
    main()

