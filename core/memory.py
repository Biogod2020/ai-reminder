import os
import json
import logging
import asyncio
import numpy as np
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SharedMemoryManager")


class SharedMemoryManager:
    """Robust Shared Memory Manager using SQLite for structured facts."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SharedMemoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_url: str = "sqlite:///notion_soul.db"):
        """Initializes the SQLite engine and session maker."""
        if self._initialized:
            return
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.base_url = os.getenv("LOCAL_PROXY_URL", "http://localhost:8888")
        self.password = os.getenv("PROXY_PASSWORD", "123456")
        self._initialized = True
        logger.info("Robust SharedMemoryManager initialized.")

    async def add(
        self, 
        content: str, 
        user_id: str = "default_user", 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Stores a fact in the SQLite user_soul table.
        
        Args:
            content: The fact string to store.
            user_id: Identifier for the user.
            metadata: Optional dict containing 'scope' and 'type'.
        """
        scope = metadata.get("scope", "soul") if metadata else "soul"
        
        # We use a hash of the content as a key for idempotency within a scope
        key_raw = f"{scope}:{content.lower()}"
        key = hashlib.md5(key_raw.encode()).hexdigest()
        
        logger.info(f"Adding memory to SQLite | Scope: {scope} | Content: {content[:50]}...")
        
        try:
            with self.Session() as session:
                # Upsert logic for SQLite
                stmt = text("""
                    INSERT INTO user_soul (key, value, category, updated_at, is_active)
                    VALUES (:key, :value, :category, :updated_at, 1)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        updated_at = excluded.updated_at,
                        is_active = excluded.is_active
                """)
                session.execute(stmt, {
                    "key": key,
                    "value": content,
                    "category": scope,
                    "updated_at": datetime.utcnow()
                })
                session.commit()
            return {"status": "success", "key": key}
        except Exception as e:
            logger.error(f"Failed to store memory in SQLite: {e}")
            raise

    async def search(
        self, 
        query: str, 
        user_id: str = "default_user", 
        scope: Optional[str] = None, 
        timeframe: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves relevant facts with temporal and active filtering.
        
        Args:
            query: Search query string.
            user_id: Identifier for the user.
            scope: Optional scope filter (e.g., 'soul', 'session').
            timeframe: Optional 'daily', 'weekly', or 'monthly'.
        """
        logger.info(
            f"Searching memory in SQLite | Scope: {scope} | "
            f"Timeframe: {timeframe} | Query: {query}"
        )
        try:
            with self.Session() as session:
                # We only search for ACTIVE memories in the normal flow
                query_str = "SELECT value, category, updated_at FROM user_soul WHERE is_active = 1"
                params = {}
                
                if scope:
                    query_str += " AND category = :scope"
                    params["scope"] = scope
                
                if timeframe:
                    days = {"daily": 1, "weekly": 7, "monthly": 30}.get(timeframe, 30)
                    query_str += f" AND updated_at > datetime('now', '-{days} days')"
                
                results = session.execute(text(query_str), params).fetchall()
                return [
                    {"content": r[0], "scope": r[1], "updated_at": r[2]} 
                    for r in results
                ]
        except Exception as e:
            logger.error(f"Failed to search memory in SQLite: {e}")
            return []


class SoulMemory:
    """Integrates Markdown and SQLite Shared Memory."""
    
    def __init__(self, soul_file_path: str = "user_soul.md"):
        self.soul_file_path = soul_file_path
        self.shared_memory = SharedMemoryManager()
        # Deferred import to avoid circular dependency
        from core.adapter import GeminiAdapter
        self.adapter = GeminiAdapter()

    async def add_fact(
        self, 
        raw_input: str, 
        user_id: str = "default_user", 
        scope: str = "soul"
    ):
        """Extracts clean facts via Gemini and updates Markdown + SQLite."""
        prompt = (
            f"Extract concise, atomic facts from: '{raw_input}'. "
            "Output bullet points starting with '-'."
        )
        extracted_facts = await self.adapter.generate_content(
            prompt, 
            include_memory=False
        )
        
        # 2. Update Markdown for human readability
        with open(self.soul_file_path, "a", encoding="utf-8") as f:
            f.write(
                f"\n\n### Updated {datetime.now().isoformat()}\n"
                f"{extracted_facts.strip()}"
            )
            
        # 3. Update SQLite for node sharing
        facts = [
            f.strip("- ").strip() 
            for f in extracted_facts.strip().split("\n") 
            if f.strip()
        ]
        for fact in facts:
            await self.shared_memory.add(
                fact, 
                user_id=user_id, 
                metadata={"scope": scope}
            )

    async def search_facts(
        self, 
        query: str, 
        user_id: str = "default_user", 
        scope: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches SQLite Shared Memory for facts."""
        return await self.shared_memory.search(
            query, 
            user_id=user_id, 
            scope=scope
        )
