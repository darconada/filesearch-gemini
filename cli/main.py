#!/usr/bin/env python3
"""
File Search CLI - Command-line interface for File Search RAG

This CLI provides a simple interface to interact with the File Search backend,
making it easy for LLM agents (Gemini CLI, Claude Code, Codex) and humans
to use File Search operations from the command line.
"""

import click
import httpx
import json
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint

from cli.config import config

console = Console()


def get_client() -> httpx.Client:
    """Get HTTP client for backend API"""
    return httpx.Client(base_url=config.backend_url, timeout=60.0)


def handle_error(e: Exception, operation: str) -> None:
    """Handle and display errors consistently"""
    console.print(f"[red]Error {operation}:[/red] {str(e)}")


# ============================================================================
# MAIN CLI GROUP
# ============================================================================

@click.group()
@click.version_option(version="2.0.0")
def cli():
    """
    File Search CLI - Manage Google File Search and RAG queries

    A command-line interface for the File Search RAG application,
    compatible with LLM agents and human users.
    """
    pass


# ============================================================================
# CONFIG COMMANDS
# ============================================================================

@cli.group()
def config_cmd():
    """Manage configuration (API key, backend URL)"""
    pass


@config_cmd.command("set-api-key")
@click.argument("api_key")
def set_api_key(api_key: str):
    """Set the Google API key"""
    try:
        with get_client() as client:
            response = client.post("/config/api-key", json={"api_key": api_key})
            response.raise_for_status()
            result = response.json()

        config.api_key = api_key
        console.print("[green]✓[/green] API key configured successfully")

        if result.get("valid"):
            console.print("[green]✓[/green] API key validated")
        else:
            console.print("[yellow]⚠[/yellow] API key may be invalid")

    except Exception as e:
        handle_error(e, "setting API key")


@config_cmd.command("status")
def config_status():
    """Show configuration status"""
    try:
        with get_client() as client:
            response = client.get("/config/status")
            response.raise_for_status()
            result = response.json()

        table = Table(title="Configuration Status")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Backend URL", config.backend_url)
        table.add_row("API Key Valid", "Yes" if result.get("valid") else "No")
        table.add_row("Config File", str(config.config_file))

        console.print(table)

    except Exception as e:
        handle_error(e, "getting config status")


@config_cmd.command("set-backend")
@click.argument("url")
def set_backend(url: str):
    """Set the backend URL (default: http://localhost:8000)"""
    config.backend_url = url
    console.print(f"[green]✓[/green] Backend URL set to: {url}")


# ============================================================================
# STORE COMMANDS
# ============================================================================

@cli.group()
def stores():
    """Manage File Search stores"""
    pass


@stores.command("list")
def list_stores():
    """List all stores"""
    try:
        with get_client() as client:
            response = client.get("/stores")
            response.raise_for_status()
            result = response.json()

        stores_list = result.get("stores", [])

        if not stores_list:
            console.print("[yellow]No stores found[/yellow]")
            return

        table = Table(title=f"File Search Stores ({len(stores_list)})")
        table.add_column("Name", style="cyan")
        table.add_column("Store ID", style="green")
        table.add_column("Created", style="yellow")

        for store in stores_list:
            table.add_row(
                store.get("display_name", "N/A"),
                store.get("name", "N/A"),
                store.get("create_time", "N/A")[:19] if store.get("create_time") else "N/A"
            )

        console.print(table)

    except Exception as e:
        handle_error(e, "listing stores")


@stores.command("create")
@click.option("--name", required=True, help="Display name for the store")
def create_store(name: str):
    """Create a new store"""
    try:
        with get_client() as client:
            response = client.post("/stores", json={"display_name": name})
            response.raise_for_status()
            result = response.json()

        console.print(Panel(
            f"[green]✓[/green] Store created successfully\n\n"
            f"Name: {result.get('display_name')}\n"
            f"ID: {result.get('name')}",
            title="Store Created"
        ))

    except Exception as e:
        handle_error(e, "creating store")


@stores.command("get")
@click.argument("store_id")
def get_store(store_id: str):
    """Get store details"""
    try:
        with get_client() as client:
            response = client.get(f"/stores/{store_id}")
            response.raise_for_status()
            result = response.json()

        console.print(Panel(
            f"Name: {result.get('display_name')}\n"
            f"ID: {result.get('name')}\n"
            f"Created: {result.get('create_time', 'N/A')}\n"
            f"Updated: {result.get('update_time', 'N/A')}",
            title="Store Details"
        ))

    except Exception as e:
        handle_error(e, "getting store")


