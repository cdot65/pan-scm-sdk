from scm.client import Scm
from scm.config.security import SecurityRule
from scm.exceptions import InvalidObjectError, NotFoundError, AuthenticationError, NameNotUniqueError, ReferenceNotZeroError

# Initialize client with debug logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG",  # Enable detailed logging
)

# Note: This script requires a folder named "Test Folder".
# Please create it before running the script.


def create_security_rule():
    try:
        # Initialize security rule object
        security_rule = SecurityRule(client)
        try:
            # Create Security Rule objects
            rule_1 = {
                "folder": "Test Folder",
                "name": "Test Security Rule 1",
                "action": 'allow',
                "from_": 'local',
                "to_": 'internet',
                "source": ['10.0.0.0/8'],
                "destination": ['any'],
                "description": "Default outbound allow",
                "source_user": ['any'],
                "application": ['web-browsing', 'ssl'],
                "service": ['application-default'],
                "category": ['any'],
                "profile_setting": {
                    "group": ["best-practice"]
                },
                "log_start": False,
                "log_end": True,
            }
            security_rule.create(rule_1)
            print(f"Created rule: {rule_1['name']}")
        except NameNotUniqueError as e:
            print(f"Name conflict: {e.message}")
        except InvalidObjectError as e:
            print(f"Invalid data: {e.message}")
            if e.details:
                print(f"Details: {e.details}")

    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")
        print(f"Status code: {e.http_status_code}")


def fetch_and_update_security_rule():
    security_rule = SecurityRule(client)

    # Fetch and update the rule
    try:
        fetched_rule = security_rule.fetch(name="Test Security Rule 1", folder="Test Folder")
        fetched_rule.description = "Updated rule description"
        updated = security_rule.update(fetched_rule)
        print(f"Updated description: {updated.description}")
    except NotFoundError as e:
        print(f"Rule not found: {e.message}")


def fetch_and_cleanup_security_rule():
    security_rule = SecurityRule(client)

    # Fetch and clean up the rule
    try:
        fetched_rule = security_rule.fetch(name="Test Security Rule 1", folder="Test Folder")
        security_rule.delete(fetched_rule.id)
        print(f"Rule {fetched_rule.name} deleted succesfully.")
    except NotFoundError as e:
        print(f"Rule not found: {e.message}")
    except ReferenceNotZeroError as e:
        print(f"Cannot delete rule - still in use: {e.message}")


if __name__ == "__main__":
    create_security_rule()
    fetch_and_update_security_rule()
    fetch_and_cleanup_security_rule()
