import requests


def start_chat_session():
    print("Welcome to the chat bot!")

    auth_token = None
    while not auth_token:
        email = "admin@test1.com"  # input("Please enter your email: ")
        password = "12345678"  # input("Please enter your password: ")

        login_response = requests.post(
            "https://nigotis-be.vercel.app/api/v1/user/login",
            json={"email": email, "password": password},
        )

        if login_response.status_code == 200:
            auth_token = login_response.json()["data"]["token"]
            print("Login successful!")
        else:
            print("Login failed. Please try again.")

    headers = {"Authorization": f"Bearer {auth_token}"}

    product_response = requests.get(
        "https://nigotis-be.vercel.app/api/v1/product", headers=headers
    )
    client_response = requests.get(
        "https://nigotis-be.vercel.app/api/v1/client", headers=headers
    )
    invoice_response = requests.get(
        "https://nigotis-be.vercel.app/api/v1/client/invoice", headers=headers
    )

    print(product_response)
    print(client_response)
    print(invoice_response)

    if (
        product_response.status_code == 200
        and client_response.status_code == 200
        and invoice_response.status_code == 200
    ):
        products = product_response.json()
        clients = client_response.json()
        invoices = invoice_response.json()

        print("Data retrieved successfully.")
        print("Options:")
        print("1. View Products")
        print("2. View Clients")
        print("3. View Invoices")

        option = input("Please choose an option: ")
        if option == "1":
            print("Products:", products)
        elif option == "2":
            print("Clients:", clients)
        elif option == "3":
            print("Invoices:", invoices)
        else:
            print("Invalid option.")
    else:
        print("Failed to retrieve data.")


if __name__ == "__main__":
    start_chat_session()