@stores.command("delete")
@click.argument("store_id")
@click.option("--force", is_flag=True, help="Force deletion even if documents are indexed")
def delete_store(store_id: str, force: bool):
    """Delete a store"""
    try:
        with get_client() as client:
            params = {"force": str(force).lower()}
            response = client.delete(f"/stores/{store_id}", params=params)
            response.raise_for_status()

        console.print(f"[green]✓[/green] Store {store_id} deleted successfully")

    except Exception as e:
        handle_error(e, "deleting store")


# ============================================================================
# DOCUMENT COMMANDS
# ============================================================================

@cli.group()
def docs():
    """Manage documents in stores"""
    pass


@docs.command("list")
@click.option("--store-id", required=True, help="Store ID to list documents from")
@click.option("--metadata-filter", help="Metadata filter (e.g., 'author=\"John\"')")
@click.option("--page-size", default=50, help="Number of documents per page")
def list_docs(store_id: str, metadata_filter: Optional[str], page_size: int):
    """List documents in a store"""
    try:
        with get_client() as client:
            params = {"page_size": page_size}
            if metadata_filter:
                params["metadata_filter"] = metadata_filter

            response = client.get(f"/stores/{store_id}/documents", params=params)
            response.raise_for_status()
            result = response.json()

        docs_list = result.get("documents", [])

        if not docs_list:
            console.print("[yellow]No documents found[/yellow]")
            return

        table = Table(title=f"Documents in Store ({len(docs_list)})")
        table.add_column("Name", style="cyan")
        table.add_column("Document ID", style="green")
        table.add_column("State", style="yellow")
        table.add_column("Metadata", style="magenta")

        for doc in docs_list:
            metadata = doc.get("custom_metadata", {})
            metadata_str = json.dumps(metadata) if metadata else "-"
            table.add_row(
                doc.get("display_name", "N/A"),
                doc.get("name", "N/A"),
                doc.get("state", "N/A"),
                metadata_str[:50] + "..." if len(metadata_str) > 50 else metadata_str
            )

        console.print(table)

    except Exception as e:
        handle_error(e, "listing documents")


