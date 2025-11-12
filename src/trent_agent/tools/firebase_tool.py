import base64
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from google.cloud import firestore
from google.oauth2 import service_account
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr


class QueryCondition(BaseModel):
    field: str
    operator: str = "=="
    value: Any


class FirebaseToolInput(BaseModel):
    operation: Literal["read", "query"] = Field(
        description="Operation to perform. Only 'read' and 'query' are supported."
    )
    collection: str = Field(description="Name of the collection to access")
    document_id: Optional[str] = Field(
        None,
        description="Document ID. Required for 'read' operations."
    )
    query_conditions: Optional[List[QueryCondition]] = Field(
        None,
        description="Conditions to apply when performing a query operation."
    )
    return_objects: bool = Field(
        default=False,
        description="When true, return raw JSON documents instead of a human-readable summary."
    )


class FirebaseReadOnlyTool(BaseTool):
    """Read/query helper backed by the Firestore client SDK with snapshot caching."""

    name: str = "Firebase Read-Only Tool"
    description: str = (
        "Read documents from Firestore using the Google Cloud client library. "
        "Supports real-time snapshot caching to avoid re-reading full collections."
    )
    args_schema: type[BaseModel] = FirebaseToolInput

    _db: Any = PrivateAttr(default=None)
    _collection_cache: Dict[str, Dict[str, Any]] = PrivateAttr(default_factory=dict)

    def __init__(self):
        super().__init__()
        self._collection_cache = {}
        self._initialize_firestore_client()

    # ------------------------------------------------------------------
    # Firestore bootstrap & helpers
    # ------------------------------------------------------------------
    def _initialize_firestore_client(self) -> None:
        encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not encoded_credentials:
            raise ValueError(
                "Missing FIREBASE credentials. Set GOOGLE_APPLICATION_CREDENTIALS_JSON "
                "to a Base64 encoded service-account JSON."
            )

        try:
            json_credentials_str = base64.b64decode(encoded_credentials).decode("utf-8")
            service_account_dict = json.loads(json_credentials_str)
        except (base64.binascii.Error, json.JSONDecodeError) as exc:
            raise ValueError(
                "Failed to decode GOOGLE_APPLICATION_CREDENTIALS_JSON; ensure it is a "
                "valid Base64-encoded JSON string."
            ) from exc

        try:
            credentials_obj = service_account.Credentials.from_service_account_info(
                service_account_dict
            )
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(f"Failed to construct service account credentials: {exc}")

        project_id = service_account_dict.get("project_id")
        if not project_id:
            raise ValueError("Service account JSON must include 'project_id'.")

        self._db = firestore.Client(project=project_id, credentials=credentials_obj)

    def _normalize_timestamp(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if hasattr(value, "ToDatetime"):
            return value.ToDatetime()
        if hasattr(value, "to_datetime"):
            return value.to_datetime()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return None

    def _update_cache_entry(
        self,
        collection: str,
        doc_id: str,
        doc_data: Dict[str, Any],
        last_update_value: Any,
    ) -> None:
        cache_entry = self._collection_cache.setdefault(
            collection,
            {
                "documents": {},
                "last_update": None,
                "unsubscribe": None,
                "ready": False,
            },
        )

        cache_entry["documents"][doc_id] = doc_data

        normalized_last_update = self._normalize_timestamp(last_update_value)
        if normalized_last_update is None:
            return

        current_last_update = cache_entry.get("last_update")
        try:
            if current_last_update is None or normalized_last_update > current_last_update:
                cache_entry["last_update"] = normalized_last_update
        except TypeError:
            cache_entry["last_update"] = normalized_last_update

    def _ensure_collection_listener(self, collection: str) -> Dict[str, Any]:
        collection_ref = self._db.collection(collection)
        cache_entry = self._collection_cache.setdefault(
            collection,
            {
                "documents": {},
                "last_update": None,
                "unsubscribe": None,
                "ready": False,
                "listener_error": False,
            },
        )

        if cache_entry.get("unsubscribe") is None and not cache_entry.get("listener_error"):
            try:
                # Define the callback function for on_snapshot (built-in method from google.cloud.firestore)
                def snapshot_callback(collection_snapshot, changes, read_time):
                    """
                    Callback function for collection_ref.on_snapshot().
                    Handles document changes: ADDED, MODIFIED, REMOVED.
                    Similar to JS Firebase: snapshot.docChanges().forEach((change) => { ... })
                    """
                    entry = self._collection_cache.setdefault(
                        collection,
                        {
                            "documents": {},
                            "last_update": None,
                            "unsubscribe": None,
                            "ready": False,
                            "listener_error": False,
                        },
                    )

                    # Handle document changes (added, modified, removed)
                    if changes:
                        for change in changes:
                            doc = change.document
                            change_type = change.type.name  # ADDED, MODIFIED, or REMOVED
                            
                            if change_type == "REMOVED":
                                # Handle removed documents
                                entry["documents"].pop(doc.id, None)
                            elif change_type == "ADDED":
                                # Handle new documents
                                doc_data = doc.to_dict()
                                last_update_field = doc_data.get("lastUpdate", getattr(doc, "update_time", None))
                                self._update_cache_entry(collection, doc.id, doc_data, last_update_field)
                            elif change_type == "MODIFIED":
                                # Handle modified documents
                                doc_data = doc.to_dict()
                                last_update_field = doc_data.get("lastUpdate", getattr(doc, "update_time", None))
                                self._update_cache_entry(collection, doc.id, doc_data, last_update_field)
                    else:
                        # Initial snapshot - populate all documents
                        for doc in collection_snapshot:
                            doc_data = doc.to_dict()
                            last_update_field = doc_data.get("lastUpdate", getattr(doc, "update_time", None))
                            self._update_cache_entry(collection, doc.id, doc_data, last_update_field)

                    entry["ready"] = True

                # Use the built-in on_snapshot method from google.cloud.firestore
                # This sets up a real-time listener for the collection
                cache_entry["unsubscribe"] = collection_ref.on_snapshot(snapshot_callback)
            except AttributeError:
                cache_entry["listener_error"] = True
            except Exception:
                cache_entry["listener_error"] = True

        if not cache_entry.get("ready"):
            try:
                docs = list(collection_ref.stream())
                for doc in docs:
                    doc_data = doc.to_dict()
                    last_update_field = doc_data.get("lastUpdate", getattr(doc, "update_time", None))
                    self._update_cache_entry(collection, doc.id, doc_data, last_update_field)
                cache_entry["ready"] = True
            except Exception:
                cache_entry["listener_error"] = True

        return cache_entry

    def _perform_remote_query(
        self,
        collection_ref: Any,
        collection: str,
        query_conditions: Optional[List[QueryCondition]],
        return_objects: bool,
    ) -> str:
        query = collection_ref
        for condition in query_conditions or []:
            field = condition.field
            operator = condition.operator
            value = condition.value

            if not field:
                return "Error: Each query condition must include a field."

            if operator == "==":
                query = query.where(field, "==", value)
            elif operator == ">=":
                query = query.where(field, ">=", value)
            elif operator == "<=":
                query = query.where(field, "<=", value)
            elif operator == ">":
                query = query.where(field, ">", value)
            elif operator == "<":
                query = query.where(field, "<", value)
            elif operator == "array-contains":
                query = query.where(field, "array-contains", value)
            elif operator == "array-contains-any":
                query = query.where(field, "array-contains-any", value)
            elif operator == "in":
                query = query.where(field, "in", value)
            else:
                return f"Error: Unsupported operator '{operator}'."

        try:
            docs = list(query.stream())
        except Exception as exc:  # pragma: no cover - remote errors are surfaced to user
            return f"Error during query: {exc}"

        results: List[Any] = []
        total_count = 0
        for doc in docs:
            total_count += 1
            doc_data = doc.to_dict()
            last_update_field = doc_data.get("lastUpdate", getattr(doc, "update_time", None))
            self._update_cache_entry(collection, doc.id, doc_data, last_update_field)
            if return_objects:
                payload = doc_data.copy()
                payload["_id"] = doc.id
                results.append(payload)
            elif total_count <= 10:
                results.append(
                    f"Document: {{'title': {doc_data.get('title', 'No title')}, "
                    f"'status': {doc_data.get('status', 'No status')}, "
                    f"'category': {doc_data.get('category', 'No category')}}}"
                )

        if return_objects:
            try:
                return json.dumps({"total": total_count, "documents": results}, default=str)
            except Exception as exc:
                return f"Error serializing documents: {exc}"

        summary_lines = [
            f"Total documents matching query: {total_count}",
            "Sample of first 10 matching documents:",
            *results,
            "\nTo get specific document details, use the 'read' operation with a document ID.",
        ]
        return "\n".join(summary_lines)

    # ------------------------------------------------------------------
    # BaseTool hook
    # ------------------------------------------------------------------
    def _run(
        self,
        operation: str,
        collection: str,
        document_id: Optional[str] = None,
        query_conditions: Optional[List[Dict[str, Any]]] = None,
        return_objects: bool = False,
    ) -> str:
        try:
            if operation == "read":
                if not document_id:
                    return "Error: document_id is required for read operation."

                doc_ref = self._db.collection(collection).document(document_id)
                doc_snapshot = doc_ref.get()
                if doc_snapshot.exists:
                    doc_data = doc_snapshot.to_dict()
                    last_update_field = doc_data.get("lastUpdate", getattr(doc_snapshot, "update_time", None))
                    self._update_cache_entry(collection, doc_snapshot.id, doc_data, last_update_field)
                    return f"Document data: {doc_data}"
                return f"Document {document_id} not found in collection {collection}."

            if operation == "query":
                collection_ref = self._db.collection(collection)
                cache_entry = self._ensure_collection_listener(collection)

                if not query_conditions:
                    documents = cache_entry.get("documents", {})
                    total_count = len(documents)

                    if return_objects:
                        payload = []
                        for doc_id, doc_data in documents.items():
                            item = doc_data.copy()
                            item["_id"] = doc_id
                            payload.append(item)
                        try:
                            return json.dumps({"total": total_count, "documents": payload}, default=str)
                        except Exception as exc:
                            return f"Error serializing documents: {exc}"

                    summaries: List[str] = []
                    for idx, doc_data in enumerate(documents.values(), start=1):
                        if idx > 10:
                            break
                        summaries.append(
                            f"Document: {{'title': {doc_data.get('title', 'No title')}, "
                            f"'status': {doc_data.get('status', 'No status')}, "
                            f"'category': {doc_data.get('category', 'No category')}}}"
                        )

                    lines = [
                        f"Total documents in collection: {total_count}",
                        "Sample of first 10 documents:",
                        *summaries,
                        "\nTo get specific document details, use the 'read' operation with a document ID.",
                    ]
                    return "\n".join(lines)

                # Convert condition dicts to QueryCondition models
                parsed_conditions = [
                    QueryCondition(**condition) if not isinstance(condition, QueryCondition) else condition
                    for condition in query_conditions
                ]

                if cache_entry.get("ready") and not cache_entry.get("listener_error"):
                    documents = cache_entry.get("documents", {})
                    matching_docs: List[Dict[str, Any]] = []
                    unsupported_operator = False

                    for doc_id, doc_data in documents.items():
                        matches = True
                        for condition in parsed_conditions:
                            doc_value = doc_data.get(condition.field)

                            if condition.operator == "==":
                                if doc_value != condition.value:
                                    matches = False
                                    break
                            else:
                                unsupported_operator = True
                                break

                        if unsupported_operator:
                            break

                        if matches:
                            payload = doc_data.copy()
                            payload["_id"] = doc_id
                            matching_docs.append(payload)

                    if not unsupported_operator:
                        total_count = len(matching_docs)

                        if return_objects:
                            try:
                                return json.dumps(
                                    {"total": total_count, "documents": matching_docs}, default=str
                                )
                            except Exception as exc:
                                return f"Error serializing documents: {exc}"

                        summaries = []
                        for idx, doc_data in enumerate(matching_docs, start=1):
                            if idx > 10:
                                break
                            summaries.append(
                                f"Document: {{'title': {doc_data.get('title', 'No title')}, "
                                f"'status': {doc_data.get('status', 'No status')}, "
                                f"'category': {doc_data.get('category', 'No category')}}}"
                            )

                        lines = [
                            f"Total documents matching query: {total_count}",
                            "Sample of first 10 matching documents:",
                            *summaries,
                            "\nTo get specific document details, use the 'read' operation with a document ID.",
                        ]
                        return "\n".join(lines)

                # Fall back to remote filtering if local cache can't handle it
                return self._perform_remote_query(collection_ref, collection, parsed_conditions, return_objects)

            return ("Error: Unsupported operation. Only 'read' and 'query' are allowed.")

        except Exception as exc:  # pragma: no cover - defensive catch for tool surface
            return f"Error executing Firebase operation: {exc}"
