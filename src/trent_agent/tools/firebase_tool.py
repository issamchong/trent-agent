import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import BaseModel, PrivateAttr, Field
from crewai.tools import BaseTool
from typing import Dict, Any, List, Optional, TypedDict, Union, Literal

class QueryCondition(BaseModel):
    field: str
    operator: str = "=="
    value: Any

class FirebaseToolInput(BaseModel):
    # --- CHANGE: Restrict operations to only 'read' and 'query' ---
    operation: Literal['read', 'query'] = Field(
        description="The operation to perform. Only 'read' or 'query' are allowed."
    )
    collection: str = Field(
        description="The name of the collection to operate on"
    )
    document_id: Optional[str] = Field(
        None,
        description="The ID of the document (required for 'read' operation)"
    )
    # --- CHANGE: 'data' field is removed as it's not needed for read-only operations ---
    query_conditions: Optional[List[QueryCondition]] = Field(
        None,
        description="List of conditions for querying (used with 'query' operation)"
    )
    return_objects: Optional[bool] = Field(
        False,
        description="When querying, return a JSON array of document objects instead of a textual summary"
    )

# --- CHANGE: Updated class to be read-only ---
class FirebaseReadOnlyTool(BaseTool):
    # --- CHANGE: Updated name and description ---
    name: str = "Firebase Read-Only Tool"
    description: str = "A tool to read and query data from Firebase Firestore collections. You can read a specific document by its ID or query a collection for multiple documents."
    args_schema: type[BaseModel] = FirebaseToolInput
    
    _db: Any = PrivateAttr(default=None)

    def __init__(self):
        super().__init__()
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase app with service account credentials from a Base64 encoded environment variable."""
        if not firebase_admin._apps:
            encoded_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            
            if not encoded_credentials:
                raise ValueError(
                    "Firebase credentials not found. Please set the "
                    "GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable "
                    "with your Base64 encoded service account JSON."
                )
            
            try:
                json_credentials_str = base64.b64decode(encoded_credentials).decode('utf-8')
                service_account_dict = json.loads(json_credentials_str)
                cred = credentials.Certificate(service_account_dict)
                
            except (base64.binascii.Error, json.JSONDecodeError) as e:
                raise ValueError(
                    f"Failed to decode or parse the GOOGLE_APPLICATION_CREDENTIALS_JSON "
                    f"environment variable. Please ensure it is a valid Base64 encoded JSON string. Original error: {e}"
                )
            
            firebase_admin.initialize_app(cred)

        self._db = firestore.client()

    # --- CHANGE: Simplified _run method to only handle 'read' and 'query' ---
    def _run(self, 
             operation: str, 
             collection: str, 
             document_id: Optional[str] = None,
             query_conditions: Optional[List[Dict[str, Any]]] = None,
             return_objects: bool = False) -> str:
        """
        Execute read-only Firebase operations.

        Args:
            operation: The operation to perform ('read' or 'query')
            collection: The name of the collection
            document_id: The ID of the document (required for 'read')
            query_conditions: List of conditions for querying (used with 'query')
            return_objects: If True, return a JSON array of documents for queries.

        Returns:
            Result of the operation as a string.
        """
        try:
            # --- CHANGE: Logic for 'create', 'update', 'delete' has been removed ---
            if operation == 'read':
                if not document_id:
                    return "Error: document_id is required for read operation"

                doc_ref = self._db.collection(collection).document(document_id)
                doc = doc_ref.get()
                if doc.exists:
                    return f"Document data: {doc.to_dict()}"
                else:
                    return f"Document {document_id} not found in collection {collection}"

            elif operation == 'query':
                collection_ref = self._db.collection(collection)
                all_results = []
                total_count = 0
                
                try:
                    # If no query conditions are provided, get all documents
                    if not query_conditions:
                        docs = collection_ref.stream()
                        for doc in docs:
                            total_count += 1
                            doc_data = doc.to_dict()
                            if return_objects:
                                to_add = doc_data.copy()
                                to_add['_id'] = doc.id
                                all_results.append(to_add)
                            else:
                                if total_count <= 10:
                                    summary = {
                                        'title': doc_data.get('title', 'No title'),
                                        'status': doc_data.get('status', 'No status'),
                                        'category': doc_data.get('categoryId', 'No category')
                                    }
                                    all_results.append(f"Document: {summary}")

                        if return_objects:
                            try:
                                return json.dumps({
                                    'total': total_count,
                                    'documents': all_results
                                }, default=str)
                            except Exception as e:
                                return f"Error serializing documents: {str(e)}"

                        summary = [
                            f"Total documents in collection: {total_count}",
                            f"Sample of first 10 documents:",
                            *all_results,
                            "\nTo get specific document details, use the 'read' operation with a document ID."
                        ]
                        return "\n".join(summary)
                    else:
                        query = collection_ref
                        for condition in query_conditions:
                            field = condition.get('field')
                            operator = condition.get('operator', '==')
                            value = condition.get('value')

                            if not field:
                                return "Error: Each query condition must have a 'field'"

                            if operator == '==':
                                query = query.where(field, '==', value)
                            elif operator == '>=':
                                query = query.where(field, '>=', value)
                            elif operator == '<=':
                                query = query.where(field, '<=', value)
                            elif operator == '>':
                                query = query.where(field, '>', value)
                            elif operator == '<':
                                query = query.where(field, '<', value)
                            elif operator == 'array-contains':
                                query = query.where(field, 'array-contains', value)
                            elif operator == 'array-contains-any':
                                query = query.where(field, 'array-contains-any', value)
                            elif operator == 'in':
                                query = query.where(field, 'in', value)
                            else:
                                return f"Error: Unsupported operator {operator}"

                        docs = query.stream()
                        total_count = 0
                        for doc in docs:
                            total_count += 1
                            doc_data = doc.to_dict()
                            if return_objects:
                                to_add = doc_data.copy()
                                to_add['_id'] = doc.id
                                all_results.append(to_add)
                            else:
                                if total_count <= 10:
                                    summary = {
                                        'title': doc_data.get('title', 'No title'),
                                        'status': doc_data.get('status', 'No status'),
                                        'category': doc_data.get('categoryId', 'No category')
                                    }
                                    all_results.append(f"Document: {summary}")

                        if return_objects:
                            try:
                                return json.dumps({
                                    'total': total_count,
                                    'documents': all_results
                                }, default=str)
                            except Exception as e:
                                return f"Error serializing documents: {str(e)}"

                        summary = [
                            f"Total documents matching query: {total_count}",
                            f"Sample of first 10 matching documents:",
                            *all_results,
                            "\nTo get specific document details, use the 'read' operation with a document ID."
                        ]
                        return "\n".join(summary)
                        
                except Exception as e:
                    return f"Error during query: {str(e)}"

            else:
                # --- CHANGE: Updated error message to reflect new allowed operations ---
                return f"Error: Unsupported operation '{operation}'. This tool only supports 'read' and 'query'."

        except Exception as e:
            return f"Error executing Firebase operation: {str(e)}"

    name: str = "Firebase Tool"
    description: str = "A tool to interact with Firebase Firestore collections. You can create, read, update, and delete documents in collections."
    args_schema: type[BaseModel] = FirebaseToolInput
    
    _db: Any = PrivateAttr(default=None)

    def __init__(self):
        super().__init__()
        self._initialize_firebase()

    def _initialize_firebase(self):  # <-- FIXED: Removed one space to align with other methods
        """Initialize Firebase app with service account credentials from a Base64 encoded environment variable."""
        if not firebase_admin._apps:
            # Use the new, more descriptive environment variable name
            encoded_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            
            if not encoded_credentials:
                raise ValueError(
                    "Firebase credentials not found. Please set the "
                    "GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable "
                    "with your Base64 encoded service account JSON."
                )
            
            try:
                # Decode from Base64 to bytes, then to a UTF-8 string
                json_credentials_str = base64.b64decode(encoded_credentials).decode('utf-8')
                
                # Parse the JSON string into a Python dictionary
                service_account_dict = json.loads(json_credentials_str)
                
                # Create the credential object
                cred = credentials.Certificate(service_account_dict)
                
            except (base64.binascii.Error, json.JSONDecodeError) as e:
                # Catch potential errors during decoding or parsing
                raise ValueError(
                    f"Failed to decode or parse the GOOGLE_APPLICATION_CREDENTIALS_JSON "
                    f"environment variable. Please ensure it is a valid Base64 encoded JSON string. Original error: {e}"
                )
            
            firebase_admin.initialize_app(cred)

        self._db = firestore.client()

    def _run(self, 
             operation: str, 
             collection: str, 
             document_id: Optional[str] = None, 
             data: Optional[Dict[str, Any]] = None,
             query_conditions: Optional[List[Dict[str, Any]]] = None,
             return_objects: bool = False) -> str:
        """
        Execute Firebase operations.

        Args:
            operation: The operation to perform ('create', 'read', 'update', 'delete', 'query')
            collection: The name of the collection
            document_id: The ID of the document (required for create, read, update, delete)
            data: The data to write (required for create, update)
            query_conditions: List of conditions for querying (each condition is a dict with field, operator, value)

        Returns:
            Result of the operation as a string
        """
        try:
            if operation == 'create':
                if not document_id:
                    return "Error: document_id is required for create operation"
                if data is None:
                    return "Error: data is required for create operation"

                doc_ref = self._db.collection(collection).document(document_id)
                doc_ref.set(data)
                return f"Document {document_id} created in collection {collection}"

            elif operation == 'read':
                if not document_id:
                    return "Error: document_id is required for read operation"

                doc_ref = self._db.collection(collection).document(document_id)
                doc = doc_ref.get()
                if doc.exists:
                    return f"Document data: {doc.to_dict()}"
                else:
                    return f"Document {document_id} not found in collection {collection}"

            elif operation == 'update':
                if not document_id:
                    return "Error: document_id is required for update operation"
                if data is None:
                    return "Error: data is required for update operation"

                doc_ref = self._db.collection(collection).document(document_id)
                doc_ref.update(data)
                return f"Document {document_id} updated in collection {collection}"

            elif operation == 'delete':
                if not document_id:
                    return "Error: document_id is required for delete operation"

                doc_ref = self._db.collection(collection).document(document_id)
                doc_ref.delete()
                return f"Document {document_id} deleted from collection {collection}"

            elif operation == 'query':
                collection_ref = self._db.collection(collection)
                all_results = []
                total_count = 0
                
                try:
                    # If no query conditions are provided, get all documents
                    if not query_conditions:
                        # First, just count documents
                        docs = collection_ref.stream()
                        for doc in docs:
                            total_count += 1
                            doc_data = doc.to_dict()
                            if return_objects:
                                # collect full objects for downstream processing
                                to_add = doc_data.copy()
                                to_add['_id'] = doc.id
                                all_results.append(to_add)
                            else:
                                # Only store summary for human-readable output
                                if total_count <= 10:  # Only store details for first 10 docs
                                    summary = {
                                        'title': doc_data.get('title', 'No title'),
                                        'status': doc_data.get('status', 'No status'),
                                        'category': doc_data.get('categoryId', 'No category')
                                    }
                                    all_results.append(f"Document: {summary}")

                        if return_objects:
                            # Return structured JSON array of documents (stringified)
                            try:
                                return json.dumps({
                                    'total': total_count,
                                    'documents': all_results
                                }, default=str)
                            except Exception as e:
                                return f"Error serializing documents: {str(e)}"

                        # Return summary instead of full data
                        summary = [
                            f"Total documents in collection: {total_count}",
                            f"Sample of first 10 documents:",
                            *all_results,
                            "\nTo get specific document details, use the 'read' operation with a document ID."
                        ]
                        return "\n".join(summary)
                    else:
                        query = collection_ref
                        for condition in query_conditions:
                            field = condition.get('field')
                            operator = condition.get('operator', '==')
                            value = condition.get('value')

                            if not field:
                                return "Error: Each query condition must have a 'field'"

                            if operator == '==':
                                query = query.where(field, '==', value)
                            elif operator == '>=':
                                query = query.where(field, '>=', value)
                            elif operator == '<=':
                                query = query.where(field, '<=', value)
                            elif operator == '>':
                                query = query.where(field, '>', value)
                            elif operator == '<':
                                query = query.where(field, '<', value)
                            elif operator == 'array-contains':
                                query = query.where(field, 'array-contains', value)
                            elif operator == 'array-contains-any':
                                query = query.where(field, 'array-contains-any', value)
                            elif operator == 'in':
                                query = query.where(field, 'in', value)
                            else:
                                return f"Error: Unsupported operator {operator}"

                        # Count and get summary of filtered documents
                        docs = query.stream()
                        total_count = 0
                        for doc in docs:
                            total_count += 1
                            doc_data = doc.to_dict()
                            if return_objects:
                                to_add = doc_data.copy()
                                to_add['_id'] = doc.id
                                all_results.append(to_add)
                            else:
                                if total_count <= 10:
                                    summary = {
                                        'title': doc_data.get('title', 'No title'),
                                        'status': doc_data.get('status', 'No status'),
                                        'category': doc_data.get('categoryId', 'No category')
                                    }
                                    all_results.append(f"Document: {summary}")

                        if return_objects:
                            try:
                                return json.dumps({
                                    'total': total_count,
                                    'documents': all_results
                                }, default=str)
                            except Exception as e:
                                return f"Error serializing documents: {str(e)}"

                        summary = [
                            f"Total documents matching query: {total_count}",
                            f"Sample of first 10 matching documents:",
                            *all_results,
                            "\nTo get specific document details, use the 'read' operation with a document ID."
                        ]
                        return "\n".join(summary)
                        
                except Exception as e:
                    return f"Error during query: {str(e)}"

            else:
                return f"Error: Unsupported operation {operation}. Supported operations are: create, read, update, delete, query"

        except Exception as e:
            return f"Error executing Firebase operation: {str(e)}"