from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import time


def setup_gmail_service():
    """Sets up and returns the Gmail service with appropriate credentials."""
    SCOPES = ["https://mail.google.com/"]
    creds = None

    # If there's an existing token, we should remove it since we're changing scopes
    if os.path.exists("token.pickle"):
        os.remove("token.pickle")

    # Get new credentials with updated scope
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def delete_emails_by_category(service, category, user_id="me", batch_size=100):
    """Deletes ALL emails from specified category (SOCIAL, PROMOTIONS, or UPDATES)."""
    total_deleted = 0

    try:
        while True:  # Keep going until no more messages are found
            # Search for messages in the specified category
            query = f"category:{category}"
            results = (
                service.users()
                .messages()
                .list(userId=user_id, q=query, maxResults=batch_size)
                .execute()
            )
            messages = results.get("messages", [])

            if not messages:
                print(f"No more messages found in {category} category.")
                break

            print(f"Found {len(messages)} messages in {category} category.")

            # Delete the batch of messages
            batch_ids = {"ids": [msg["id"] for msg in messages]}
            service.users().messages().batchDelete(
                userId=user_id, body=batch_ids
            ).execute()

            total_deleted += len(messages)
            print(
                f"Deleted batch of {len(messages)} messages. Total deleted so far: {total_deleted}"
            )

            # Add a small delay to avoid hitting rate limits
            time.sleep(0.5)

        print(
            f"Successfully deleted all {total_deleted} messages in {category} category."
        )

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Total messages deleted before error: {total_deleted}")


def main():
    """Main function to run the email cleanup process."""
    print("Starting Gmail cleanup process...")
    service = setup_gmail_service()

    # Added UPDATES to the categories list
    categories = ["SOCIAL", "PROMOTIONS", "UPDATES"]
    for category in categories:
        print(f"\nProcessing {category} category...")
        delete_emails_by_category(service, category)

    print("\nCleanup process completed!")


if __name__ == "__main__":
    main()
