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

def main():
    subscription_id = "d8eaebd9-e25f-48b1-b7fe-95d296133cfa"  # Replace with your Azure subscription ID

    # Fetch storage account status
    report = fetch_storage_account_status(subscription_id)

    # Print report
    print("Storage Account Public Access Report:")
    for entry in report:
        print(
            f"Storage Account: {entry['name']}, Resource Group: {entry['resource_group']}, Public Access: {entry['public_access']}"
        )

if __name__ == "__main__":
    main()
