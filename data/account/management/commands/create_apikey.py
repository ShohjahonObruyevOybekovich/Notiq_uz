from django.core.management.base import BaseCommand
from data.account.models import Customer, ApiKey


class Command(BaseCommand):
    help = "Create a customer and API key (or add a key for existing customer)."


    def add_arguments(self, parser):
        parser.add_argument("name", help="Customer name")
        parser.add_argument("--email", default="")


    def handle(self, *args, **opts):
        cust, _ = Customer.objects.get_or_create(name=opts["name"], defaults={"email": opts["email"]})
        key = ApiKey.objects.create(customer=cust)
        self.stdout.write(self.style.SUCCESS(f"Customer: {cust.id} {cust.name}"))
        self.stdout.write(self.style.SUCCESS(f"API Key: {key.key}"))