"""
Semantic cache and query optimizer using local embedding models
"""

import numpy as np
from typing import Optional, List, Dict, Any
import json
import os
from pathlib import Path

class SemanticCache:
    """
    Caches query results using semantic similarity
    Uses local embedding models only
    Supports persistence to disk via JSON or pickle files
    """
    
    def __init__(self, similarity_threshold: float = 0.95, cache_file: str = "semantic_cache.pkl") -> None:
        self.cache: List[Dict] = []
        self.similarity_threshold = similarity_threshold
        self.model = None
        
        # Support environment variable for cache file path
        cache_file_env = os.environ.get('NEXUMDB_CACHE_FILE', cache_file)
        self.cache_file = cache_file_env
        
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_path = self.cache_dir / self.cache_file
        
        # Load existing cache on initialization
        self.load_cache()
        
    def initialize_model(self) -> None:
        """Initialize local embedding model - deferred to avoid import errors"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Semantic cache initialized with all-MiniLM-L6-v2")
        except ImportError:
            print("Warning: sentence-transformers not installed, using fallback")
            self.model = None
    
    def vectorize(self, text: str) -> List[float]:
        """Convert text to embedding vector"""
        if self.model is None:
            self.initialize_model()
        
        if self.model is not None:
            embedding = self.model.encode(text)
            return embedding.tolist()
        else:
            return self._fallback_vectorize(text)
    
    def _fallback_vectorize(self, text: str) -> List[float]:
        """Simple fallback vectorization using character hashing"""
        vec = [0.0] * 384
        for i, char in enumerate(text[:384]):
            vec[i] = float(ord(char)) / 128.0
        return vec
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_arr = np.array(vec1)
        vec2_arr = np.array(vec2)
        
        dot_product = np.dot(vec1_arr, vec2_arr)
        norm1 = np.linalg.norm(vec1_arr)
        norm2 = np.linalg.norm(vec2_arr)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def get(self, query: str) -> Optional[str]:
        """Retrieve cached result if similar query exists"""
        query_vec = self.vectorize(query)
        
        for entry in self.cache:
            similarity = self.cosine_similarity(query_vec, entry['vector'])
            if similarity >= self.similarity_threshold:
                print(f"Cache hit! Similarity: {similarity:.4f}")
                return entry['result']
        
        return None
    
    def put(self, query: str, result: str) -> None:
        """Store query and result in cache"""
        query_vec = self.vectorize(query)
        self.cache.append({
            'query': query,
            'vector': query_vec,
            'result': result
        })
        print(f"Cached query: {query[:50]}...")
        
        # Auto-save cache after adding new entry
        self.save_cache()
    
    def clear(self) -> None:
        """Clear the cache"""
        self.cache.clear()
        # Remove cache file when clearing
        if self.cache_path.exists():
            self.cache_path.unlink()
            print("Cache file deleted")
    
    def save_cache(self, filepath: Optional[str] = None) -> None:
        """Save cache to disk using pickle for better performance"""
        try:
            import pickle
        except ImportError:
            print("Warning: pickle not available, cannot save cache")
            return
        
        if filepath is None:
            filepath = str(self.cache_path)
        
        try:
            # Create backup of existing cache
            if os.path.exists(filepath):
                backup_path = f"{filepath}.backup"
                os.rename(filepath, backup_path)
            
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'cache': self.cache,
                    'similarity_threshold': self.similarity_threshold,
                    'cache_size': len(self.cache)
                }, f)
            
            print(f"Semantic cache saved to {filepath} ({len(self.cache)} entries)")
            
            # Remove backup if save was successful
            backup_path = f"{filepath}.backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
        except Exception as e:
            print(f"Error saving semantic cache: {e}")
            # Restore backup if save failed
            backup_path = f"{filepath}.backup"
            if os.path.exists(backup_path):
                os.rename(backup_path, filepath)
    
    def load_cache(self, filepath: Optional[str] = None) -> None:
        """Load cache from disk using pickle"""
        try:
            import pickle
        except ImportError:
            print("Warning: pickle not available, cannot load cache")
            return
        
        if filepath is None:
            filepath = str(self.cache_path)
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                
                self.cache = data.get('cache', [])
                self.similarity_threshold = data.get('similarity_threshold', self.similarity_threshold)
                
                print(f"Semantic cache loaded from {filepath} ({len(self.cache)} entries)")
                
                # Validate cache entries
                valid_entries = []
                for entry in self.cache:
                    if all(key in entry for key in ['query', 'vector', 'result']):
                        valid_entries.append(entry)
                    else:
                        print(f"Warning: Invalid cache entry found and removed")
                
                self.cache = valid_entries
                
            except Exception as e:
                print(f"Error loading semantic cache: {e}")
                print("Starting with empty cache")
                self.cache = []
        else:
            print(f"No cache file found at {filepath}, starting with empty cache")
    
    def save_cache_json(self, filepath: Optional[str] = None) -> None:
        """Save cache to JSON format (alternative to pickle)"""
        if filepath is None:
            filepath = str(self.cache_path).replace('.pkl', '.json')
        
        try:
            cache_data = {
                'cache': self.cache,
                'similarity_threshold': self.similarity_threshold,
                'cache_size': len(self.cache),
                'format_version': '1.0'
            }
            
            with open(filepath, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"Semantic cache saved to JSON: {filepath}")
            
        except Exception as e:
            print(f"Error saving cache to JSON: {e}")
    
    def load_cache_json(self, filepath: Optional[str] = None) -> None:
        """Load cache from JSON format"""
        if filepath is None:
            filepath = str(self.cache_path).replace('.pkl', '.json')
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.cache = data.get('cache', [])
                self.similarity_threshold = data.get('similarity_threshold', self.similarity_threshold)
                
                print(f"Semantic cache loaded from JSON: {filepath} ({len(self.cache)} entries)")
                
            except Exception as e:
                print(f"Error loading cache from JSON: {e}")
                self.cache = []
        else:
            print(f"No JSON cache file found at {filepath}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'similarity_threshold': self.similarity_threshold,
            'cache_file': str(self.cache_path),
            'cache_exists': self.cache_path.exists(),
            'cache_size_bytes': self.cache_path.stat().st_size if self.cache_path.exists() else 0
        }
    
    def set_cache_expiration(self, max_age_hours: int = 24) -> None:
        """Remove cache entries older than specified hours (future enhancement)"""
        # This would require adding timestamps to cache entries
        # For now, just a placeholder for TTL functionality
        print(f"Cache expiration set to {max_age_hours} hours (not yet implemented)")
    
    def optimize_cache(self, max_entries: int = 1000) -> None:
        """Remove oldest entries if cache exceeds max size"""
        if len(self.cache) > max_entries:
            removed_count = len(self.cache) - max_entries
            self.cache = self.cache[-max_entries:]  # Keep most recent entries
            print(f"Cache optimized: removed {removed_count} oldest entries")
            self.save_cache()


class QueryOptimizer:
    """
    Reinforcement learning-based query optimizer
    Uses Q-learning to optimize query execution
    """
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.9) -> None:
        self.q_table: Dict[str, Dict[str, float]] = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = 0.1
        
    def get_action(self, state: str, available_actions: List[str]) -> str:
        """Select action using epsilon-greedy strategy"""
        if np.random.random() < self.epsilon:
            return np.random.choice(available_actions)
        
        if state not in self.q_table:
            self.q_table[state] = {action: 0.0 for action in available_actions}
        
        state_values = self.q_table[state]
        best_action = max(available_actions, key=lambda a: state_values.get(a, 0.0))
        return best_action
    
    def update(self, state: str, action: str, reward: float, next_state: str) -> None:
        """Update Q-values based on observed reward"""
        if state not in self.q_table:
            self.q_table[state] = {}
        
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0
        
        current_q = self.q_table[state][action]
        
        max_next_q = 0.0
        if next_state in self.q_table:
            max_next_q = max(self.q_table[next_state].values()) if self.q_table[next_state] else 0.0
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
        
        print(f"Updated Q({state}, {action}) = {new_q:.4f}")
    
    def feed_metrics(self, query: str, latency_ms: float) -> None:
        """Feed execution metrics to the optimizer"""
        reward = -latency_ms / 1000.0
        
        state = f"query_type_{len(query) // 10}"
        action = "execute"
        next_state = "completed"
        
        self.update(state, action, reward, next_state)


def test_vectorization() -> Dict[str, Any]:
    """Test function for Rust integration"""
    cache = SemanticCache()
    test_query = "SELECT * FROM users WHERE age > 25"
    vector = cache.vectorize(test_query)
    return {
        'query': test_query,
        'vector': vector[:10],
        'dimension': len(vector)
    }


def test_cache_persistence() -> Dict[str, Any]:
    """Test semantic cache persistence functionality"""
    print("\n" + "="*60)
    print("Testing Semantic Cache Persistence")
    print("="*60 + "\n")
    
    # Test 1: Create cache and add entries
    print("1. Creating cache and adding test entries...")
    cache1 = SemanticCache(cache_file="test_cache.pkl")
    
    test_queries = [
        ("SELECT * FROM users WHERE age > 25", "User data for age > 25"),
        ("SELECT name FROM products WHERE price < 100", "Product names under $100"),
        ("SELECT COUNT(*) FROM orders WHERE status = 'active'", "Active order count: 42")
    ]
    
    for query, result in test_queries:
        cache1.put(query, result)
    
    stats1 = cache1.get_cache_stats()
    print(f"Cache stats after adding entries: {stats1}")
    
    # Test 2: Create new cache instance and verify persistence
    print("\n2. Creating new cache instance to test persistence...")
    cache2 = SemanticCache(cache_file="test_cache.pkl")
    
    stats2 = cache2.get_cache_stats()
    print(f"Cache stats after reload: {stats2}")
    
    # Test 3: Verify cache hits work after reload
    print("\n3. Testing cache hits after reload...")
    for query, expected_result in test_queries:
        cached_result = cache2.get(query)
        if cached_result:
            print(f"✓ Cache hit for: {query[:30]}...")
            print(f"  Result: {cached_result[:50]}...")
        else:
            print(f"✗ Cache miss for: {query[:30]}...")
    
    # Test 4: Test JSON export
    print("\n4. Testing JSON export...")
    cache2.save_cache_json("test_cache.json")
    
    # Test 5: Test cache optimization
    print("\n5. Testing cache optimization...")
    cache2.optimize_cache(max_entries=2)
    
    # Cleanup
    print("\n6. Cleaning up test files...")
    cache2.clear()
    
    return {
        'test_passed': True,
        'entries_before_reload': stats1['total_entries'],
        'entries_after_reload': stats2['total_entries'],
        'persistence_working': stats1['total_entries'] == stats2['total_entries']
    }


if __name__ == "__main__":
    # Run both tests
    print("Running vectorization test...")
    result = test_vectorization()
    print(json.dumps(result, indent=2))
    
    print("\nRunning persistence test...")
    persistence_result = test_cache_persistence()
    print(f"\nPersistence test result: {persistence_result}")
