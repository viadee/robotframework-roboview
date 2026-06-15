---
name: robot-framework
description: Robot Framework test development and resource file creation. Use when writing, modifying, or debugging Robot Framework tests, keywords, and resources. Covers BDD syntax, keyword design, resource organization, and test patterns.
applyTo: "**/*.{robot,resource}"
---

# Robot Framework Development

## Project Structure

```
rf_usergrp_vtiger/
├── robocop.toml           # Robocop linting configuration
├── resources/             # Reusable keyword libraries
│   ├── common.resource    # Common utilities
│   ├── globals.resource   # Global variables
│   ├── startup.resource   # Setup/teardown keywords
│   └── <domain>/          # Domain-specific resources
└── tests/                 # Test files organized by domain
    └── <domain>/          # Domain-specific tests
```

## Test File Structure

```robotframework
*** Settings ***
Documentation    Brief description of test suite purpose
Resource         ../../resources/vtiger.resource
Test Setup       startup.Startup Vtiger
Test Teardown    startup.Alles Schließen
Test Tags        feature:login  sprint:42

*** Variables ***
${TEST_USER}     robot_user
${TEST_PASS}     secret123

*** Test Cases ***
Valid Login With Correct Credentials
    [Documentation]    Verify user can login with valid credentials
    [Tags]    XRAY:SVQ-4  positiv  smoke
    login.Login Robot
    dashboard.Verify Dashboard Loaded

Invalid Login Shows Error Message
    [Documentation]    Verify error message for invalid credentials
    [Tags]    XRAY:SVQ-5  negativ
    login.Enter Username    invalid_user
    login.Enter Password    wrong_pass
    login.Click Login Button
    login.Verify Error Message    Invalid credentials
```

## Resource File Structure

```robotframework
*** Settings ***
Documentation    Description of resource purpose
Library          Browser
Library          Collections
Resource         ../common.resource
Resource         selLogin.resource

*** Variables ***
${LOGIN_URL}           https://example.com/login
${DEFAULT_TIMEOUT}     10s

*** Keywords ***
Login With Credentials
    [Documentation]    Login with specified username and password
    [Arguments]    ${username}    ${password}
    Enter Username    ${username}
    Enter Password    ${password}
    Click Login Button

Enter Username
    [Documentation]    Enter username in login form
    [Arguments]    ${username}
    Fill Text    ${selLogin.USERNAME_INPUT}    ${username}

Enter Password
    [Documentation]    Enter password in login form
    [Arguments]    ${password}
    Fill Secret    ${selLogin.PASSWORD_INPUT}    $password

Click Login Button
    [Documentation]    Click the login button
    Click    ${selLogin.LOGIN_BUTTON}

Verify Login Successful
    [Documentation]    Verify user is logged in
    Wait For Elements State    ${selLogin.DASHBOARD}    visible    ${DEFAULT_TIMEOUT}
```

## Selector Resource Files

Organize selectors separately for maintainability:

```robotframework
*** Settings ***
Documentation    Selectors for Login page

*** Variables ***
# Form elements
${USERNAME_INPUT}     id=username
${PASSWORD_INPUT}     id=password
${LOGIN_BUTTON}       css=button[type="submit"]

# Messages
${ERROR_MESSAGE}      css=.error-message
${SUCCESS_MESSAGE}    css=.success-message

# Dashboard elements
${DASHBOARD}          css=.dashboard-container
```

## Keyword Design Patterns

### 1. High-Level Business Keywords

```robotframework
User Creates New Lead
    [Documentation]    Complete flow to create a new lead
    [Arguments]    ${lead_data}
    Navigate To Leads
    Click New Lead Button
    Fill Lead Form    ${lead_data}
    Save Lead
    Verify Lead Created    ${lead_data}[name]
```

### 2. Parameterized Keywords

```robotframework
Fill Form Field
    [Documentation]    Fill a form field with validation
    [Arguments]    ${selector}    ${value}    ${clear_first}=${TRUE}
    IF    ${clear_first}
        Clear Text    ${selector}
    END
    Fill Text    ${selector}    ${value}
```

### 3. Verification Keywords

```robotframework
Verify Table Contains Row
    [Documentation]    Verify table contains row with expected data
    [Arguments]    ${table_selector}    @{expected_values}
    ${rows}=    Get Elements    ${table_selector} tbody tr
    FOR    ${row}    IN    @{rows}
        ${text}=    Get Text    ${row}
        ${found}=    Evaluate    all(v in '''${text}''' for v in ${expected_values})
        IF    ${found}
            RETURN
        END
    END
    Fail    Table does not contain expected row: ${expected_values}
```

### 4. BDD-Style Keywords

```robotframework
*** Keywords ***
Given User Is On Login Page
    Go To    ${LOGIN_URL}
    Wait For Elements State    ${USERNAME_INPUT}    visible

When User Enters Valid Credentials
    Enter Username    ${VALID_USER}
    Enter Password    ${VALID_PASS}

And User Clicks Login
    Click Login Button

Then User Should See Dashboard
    Verify Login Successful
```

## Documentation Standards

Every keyword should have:

```robotframework
Keyword Name
    [Documentation]    Brief description of what the keyword does.
    ...                Additional context or notes if needed.
    ...                
    ...                Example:
    ...                | Keyword Name | arg1 | arg2 |
    [Arguments]    ${arg1}    ${arg2}=${DEFAULT}
    [Tags]    robot:private    # Optional: mark as internal
```

## Error Handling

```robotframework
Safe Click Element
    [Documentation]    Click element with retry and screenshot on failure
    [Arguments]    ${selector}    ${timeout}=${DEFAULT_TIMEOUT}
    TRY
        Wait For Elements State    ${selector}    visible    ${timeout}
        Click    ${selector}
    EXCEPT    *timeout*    type=glob
        Take Screenshot    failure_{selector}
        Fail    Element not found: ${selector}
    END
```

## Variable Patterns

```robotframework
*** Variables ***
# Scalars
${BASE_URL}           https://example.com
${DEFAULT_TIMEOUT}    10s

# Lists
@{VALID_STATUSES}     Active    Pending    Complete

# Dictionaries
&{USER_DATA}
...    username=testuser
...    email=test@example.com
...    role=admin
```

## Robocop Compliance

Follow Robocop rules to maintain code quality:

- **0201**: Keywords should have documentation
- **0301**: Use consistent variable naming (${snake_case} for scalars)
- **0501**: Avoid too long test cases (max 20 keywords)
- **0502**: Avoid too long keywords (max 10 steps)
- **0601**: Use [Setup] and [Teardown] at test level

## Testing Best Practices

1. **Independence**: Each test should be runnable in isolation
2. **Descriptive names**: Test names should describe the behavior
3. **Single responsibility**: One test verifies one behavior
4. **Clean state**: Tests should clean up after themselves
5. **Tags for filtering**: Use tags for test categorization

```robotframework
*** Test Cases ***
# Good: Descriptive, behavior-focused
User Cannot Login With Expired Password
    [Tags]    security  authentication  negativ

# Bad: Vague, implementation-focused
Test Login 3
    [Tags]    login
```
