# Configure Advanced Alarms

## Introduction

This script allows you to create a new data alarm in IXON Cloud--with more than one condition--and push it to an IXrouter.

## Setup

1. Install the required packages: pip install -r requirements.txt
2. Create a new file named config.json in the same directory as main.py, and copy the following JSON object into it:

```json
Copy code
{
    "authorization": "Bearer [INSERT YOUR IXON API TOKEN HERE]",
    "api_company": "[INSERT YOUR IXON COMPANY ID HERE]",
    "api_application": "[INSERT YOUR IXON APPLICATION ID HERE]"
}
```

4. Replace [INSERT YOUR IXON API TOKEN HERE] with your IXON API token, and [INSERT YOUR IXON COMPANY ID HERE] and [INSERT YOUR IXON APPLICATION ID HERE] with your IXON company and application IDs, respectively.
5. Save and close config.json

## Usage

1. Run the script: python main.py
2. Follow the on-screen prompts to select an agent, data source, and variables to use in the alarm, and to create the alarm formula.
3. When prompted to enter a name for the alarm, enter a name of your choice.
4. When prompted to enter a severity for the alarm, enter one of the following options: low, medium, or high. If you do not enter a severity, the script will use medium as the default.
5. When prompted to enter a type for the alarm, enter one of the following options: boolean or numeric. If you do not enter a type, the script will use boolean as the default.
6. When prompted to enter an on-delay for the alarm, enter a number of seconds to delay the alarm's activation after it is triggered. If you do not enter an on-delay, the script will use 1 second as the default.
7. When prompted to select an audience.
8. The script will create the new alarm and print the response from the IXON API.
9. **IMPORTANT**: After creating a new alarm, you must go to the IXON Fleet Manager and push the configuration to your device in order for the new alarm to work on the IXrouter. You can do this by going to the device's page in the IXON Fleet Manager, and clicking the "Push config to device" button.

That's it! You have now created a new data alarm in IXON Cloud and pushed it to your IXrouter.
