SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS textbooks (
        textbook_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        title TEXT NOT NULL,
        file_format TEXT NOT NULL,
        file_size INTEGER NOT NULL DEFAULT 0,
        saved_path TEXT NOT NULL,
        parse_status TEXT NOT NULL DEFAULT 'pending',
        total_pages INTEGER NOT NULL DEFAULT 0,
        total_chars INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chapters (
        chapter_id TEXT PRIMARY KEY,
        textbook_id TEXT NOT NULL,
        title TEXT NOT NULL,
        order_index INTEGER NOT NULL,
        page_start INTEGER,
        page_end INTEGER,
        content TEXT NOT NULL,
        char_count INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY (textbook_id) REFERENCES textbooks(textbook_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS graph_nodes (
        node_id TEXT PRIMARY KEY,
        textbook_id TEXT NOT NULL,
        chapter_id TEXT,
        name TEXT NOT NULL,
        definition TEXT NOT NULL,
        category TEXT NOT NULL,
        page INTEGER,
        source_excerpt TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (textbook_id) REFERENCES textbooks(textbook_id) ON DELETE CASCADE,
        FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS graph_edges (
        edge_id TEXT PRIMARY KEY,
        textbook_id TEXT NOT NULL,
        source_node_id TEXT NOT NULL,
        target_node_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (textbook_id) REFERENCES textbooks(textbook_id) ON DELETE CASCADE,
        FOREIGN KEY (source_node_id) REFERENCES graph_nodes(node_id) ON DELETE CASCADE,
        FOREIGN KEY (target_node_id) REFERENCES graph_nodes(node_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS integration_decisions (
        decision_id TEXT PRIMARY KEY,
        action TEXT NOT NULL,
        affected_node_ids TEXT NOT NULL,
        result_node_id TEXT,
        reason TEXT NOT NULL,
        confidence REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS merged_nodes (
        merged_node_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        definition TEXT NOT NULL,
        source_node_ids TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rag_chunks (
        chunk_id TEXT PRIMARY KEY,
        textbook_id TEXT NOT NULL,
        chapter_id TEXT,
        chunk_index INTEGER NOT NULL,
        text TEXT NOT NULL,
        page_start INTEGER,
        page_end INTEGER,
        token_count INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY (textbook_id) REFERENCES textbooks(textbook_id) ON DELETE CASCADE,
        FOREIGN KEY (chapter_id) REFERENCES chapters(chapter_id) ON DELETE SET NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_sessions (
        session_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS chat_messages (
        message_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        task_type TEXT NOT NULL,
        status TEXT NOT NULL,
        progress INTEGER NOT NULL DEFAULT 0,
        error_message TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
]
