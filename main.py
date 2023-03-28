import requests
import json
import re

API_BASE_URL = 'https://portal.ixon.cloud:443/api'


def validate_auth(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        raise Exception("Invalid credentials")


def get_data(url, fields, headers, filters=None):
    more_after = None
    data_list = []

    while True:
        response = requests.get(
            f"{API_BASE_URL}{url}?fields={fields}{f'&page-after={more_after}' if more_after else ''}{f'&filters={filters}' if filters else ''}",
            headers=headers)
        data = response.json()["data"]
        data_list.extend(data)
        more_after = response.json()["moreAfter"]

        if more_after is None:
            break

    return data_list


# Load API configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

# Set headers for API requests
headers = {
    'Api-Version': '2',
    'accept': 'application/json',
    'authorization': config['authorization'],
    'Api-Company': config['api_company'],
    'Api-Application': config['api_application']
}

# Validate authorization
validate_auth(f"{API_BASE_URL}/agents", headers)

# List available agents
print('Available agents:')
agents_data = get_data('/agents', 'name', headers)
for i, agent in enumerate(agents_data):
    print(f"{i + 1}. {agent['name']} ({agent['publicId']})")

# Prompt user to select an agent
selected_agent_index = int(input('Enter the index of the agent to use: ')) - 1
selected_agent = agents_data[selected_agent_index]
print(
    f"Selected agent: {selected_agent['name']} ({selected_agent['publicId']})")

# Prompt user to select a data source for the selected agent
data_sources_data = get_data(
    f"/agents/{selected_agent['publicId']}/data-sources",
    'name,publicId', headers)
print('Select a data source:')
for i, data_source in enumerate(data_sources_data):
    print(f"{i + 1}. {data_source['name']} ({data_source['publicId']})")
selected_data_source_index = int(input()) - 1
selected_data_source = data_sources_data[selected_data_source_index]

# Retrieve variables for the selected data source
tag_filter = f"eq(source.publicId,\"{selected_data_source['publicId']}\")"
variables_data = get_data(
    f"/agents/{selected_agent['publicId']}/data-variables",
    'variableId,name,address,source,type', headers, tag_filter)
print('Variables for selected data source:')
print('variableId | name | address | type')
for variable in variables_data:
    print(
        f"${variable['variableId']} | {variable['name']} | {variable['address']} | {variable['type']}")


def infix_to_postfix(infix_formula):
    # Map natural language operators to postfix operators
    operators = {
        'and': '&&',
        'or': '||',
        '>': '>',
        '>=': '>=',
        '<': '<',
        '<=': '<=',
        '==': '==',
        '!=': '!='
    }

    # Split the comparison into tokens and replace natural language operators with postfix operators
    # Modified to handle string literals
    tokens = re.findall(r'"[^"]+"|\S+', infix_formula)
    for i, token in enumerate(tokens):
        if token in operators:
            tokens[i] = operators[token]

    # Convert the tokens to postfix notation
    precedence = {
        '(': 0, '||': 1, '&&': 2, '>': 3, '>=': 3, '<': 3, '<=': 3, '==': 3,
        '!=': 3, '+': 4, '-': 4, '*': 5, '/': 5}
    postfix_formula = []
    operator_stack = []
    for token in tokens:
        if token.isnumeric() or token.startswith('$') or token == 'true' or token == 'false' or token.startswith('"') and token.endswith('"'):  # Modified to handle string literals
            postfix_formula.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack[-1] != '(':
                right_operand = postfix_formula.pop()
                left_operand = postfix_formula.pop()
                operator = operator_stack.pop()
                postfix_formula.append(
                    f'{left_operand} {right_operand} {operator}')
            operator_stack.pop()
        else:
            while operator_stack and operator_stack[-1] != '(' and precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0):
                right_operand = postfix_formula.pop()
                left_operand = postfix_formula.pop()
                operator = operator_stack.pop()
                postfix_formula.append(
                    f'{left_operand} {right_operand} {operator}')
            operator_stack.append(token)
    while operator_stack:
        postfix_formula.append(operator_stack.pop())

    # Return the postfix formula as a string
    return ' '.join(postfix_formula)


comparison = input(
    'Create a formula using the selected variables (use "$" prefix for variables and infix notation, e.g., "$var1 > $var2 and $var3 < $var4")\nyou can connect comparisons using "and" and "or" operators\nFor example ( $30 > 5000 ) and ( $48 == true ) or ( $51 == "Hello"):\n')
postfix_formula = infix_to_postfix(comparison)
print(postfix_formula)

# Prompt user to enter other alarm properties
name = input('Enter a name for the alarm: ')
severity = input(
    'Enter a severity for the alarm (low, medium, high) [default: medium]: ') or 'medium'
type = input(
    'Enter a type for the alarm (boolean, numeric) [default: boolean]: ') or 'boolean'
on_delay = input(
    'Enter an on-delay for the alarm (in seconds) [default: 1]: ') or '1'

# Retrieve available audiences
audiences_data = get_data(
    '/audiences', 'default,name,publicId', headers)
print('Available audiences:')
for i, audience in enumerate(audiences_data):
    print(f"{i + 1}. {audience['name']}")
selected_audience_index = int(
    input('Enter the index of the audience to use: ')) - 1
selected_audience = audiences_data[selected_audience_index]
print(
    f"Selected audience: {selected_audience['name']} ({selected_audience['default']})")

# Construct payload for creating the alarm
payload = {
    "audience": {
        "publicId": selected_audience['publicId']
    },
    "name": name,
    "formula": postfix_formula,
    "operatorInstructionRtn": None,
    "severity": severity,
    "onDelay": int(on_delay),
    "type": type,
    "source": {
        "publicId": selected_data_source['publicId']
    }
}

# Send request to create the alarm
response = requests.post(
    f"{API_BASE_URL}/agents/{selected_agent['publicId']}/data-alarms",
    headers=headers,
    json=payload)

# Print response
print(f"Response code: {response.status_code}")
print(response.json())
