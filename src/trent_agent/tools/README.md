# Firebase Tool

The Firebase Tool allows you to interact with Firebase Firestore collections directly from your agents or scripts.

## Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Generate a service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file as `serviceAccountKey.json`

3. Configure the service account in one of two ways:
   - **Local Development**: Place `serviceAccountKey.json` in `src/trent_agent/config/`
   - **Deployment**: Add the JSON content as a string to `FIREBASE_SERVICE_ACCOUNT` in your `.env` file

## Features

- Create documents in collections
- Read documents from collections
- Update existing documents
- Delete documents
- Query documents with various conditions

## Usage

### Basic Usage

```python
from trent_agent.tools import FirebaseTool

# Initialize the Firebase tool
firebase_tool = FirebaseTool()

# Create a document
result = firebase_tool._run(
    operation="create",
    collection="users",
    document_id="user123",
    data={"name": "John Doe", "email": "john@example.com", "age": 30}
)
print(result)

# Read a document
result = firebase_tool._run(
    operation="read",
    collection="users",
    document_id="user123"
)
print(result)

# Update a document
result = firebase_tool._run(
    operation="update",
    collection="users",
    document_id="user123",
    data={"age": 31}
)
print(result)

# Delete a document
result = firebase_tool._run(
    operation="delete",
    collection="users",
    document_id="user123"
)
print(result)
```

### Querying Documents

```python
# Query documents with conditions
result = firebase_tool._run(
    operation="query",
    collection="users",
    query_conditions=[
        {"field": "age", "operator": ">=", "value": 25}
    ]
)
print(result)
```

### Supported Query Operators

- `==`: Equal to
- `>`: Greater than
- `<`: Less than
- `>=`: Greater than or equal to
- `<=`: Less than or equal to
- `array-contains`: Contains the specified value in an array
- `array-contains-any`: Contains any of the specified values in an array
- `in`: Equal to one of the specified values

## Parameters

### Required Parameters

- `operation`: The operation to perform ('create', 'read', 'update', 'delete', 'query')
- `collection`: The name of the collection

### Optional Parameters

- `document_id`: The ID of the document (required for create, read, update, delete)
- `data`: The data to write (required for create, update)
- `query_conditions`: List of conditions for querying (each condition is a dict with field, operator, value)

## Example

See `examples/firebase_example.py` for a complete example of how to use the Firebase tool.
