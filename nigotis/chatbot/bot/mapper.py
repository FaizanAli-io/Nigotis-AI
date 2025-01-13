class Customer:
    def __init__(self, id, name, email, address, phone, products):
        self.id = id
        self.name = name
        self.email = email
        self.address = address
        self.phone = phone
        self.products = products

    def __str__(self):
        return f"{self.name}\n{'\n'.join(['\t' + str(product) for product in self.products])}"


class Product:
    def __init__(self, id, name, description, price, quantity):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

    def __str__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price}, quantity={self.quantity})"


class InvoiceMapper:
    @staticmethod
    def map_invoices_to_customers(invoices):
        customers = {}

        for invoice in invoices:
            client = invoice["clientId"]
            personal_info = client["personalInfo"]

            customer_id = client["_id"]
            if customer_id not in customers:
                customers[customer_id] = Customer(
                    id=customer_id,
                    name=f"{personal_info['title']} {personal_info['firstName']} {personal_info['lastName']}",
                    email=client["email"],
                    address=personal_info["address"],
                    phone=personal_info["phone"],
                    products=[],
                )

            for item in invoice["items"]:
                product = item["productId"]
                customers[customer_id].products.append(
                    Product(
                        id=product["_id"],
                        name=product["name"],
                        description=product["desc"],
                        price=product["price"],
                        quantity=item["quantity"],
                    )
                )

        return list(customers.values())
