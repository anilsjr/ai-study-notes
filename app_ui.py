from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import streamlit as st


API_BASE_URL = os.getenv("AI_STUDY_API_BASE_URL", "http://localhost:8000").rstrip("/")
API_PREFIX = os.getenv("AI_STUDY_API_PREFIX", "/api/v1").strip()
API_PREFIX = API_PREFIX if API_PREFIX.startswith("/") else f"/{API_PREFIX}"
REQUEST_TIMEOUT_SECONDS = int(os.getenv("AI_STUDY_API_TIMEOUT_SECONDS", "180"))
REGISTRY_PATH = Path(
    os.getenv(
        "AI_STUDY_COLLECTION_REGISTRY",
        str(Path(__file__).with_name(".streamlit_collections.json")),
    )
)


st.set_page_config(
    page_title="AI Study Notes",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


class BackendAPIError(RuntimeError):
    """Raised when the Streamlit client cannot complete a backend request."""


def api_url(path: str, *, include_prefix: bool = True) -> str:
    clean_path = path if path.startswith("/") else f"/{path}"
    if include_prefix and not clean_path.startswith(API_PREFIX):
        clean_path = f"{API_PREFIX}{clean_path}"
    return f"{API_BASE_URL}{clean_path}"


def extract_error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text.strip() or response.reason or "Unknown backend error"

    if isinstance(payload, dict):
        detail = payload.get("detail") or payload.get("message") or payload
        if isinstance(detail, (dict, list)):
            return json.dumps(detail, indent=2)
        return str(detail)

    return str(payload)


def request_json(
    method: str,
    path: str,
    *,
    include_prefix: bool = True,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
    **kwargs: Any,
) -> dict[str, Any]:
    try:
        response = requests.request(
            method,
            api_url(path, include_prefix=include_prefix),
            timeout=timeout,
            **kwargs,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise BackendAPIError(
            f"Could not connect to the backend at {API_BASE_URL}. "
            "Start the FastAPI server and try again."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise BackendAPIError(
            "The backend request timed out. Large files or generation tasks may need more time."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise BackendAPIError(
            f"Backend returned {response.status_code}: {extract_error_detail(response)}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise BackendAPIError(f"Backend request failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise BackendAPIError("Backend returned a non-JSON response.") from exc

    if not isinstance(payload, dict):
        raise BackendAPIError("Backend returned an unexpected response shape.")

    return payload


@st.cache_data(ttl=15, show_spinner=False)
def check_backend_health() -> tuple[bool, str]:
    try:
        payload = request_json("GET", "/health", include_prefix=False, timeout=5)
    except BackendAPIError as exc:
        return False, str(exc)

    status = payload.get("status", "unknown")
    return status == "healthy", f"Backend status: {status}"


def upload_document(uploaded_file: Any) -> dict[str, Any]:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }
    return request_json("POST", "/upload", files=files)


def generate_study_pack(collection_id: str) -> dict[str, Any]:
    return request_json(
        "POST",
        "/notes/generate",
        params={"collection_id": collection_id},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )


def ask_study_agent(collection_id: str, query: str) -> str:
    payload = request_json(
        "POST",
        "/rag/ask",
        params={"collection_id": collection_id, "query": query},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    return str(payload.get("answer", "")).strip() or "No answer was returned."


def load_collection_registry() -> list[dict[str, Any]]:
    if not REGISTRY_PATH.exists():
        return []

    try:
        payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(payload, list):
        return []

    collections: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict) and item.get("collection_id"):
            collections.append(item)
    return collections


def save_collection_registry(collections: list[dict[str, Any]]) -> None:
    try:
        REGISTRY_PATH.write_text(
            json.dumps(collections, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        st.warning(f"Could not save the local collection registry: {exc}")


def init_session_state() -> None:
    if "collections" not in st.session_state:
        st.session_state.collections = load_collection_registry()

    if "active_collection_id" not in st.session_state:
        st.session_state.active_collection_id = (
            st.session_state.collections[0]["collection_id"]
            if st.session_state.collections
            else None
        )

    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}

    if "study_packs" not in st.session_state:
        st.session_state.study_packs = {}


def upsert_collection(record: dict[str, Any]) -> None:
    collection_id = record["collection_id"]
    collections = st.session_state.collections

    for index, existing in enumerate(collections):
        if existing.get("collection_id") == collection_id:
            collections[index] = {**existing, **record}
            break
    else:
        collections.insert(0, record)

    st.session_state.active_collection_id = collection_id
    save_collection_registry(collections)


def get_collection(collection_id: str | None) -> dict[str, Any] | None:
    if not collection_id:
        return None

    for collection in st.session_state.collections:
        if collection.get("collection_id") == collection_id:
            return collection
    return None


def collection_label(collection_id: str) -> str:
    collection = get_collection(collection_id)
    if not collection:
        return collection_id

    filename = collection.get("filename") or "Untitled material"
    chunks = collection.get("chunks_processed")
    chunk_text = f", {chunks} chunks" if chunks is not None else ""
    return f"{filename} ({collection_id}{chunk_text})"


def active_collection_id() -> str | None:
    collection_id = st.session_state.get("active_collection_id")
    if collection_id and get_collection(collection_id):
        return collection_id
    return None


def format_timestamp(raw_value: str | None) -> str:
    if not raw_value:
        return "-"
    try:
        parsed = datetime.fromisoformat(raw_value)
    except ValueError:
        return raw_value
    return parsed.strftime("%Y-%m-%d %H:%M")


def render_sidebar() -> str:
    st.sidebar.title("AI Study Notes")
    st.sidebar.caption("🤖 **ADK-powered backend**")

    if st.sidebar.button("Refresh backend status", use_container_width=True):
        check_backend_health.clear()

    healthy, status_message = check_backend_health()
    if healthy:
        st.sidebar.success("Backend online (ADK active)")
    else:
        st.sidebar.error("Backend offline")
        st.sidebar.caption(status_message)

    st.sidebar.divider()
    mode = st.sidebar.radio(
        "Mode",
        ["Knowledge Base / Notes Management", "AI Study Assistant"],
    )

    st.sidebar.divider()
    collection_ids = [
        item["collection_id"]
        for item in st.session_state.collections
        if item.get("collection_id")
    ]

    if collection_ids:
        current = active_collection_id()
        selected_index = collection_ids.index(current) if current in collection_ids else 0
        selected = st.sidebar.selectbox(
            "Active collection",
            collection_ids,
            index=selected_index,
            format_func=collection_label,
        )
        st.session_state.active_collection_id = selected
    else:
        st.sidebar.info("No collections indexed from this UI yet.")

    return mode


def render_collection_table() -> None:
    if not st.session_state.collections:
        st.info("Upload a document or add an existing collection ID to get started.")
        return

    rows = []
    for collection in st.session_state.collections:
        rows.append(
            {
                "File": collection.get("filename", "Untitled material"),
                "Collection ID": collection.get("collection_id", "-"),
                "Chunks": collection.get("chunks_processed", "-"),
                "Added": format_timestamp(collection.get("created_at")),
                "Source": collection.get("source", "upload"),
            }
        )

    st.dataframe(rows, hide_index=True, use_container_width=True)


def render_upload_panel() -> None:
    st.subheader("Upload Study Material")
    st.write("Index a PDF, DOCX, or TXT file into the vector database.")

    with st.form("upload_document_form", clear_on_submit=False):
        uploaded_file = st.file_uploader(
            "Choose a study file",
            type=["pdf", "docx", "txt"],
        )
        submitted = st.form_submit_button(
            "Upload and index",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if uploaded_file is None:
        st.warning("Choose a file before submitting.")
        return

    with st.spinner("Processing and indexing document..."):
        try:
            payload = upload_document(uploaded_file)
        except BackendAPIError as exc:
            st.error(str(exc))
            st.toast("Upload failed.")
            return

    collection_id = payload.get("collection_id")
    if not collection_id:
        st.error("The backend did not return a collection ID.")
        return

    record = {
        "collection_id": collection_id,
        "filename": uploaded_file.name,
        "chunks_processed": payload.get("chunks_processed"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "upload",
    }
    upsert_collection(record)
    st.success(
        f"Indexed {uploaded_file.name} as collection `{collection_id}` "
        f"with {payload.get('chunks_processed', 0)} chunks."
    )
    st.toast("Document indexed.")


def render_manual_collection_form() -> None:
    st.subheader("Add Existing Collection")
    st.write("Use this when you already know a Chroma collection ID from the API.")

    with st.form("manual_collection_form", clear_on_submit=True):
        collection_id = st.text_input("Collection ID", placeholder="doc_abc123def456")
        display_name = st.text_input("Display name", placeholder="Physics Chapter 4")
        submitted = st.form_submit_button("Add collection", use_container_width=True)

    if not submitted:
        return

    collection_id = collection_id.strip()
    if not collection_id:
        st.warning("Enter a collection ID before adding it.")
        return

    upsert_collection(
        {
            "collection_id": collection_id,
            "filename": display_name.strip() or "Existing collection",
            "chunks_processed": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "manual",
        }
    )
    st.success(f"Added collection `{collection_id}`.")


def markdown_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return f"```json\n{json.dumps(value, indent=2)}\n```"


def study_pack_to_markdown(study_pack: dict[str, Any]) -> str:
    labels = {
        "summary": "Summary",
        "flashcards": "Flashcards",
        "mcqs": "MCQs",
    }
    sections = []
    for key, label in labels.items():
        if key in study_pack:
            sections.append(f"## {label}\n\n{markdown_value(study_pack[key])}")
    return "\n\n".join(sections) or markdown_value(study_pack)


def render_study_pack(study_pack: dict[str, Any]) -> None:
    st.subheader("Generated Study Pack")

    sections = [
        ("summary", "Summary"),
        ("flashcards", "Flashcards"),
        ("mcqs", "MCQs"),
    ]
    for key, label in sections:
        if key not in study_pack:
            continue
        with st.expander(label, expanded=key == "summary"):
            st.markdown(markdown_value(study_pack[key]))

    unknown_keys = [key for key in study_pack if key not in {item[0] for item in sections}]
    for key in unknown_keys:
        with st.expander(key.replace("_", " ").title()):
            st.markdown(markdown_value(study_pack[key]))


def render_study_pack_panel() -> None:
    st.subheader("Study Pack")
    collection_id = active_collection_id()

    if not collection_id:
        st.info("Select or add a collection before generating a study pack.")
        return

    st.write(f"Active collection: `{collection_id}`")
    if st.button("Generate study pack", type="primary", use_container_width=True):
        with st.spinner("Generating summary, flashcards, and MCQs..."):
            try:
                payload = generate_study_pack(collection_id)
            except BackendAPIError as exc:
                st.error(str(exc))
                st.toast("Generation failed.")
                return

        study_pack = payload.get("study_pack")
        if not isinstance(study_pack, dict):
            st.error("The backend returned an unexpected study pack response.")
            return

        st.session_state.study_packs[collection_id] = study_pack
        st.success("Study pack generated.")

    study_pack = st.session_state.study_packs.get(collection_id)
    if study_pack:
        render_study_pack(study_pack)
        st.download_button(
            "Download study pack as Markdown",
            data=study_pack_to_markdown(study_pack),
            file_name=f"{collection_id}_study_pack.md",
            mime="text/markdown",
            use_container_width=True,
        )


def render_knowledge_base_page() -> None:
    st.title("Knowledge Base / Notes Management")
    st.write("Manage uploaded materials and generate revision assets from indexed notes.")
    st.divider()

    upload_col, manual_col = st.columns(2, gap="large")
    with upload_col:
        render_upload_panel()
    with manual_col:
        render_manual_collection_form()

    st.divider()
    st.subheader("Indexed Collections")
    render_collection_table()

    st.divider()
    render_study_pack_panel()


def chat_key(collection_id: str) -> str:
    return collection_id


def clipped(text: str, limit: int = 900) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def contextual_query(user_prompt: str, messages: list[dict[str, str]]) -> str:
    recent_messages = [
        item for item in messages[-6:] if item.get("role") in {"user", "assistant"}
    ]
    if not recent_messages:
        return user_prompt

    history_lines = []
    for item in recent_messages:
        role = "Student" if item["role"] == "user" else "Assistant"
        history_lines.append(f"{role}: {clipped(item.get('content', ''))}")

    return (
        f"{user_prompt}\n\n"
        "Recent conversation for resolving follow-up references:\n"
        + "\n".join(history_lines)
    )


def render_chat_messages(messages: list[dict[str, str]]) -> None:
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_ai_assistant_page() -> None:
    st.title("AI Study Assistant")
    st.write("Ask questions, request explanations, and review the active collection.")
    st.divider()

    collection_id = active_collection_id()
    if not collection_id:
        st.warning("Upload a document or add a collection ID before opening a study chat.")
        st.chat_input("Select a collection to start chatting", disabled=True)
        return

    collection = get_collection(collection_id) or {}
    st.caption(f"Using `{collection_id}` - {collection.get('filename', 'Untitled material')}")

    history_key = chat_key(collection_id)
    messages = st.session_state.chat_histories.setdefault(history_key, [])

    controls_col, spacer_col = st.columns([1, 3])
    with controls_col:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_histories[history_key] = []
            st.rerun()
    with spacer_col:
        st.empty()

    render_chat_messages(messages)

    prompt = st.chat_input("Ask a question about your notes")
    if not prompt:
        return

    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking through your notes..."):
            try:
                answer = ask_study_agent(
                    collection_id,
                    contextual_query(prompt, messages[:-1]),
                )
            except BackendAPIError as exc:
                st.error(str(exc))
                st.toast("Assistant request failed.")
                return

        st.markdown(answer)

    messages.append({"role": "assistant", "content": answer})


def main() -> None:
    init_session_state()
    mode = render_sidebar()

    if mode == "Knowledge Base / Notes Management":
        render_knowledge_base_page()
    else:
        render_ai_assistant_page()


if __name__ == "__main__":
    main()