@docs.command("upload")
@click.option("--store-id", required=True, help="Target store ID")
@click.option("--file", "file_path", required=True, type=click.Path(exists=True), help="Path to file")
@click.option("--name", help="Display name for the document")
@click.option("--metadata", help="Metadata as JSON string (e.g., '{\"author\":\"John\"}')")
def upload_doc(store_id: str, file_path: str, name: Optional[str], metadata: Optional[str]):
    """Upload a document to a store"""
    try:
        file_obj = Path(file_path)

        with get_client() as client:
            files = {"file": (file_obj.name, open(file_obj, "rb"))}
            data = {}

            if name:
                data["display_name"] = name
            if metadata:
                data["metadata"] = metadata

            response = client.post(
                f"/stores/{store_id}/documents",
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()

        console.print(Panel(
            f"[green]✓[/green] Document uploaded successfully\n\n"
            f"Name: {result.get('display_name')}\n"
            f"ID: {result.get('name')}\n"
            f"State: {result.get('state', 'PROCESSING')}",
            title="Document Uploaded"
        ))

    except Exception as e:
        handle_error(e, "uploading document")


@docs.command("delete")
@click.option("--store-id", required=True, help="Store ID")
@click.option("--doc-id", required=True, help="Document ID")
@click.option("--force", is_flag=True, help="Force deletion even if indexed")
def delete_doc(store_id: str, doc_id: str, force: bool):
    """Delete a document from a store"""
    try:
        with get_client() as client:
            params = {"force": str(force).lower()}
            response = client.delete(
                f"/stores/{store_id}/documents/{doc_id}",
                params=params
            )
            response.raise_for_status()

        console.print(f"[green]✓[/green] Document {doc_id} deleted successfully")

    except Exception as e:
        handle_error(e, "deleting document")


# ============================================================================
# QUERY COMMAND
# ============================================================================

@cli.command()
@click.option("--question", required=True, help="Question to ask")
@click.option("--stores", required=True, help="Comma-separated store IDs")
@click.option("--metadata-filter", help="Metadata filter (e.g., 'author=\"John\"')")
@click.option("--max-tokens", type=int, help="Maximum output tokens")
@click.option("--temperature", type=float, help="Temperature (0.0-1.0)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def query(
    question: str,
    stores: str,
    metadata_filter: Optional[str],
    max_tokens: Optional[int],
    temperature: Optional[float],
    output_json: bool
):
    """Execute a RAG query"""
    try:
        store_ids = [s.strip() for s in stores.split(",")]

        payload = {
            "question": question,
            "store_ids": store_ids
        }

        if metadata_filter:
            payload["metadata_filter"] = metadata_filter
        if max_tokens:
            payload["max_output_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature

        with get_client() as client:
            response = client.post("/query", json=payload)
            response.raise_for_status()
            result = response.json()

        if output_json:
            console.print_json(data=result)
            return

        # Display formatted result
        console.print(Panel(
            result.get("answer", "No answer"),
            title=f"Answer (Model: {result.get('model_used', 'N/A')})",
            border_style="green"
        ))

        sources = result.get("sources", [])
        if sources:
            console.print("\n[bold]Sources:[/bold]")
            for i, source in enumerate(sources, 1):
                metadata = source.get("metadata", {})
                metadata_str = ", ".join(f"{k}={v}" for k, v in metadata.items()) if metadata else "No metadata"

                console.print(f"\n{i}. [cyan]{source.get('document_display_name', 'Unknown')}[/cyan]")
                console.print(f"   ID: {source.get('document_id', 'N/A')}")
                console.print(f"   Metadata: {metadata_str}")
                if source.get("chunk_text"):
                    console.print(f"   Excerpt: {source['chunk_text'][:150]}...")

    except Exception as e:
        handle_error(e, "executing query")


# ============================================================================
# DRIVE LINK COMMANDS
# ============================================================================

@cli.group()
def drive():
    """Manage Google Drive sync links"""
    pass


@drive.command("list")
def list_drive_links():
    """List all Drive sync links"""
    try:
        with get_client() as client:
            response = client.get("/drive-links")
            response.raise_for_status()
            result = response.json()

        links = result.get("links", [])

        if not links:
            console.print("[yellow]No Drive links found[/yellow]")
            return

        table = Table(title=f"Google Drive Sync Links ({len(links)})")
        table.add_column("ID", style="cyan")
        table.add_column("Drive File ID", style="green")
        table.add_column("Store ID", style="yellow")
        table.add_column("Mode", style="magenta")

        for link in links:
            table.add_row(
                str(link.get("id", "N/A")),
                link.get("drive_file_id", "N/A"),
                link.get("store_id", "N/A"),
                link.get("mode", "N/A")
            )

        console.print(table)

    except Exception as e:
        handle_error(e, "listing drive links")


@drive.command("create")
@click.option("--drive-id", required=True, help="Google Drive file/folder ID")
@click.option("--store-id", required=True, help="Target store ID")
@click.option("--mode", type=click.Choice(["manual", "auto"]), default="manual", help="Sync mode")
@click.option("--description", help="Description for this link")
def create_drive_link(drive_id: str, store_id: str, mode: str, description: Optional[str]):
    """Create a Drive sync link"""
    try:
        payload = {
            "drive_file_id": drive_id,
            "store_id": store_id,
            "mode": mode
        }

        if description:
            payload["description"] = description

        with get_client() as client:
            response = client.post("/drive-links", json=payload)
            response.raise_for_status()
            result = response.json()

        console.print(Panel(
            f"[green]✓[/green] Drive link created successfully\n\n"
            f"Link ID: {result.get('id')}\n"
            f"Drive File ID: {result.get('drive_file_id')}\n"
            f"Store ID: {result.get('store_id')}\n"
            f"Mode: {result.get('mode')}",
            title="Drive Link Created"
        ))

    except Exception as e:
        handle_error(e, "creating drive link")


@drive.command("sync-now")
@click.argument("link_id")
def sync_now(link_id: str):
    """Manually trigger sync for a Drive link"""
    try:
        with get_client() as client:
            response = client.post(f"/drive-links/{link_id}/sync-now")
            response.raise_for_status()
            result = response.json()

        console.print(f"[green]✓[/green] Sync completed: {result.get('message', 'Success')}")

    except Exception as e:
        handle_error(e, "syncing drive link")


@drive.command("delete")
@click.argument("link_id")
def delete_drive_link(link_id: str):
    """Delete a Drive sync link"""
    try:
        with get_client() as client:
            response = client.delete(f"/drive-links/{link_id}")
            response.raise_for_status()

        console.print(f"[green]✓[/green] Drive link {link_id} deleted successfully")

    except Exception as e:
        handle_error(e, "deleting drive link")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    cli()
