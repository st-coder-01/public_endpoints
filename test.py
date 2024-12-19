import subprocess
import json
import argparse
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from tabulate import tabulate  # Ensure this library is installed: pip install tabulate

# Fetch storage account details
def fetch_storage_account_status(subscription_id):
    try:
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        result = subprocess.run(
            ["az", "storage", "account", "list", "--query", "[].{name:name,resourceGroup:resourceGroup}", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        storage_accounts = json.loads(result.stdout)

        report = []
        for account in storage_accounts:
            name = account["name"]
            resource_group = account["resourceGroup"]

            net_result = subprocess.run(
                ["az", "storage", "account", "show", "--name", name, "--resource-group", resource_group, "-o", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            account_details = json.loads(net_result.stdout)
            public_access = account_details.get("networkRuleSet", {}).get("defaultAction", "Unknown")

            report.append({"name": name, "resource_group": resource_group, "public_access": public_access})

        return report

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return []

# Fetch key vault details
def fetch_key_vault_status(subscription_id):
    try:
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        result = subprocess.run(
            ["az", "keyvault", "list", "--query", "[].{name:name,resourceGroup:resourceGroup}", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        key_vaults = json.loads(result.stdout)

        report = []
        for vault in key_vaults:
            name = vault["name"]
            resource_group = vault["resourceGroup"]

            net_result = subprocess.run(
                ["az", "keyvault", "show", "--name", name, "--resource-group", resource_group, "-o", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            vault_details = json.loads(net_result.stdout)
            properties = vault_details.get("properties", {})
            public_access = properties.get("publicNetworkAccess", "Unknown")

            report.append({"name": name, "resource_group": resource_group, "public_access": public_access})

        return report

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return []

# Fetch function app details
def fetch_function_app_status(subscription_id):
    try:
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        result = subprocess.run(
            ["az", "functionapp", "list", "--query", "[].{name:name,resourceGroup:resourceGroup}", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        function_apps = json.loads(result.stdout)

        report = []
        for app in function_apps:
            name = app["name"]
            resource_group = app["resourceGroup"]

            net_result = subprocess.run(
                ["az", "functionapp", "show", "--name", name, "--resource-group", resource_group, "-o", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            app_details = json.loads(net_result.stdout)
            public_access = app_details.get("publicNetworkAccess", "Unknown")

            report.append({"name": name, "resource_group": resource_group, "public_access": public_access})

        return report

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return []

# Fetch Redis cache details
def fetch_redis_status(subscription_id):
    try:
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        result = subprocess.run(
            ["az", "redis", "list", "--query", "[].{name:name,resourceGroup:resourceGroup}", "-o", "json"],
            capture_output=True,
            text=True,
            check=True
        )
        redis_caches = json.loads(result.stdout)

        report = []
        for cache in redis_caches:
            name = cache["name"]
            resource_group = cache["resourceGroup"]

            net_result = subprocess.run(
                ["az", "redis", "show", "--name", name, "--resource-group", resource_group, "-o", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            cache_details = json.loads(net_result.stdout)
            enable_non_ssl_port = cache_details.get("enableNonSslPort", "Unknown")

            report.append({"name": name, "resource_group": resource_group, "enable_non_ssl_port": enable_non_ssl_port})

        return report

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return []

# Generate the report content with properly aligned tables
def generate_report_content(storage_report, key_vault_report, function_app_report, redis_report):
    def create_html_table(rows, headers):
        # Start table with headers
        html = "<table border='1' style='border-collapse: collapse; text-align: left;'>"
        html += "<tr>" + "".join(f"<th style='padding: 8px;'>{header}</th>" for header in headers) + "</tr>"
        # Add rows
        for row in rows:
            html += "<tr>" + "".join(f"<td style='padding: 8px;'>{cell}</td>" for cell in row) + "</tr>"
        html += "</table>"
        return html

    report_html = "<h2>Azure Report Summary</h2>"

    # Storage Account Report
    if storage_report:
        storage_table = [[entry["name"], entry["resource_group"], entry["public_access"]] for entry in storage_report]
        report_html += "<h3>Storage Account Public Access Report:</h3>"
        report_html += create_html_table(storage_table, ["Name", "Resource Group", "Public Access"])
    else:
        report_html += "<p>No Storage Accounts found.</p>"

    # Key Vault Report
    if key_vault_report:
        key_vault_table = [[entry["name"], entry["resource_group"], entry["public_access"]] for entry in key_vault_report]
        report_html += "<h3>Key Vault Public Access Report:</h3>"
        report_html += create_html_table(key_vault_table, ["Name", "Resource Group", "Public Access"])
    else:
        report_html += "<p>No Key Vaults found.</p>"

    # Function App Report
    if function_app_report:
        function_app_table = [[entry["name"], entry["resource_group"], entry["public_access"]] for entry in function_app_report]
        report_html += "<h3>Function App Report:</h3>"
        report_html += create_html_table(function_app_table, ["Name", "Resource Group", "Public Access"])
    else:
        report_html += "<p>No Function Apps found.</p>"

    # Redis Cache Report
    if redis_report:
        redis_table = [[entry["name"], entry["resource_group"], entry["enable_non_ssl_port"]] for entry in redis_report]
        report_html += "<h3>Redis Cache Report:</h3>"
        report_html += create_html_table(redis_table, ["Name", "Resource Group", "Enable Non-SSL Port"])
    else:
        report_html += "<p>No Redis Caches found.</p>"

    return report_html

# Send email using SendGrid
def send_email_with_sendgrid(api_key, sender_email, recipient_email, subject, content_body):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        from_email = Email(sender_email)
        to_email = To(recipient_email)
        content = Content("text/plain", content_body)
        mail = Mail(from_email, to_email, subject, content)
        sg.client.mail.send.post(request_body=mail.get())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

# Main function
def main():
    parser = argparse.ArgumentParser(description="Fetch Azure resource details and send an email report.")
    parser.add_argument("--subscription-id", required=True, help="Azure subscription ID")
    parser.add_argument("--sendgrid-api-key", required=True, help="SendGrid API key")
    parser.add_argument("--sender-email", required=True, help="Sender email address")
    parser.add_argument("--recipient-email", required=True, help="Recipient email address")

    args = parser.parse_args()

    storage_report = fetch_storage_account_status(args.subscription_id)
    key_vault_report = fetch_key_vault_status(args.subscription_id)
    function_app_report = fetch_function_app_status(args.subscription_id)
    redis_report = fetch_redis_status(args.subscription_id)

    email_content = generate_report_content(storage_report, key_vault_report, function_app_report, redis_report)
    send_email_with_sendgrid(args.sendgrid_api_key, args.sender_email, args.recipient_email, "Azure Resource Report", email_content)

if __name__ == "__main__":
    main()
