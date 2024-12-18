import subprocess
import json
import argparse
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

# Fetch storage account details
def fetch_storage_account_status(subscription_id):
    try:
        # Set Azure subscription
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        # Get list of storage accounts
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

            # Get public network access setting
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
        # Set Azure subscription
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        # Get list of key vaults
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

            # Get public network access setting
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
        # Set Azure subscription
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        # Get list of function apps
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

            # Get public network access setting
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
        # Set Azure subscription
        subprocess.run(["az", "account", "set", "--subscription", subscription_id], check=True)

        # Get list of Redis caches
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

            # Get enableNonSslPort setting
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

# Send email using SendGrid
def send_email_with_sendgrid(api_key, sender_email, recipient_email, subject, content_body):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        # Create the email message
        from_email = Email(sender_email)  # Verified sender email
        to_email = To(recipient_email)    # Recipient email
        subject = subject
        content = Content("text/plain", content_body)
        
        mail = Mail(from_email, to_email, subject, content)
        
        # Send the email
        response = sg.client.mail.send.post(request_body=mail.get())
        
        print("Email sent successfully!")
        print(f"Status Code: {response.status_code}")
        print(f"Body: {response.body}")
        print(f"Headers: {response.headers}")
    
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

# Generate the report content
def generate_report_content(storage_report, key_vault_report, function_app_report, redis_report):
    report_lines = ["Azure Report Summary:\n"]

    # Storage Account Report
    report_lines.append("Storage Account Public Access Report:")
    for entry in storage_report:
        report_lines.append(
            f"Storage Account: {entry['name']}, Resource Group: {entry['resource_group']}, Public Access: {entry['public_access']}"
        )

    # Key Vault Report
    report_lines.append("\nKey Vault Public Access Report:")
    for entry in key_vault_report:
        report_lines.append(
            f"Key Vault: {entry['name']}, Resource Group: {entry['resource_group']}, Public Access: {entry['public_access']}"
        )

    # Function App Report
    report_lines.append("\nFunction App Report:")
    for entry in function_app_report:
        report_lines.append(
            f"Function App: {entry['name']}, Resource Group: {entry['resource_group']}, Public Access: {entry['public_access']}"
        )

    # Redis Cache Report
    report_lines.append("\nRedis Cache Report:")
    for entry in redis_report:
        report_lines.append(
            f"Redis Cache: {entry['name']}, Resource Group: {entry['resource_group']}, Enable Non-SSL Port: {entry['enable_non_ssl_port']}"
        )

    return "\n".join(report_lines)

# Main function
def main():
    parser = argparse.ArgumentParser(description="Fetch Azure resource details and send an email report.")
    parser.add_argument("--subscription-id", required=True, help="Azure subscription ID")
    parser.add_argument("--sendgrid-api-key", required=True, help="SendGrid API key")
    parser.add_argument("--sender-email", required=True, help="Sender email address")
    parser.add_argument("--recipient-email", required=True, help="Recipient email address")

    args = parser.parse_args()

    # Fetch statuses
    storage_report = fetch_storage_account_status(args.subscription_id)
    key_vault_report = fetch_key_vault_status(args.subscription_id)
    function_app_report = fetch_function_app_status(args.subscription_id)
    redis_report = fetch_redis_status(args.subscription_id)

    # Generate report content
    email_content = generate_report_content(storage_report, key_vault_report, function_app_report, redis_report)

    # Send the email
    send_email_with_sendgrid(args.sendgrid_api_key, args.sender_email, args.recipient_email, "Azure Resource Report", email_content)

if __name__ == "__main__":
    main()
