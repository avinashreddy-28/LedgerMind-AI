"""
rag_ingest.py — Knowledge Base Ingestion for LedgerMind AI
===========================================================
Ingests finance and policy documents into a local ChromaDB vector store.

Logic:
1. Initialize a persistent ChromaDB client pointing to "./chroma_db".
2. Create or retrieve the "finance_docs" collection.
3. Read all .txt policy files from the "docs/knowledge/" directory.
4. Split each document into chunks based on double newlines (paragraphs).
5. Ingest each chunk into the ChromaDB collection with unique IDs and metadata.
6. Report summary statistics on ingested chunks per file.
"""

import os
import sys
import chromadb
from chromadb.config import Settings

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# Resolve project root directory dynamically
project_root = os.path.dirname(os.path.abspath(__file__))
docs_dir = os.path.join(project_root, "docs", "knowledge")
chroma_dir = os.path.join(project_root, "chroma_db")


def ingest_documents():
    """
    Reads .txt documents from docs/knowledge/, chunks them,
    and stores them in the ChromaDB collection 'finance_docs'.
    """
    print("=" * 60)
    print("  LedgerMind AI — RAG Knowledge Ingestion")
    print("=" * 60)

    # -----------------------------------------------------------------------
    # Step 1: Initialize ChromaDB PersistentClient
    # -----------------------------------------------------------------------
    # PersistentClient persists vector embeddings to disk at the specified path
    # so they remain available across application restarts.
    print(f"\n📁 Initializing ChromaDB at: {chroma_dir}")
    client = chromadb.PersistentClient(path=chroma_dir)

    # -----------------------------------------------------------------------
    # Step 2: Create or get the collection
    # -----------------------------------------------------------------------
    # Using get_or_create_collection with ChromaDB's default embedding function
    # (all-MiniLM-L6-v2 by default).
    collection_name = "finance_docs"
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Financial policies and operations manuals"}
    )
    print(f"✅ Collection '{collection_name}' ready.")

    # -----------------------------------------------------------------------
    # Step 3: Check and read files from docs/knowledge/
    # -----------------------------------------------------------------------
    if not os.path.exists(docs_dir):
        print(f"❌ Knowledge directory not found: {docs_dir}")
        return

    txt_files = [f for f in os.listdir(docs_dir) if f.endswith(".txt")]
    if not txt_files:
        print(f"⚠️  No .txt files found in {docs_dir}")
        return

    print(f"\n📄 Found {len(txt_files)} document(s) in {docs_dir}:")
    for f in txt_files:
        print(f"   - {f}")

    total_chunks_ingested = 0

    # -----------------------------------------------------------------------
    # Step 4 & 5: Process each file, split into chunks, and ingest to ChromaDB
    # -----------------------------------------------------------------------
    for filename in txt_files:
        file_path = os.path.join(docs_dir, filename)

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Split document by paragraphs (double newlines)
        raw_chunks = content.split("\n\n")

        # Strip whitespace and ignore empty paragraphs
        chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]

        if not chunks:
            print(f"\n⚠️  Skipping empty file: {filename}")
            continue

        # Prepare lists for batch ingestion into ChromaDB
        ids = []
        documents = []
        metadatas = []

        base_name = os.path.splitext(filename)[0]

        for idx, chunk in enumerate(chunks):
            # Unique ID for each chunk (e.g., settlement_policy_chunk_0)
            chunk_id = f"{base_name}_chunk_{idx}"
            ids.append(chunk_id)
            documents.append(chunk)
            # Store source filename in metadata
            metadatas.append({"source": filename})

        # Upsert chunks into collection (adds new chunks or updates existing ones)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        total_chunks_ingested += len(chunks)
        print(f"\n📥 Ingested '{filename}': {len(chunks)} chunk(s)")
        for i, doc in enumerate(documents):
            first_line = doc.split("\n")[0]
            print(f"   [{ids[i]}] {first_line[:50]}...")

    # -----------------------------------------------------------------------
    # Step 6: Ingestion Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"🎉 Ingestion complete! Total chunks in collection '{collection_name}': {collection.count()}")
    print("=" * 60)


if __name__ == "__main__":
    ingest_documents()
