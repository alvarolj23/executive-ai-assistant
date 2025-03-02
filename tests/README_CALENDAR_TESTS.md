# Calendar Invite Testing

This directory contains test scripts for verifying the calendar invite functionality.

## Prerequisites

Before running the tests, make sure:

1. You have properly set up Google Calendar authentication (token.json should exist in the eaia/.secrets directory)
2. Your Google account has the necessary permissions for Calendar API access
3. You have the required environment variables set (or you'll need to provide them as command-line arguments)

## Test Scripts

### 1. Simple Command-Line Test

The simplest way to test calendar invites is using the command-line script:

```bash
# Set your email as an environment variable (recommended)
export TEST_EMAIL="your.email@example.com"

# Run the basic test (will schedule an event 30 minutes from now)
python tests/test_send_invite.py

# Or with custom parameters
python tests/test_send_invite.py \
  --email your.email@example.com \
  --participants "colleague1@example.com,colleague2@example.com" \
  --title "Test Meeting - Please Ignore" \
  --start-offset 60 \
  --duration 45 \
  --timezone "America/New_York" \
  --calendar "primary" \
  --verify
```

### 2. Unit Test Suite

For automated testing in a CI/CD environment, use the unittest-based test:

```bash
# Set required environment variables
export TEST_EMAIL="your.email@example.com"
export PARTICIPANT_EMAIL_1="participant1@example.com"
export TEST_CALENDAR_NAME="primary"
export TEST_TIMEZONE="America/Los_Angeles"

# Run the unittest
python tests/test_calendar_invite.py
```

## Command-Line Arguments for test_send_invite.py

| Argument | Description | Default |
|----------|-------------|---------|
| `--email` | Your email address (organizer) | `$TEST_EMAIL` env var |
| `--participants` | Comma-separated list of participant emails | Empty |
| `--title` | Title of the calendar event | Auto-generated with timestamp |
| `--start-offset` | Minutes from now to schedule the event | 30 |
| `--duration` | Duration of the event in minutes | 30 |
| `--timezone` | Timezone for the event | America/Los_Angeles |
| `--calendar` | Name of the calendar to use | primary |
| `--verify` | Verify the event was created | False |

## Troubleshooting

If the tests fail, check the following:

1. **Authentication Issues**: Ensure your token.json is valid and has the right permissions
2. **Email Format**: Make sure all email addresses are valid
3. **Calendar Permissions**: Verify you have write access to the specified calendar
4. **API Quotas**: Check if you've hit Google API usage limits
5. **Timezone Issues**: Ensure the timezone string is valid (e.g., "America/Los_Angeles")
6. **LangChain Tool Issues**: The `get_events_for_days` function is a LangChain tool and must be invoked properly. If you see errors like `TypeError: BaseTool.__call__() got an unexpected keyword argument`, it means you're calling the tool incorrectly. The test scripts include helper functions to handle this properly.

## Notes

- Events are created with Google Meet integration by default
- The script adds email notifications (24 hours before) and popup reminders (10 minutes before)
- For repeated testing, consider using a dedicated test calendar to avoid cluttering your main calendar
- The tests handle LangChain tool deprecation warnings by using the appropriate invocation method 