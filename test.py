import subprocess
import json

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
            network_acls = properties.get("networkAcls", {}) if isinstance(properties, dict) else {}
            public_access = network_acls.get("defaultAction", "Unknown")

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

            # Get public network access setting (if applicable)
            app_details = {"name": name, "resource_group": resource_group, "public_access": "N/A"}  # Function apps don't have a direct public access setting

            report.append(app_details)

        return report

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
        return []

def main():
    subscription_id = "d8eaebd9-e25f-48b1-b7fe-95d296133cfa"  # Replace with your Azure subscription ID

    # Fetch statuses
    storage_report = fetch_storage_account_status(subscription_id)
    key_vault_report = fetch_key_vault_status(subscription_id)
    function_app_report = fetch_function_app_status(subscription_id)

    # Print reports
    print("\nStorage Account Public Access Report:")
    for entry in storage_report:
        print(
            f"Storage Account: {entry['name']}, Resource Group: {entry['resource_group']}, Public Access: {entry['public_access']}"
        )

    print("\nKey Vault Public Access Report:")
    for entry in key_vault_report:
        print(
            f"Key Vault: {entry['name']}, Resource Group: {entry['resource_group']}, Public Access: {entry['public_access']}"
        )

    print("\nFunction App Report:")
    for entry in function_app_report:
        print(
            f"Function App: {entry['name']}, Resource Group: {entry['resource_group']}, Public Access: {entry['public_access']}"
        )

if __name__ == "__main__":
    main()
