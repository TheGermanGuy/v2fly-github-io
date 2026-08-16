"""
Network Resilience
Retry logic with exponential backoff for unreliable connections
"""

import asyncio
import time
from typing import Callable, Optional, Any


class RetryPolicy:
    """Defines retry behavior"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, retry_count: int) -> float:
        """Calculate delay for retry attempt with exponential backoff"""
        delay = self.base_delay * (self.exponential_base ** retry_count)
        return min(delay, self.max_delay)

    def should_retry(self, retry_count: int, exception: Exception) -> bool:
        """Determine if operation should be retried"""
        if retry_count >= self.max_retries:
            return False

        # Retry on network errors, not on application logic errors
        retryable_exceptions = (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
            OSError,
        )

        return isinstance(exception, retryable_exceptions)


class NetworkResilience:
    """Provides retry logic for network operations"""

    DEFAULT_POLICY = RetryPolicy(max_retries=3, base_delay=2.0)

    @staticmethod
    def retry_sync(
        operation: Callable,
        policy: Optional[RetryPolicy] = None,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        Execute synchronous operation with automatic retry

        Args:
            operation: Callable to execute
            policy: RetryPolicy (default: DEFAULT_POLICY)
            *args, **kwargs: Arguments for operation

        Returns:
            Result or None if all retries failed
        """
        if policy is None:
            policy = NetworkResilience.DEFAULT_POLICY

        last_exception = None
        for retry_count in range(policy.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if not policy.should_retry(retry_count, e):
                    break

                delay = policy.get_delay(retry_count)
                print(f"[RETRY] Operation failed, retrying in {delay:.1f}s (attempt {retry_count + 1}/{policy.max_retries})")
                time.sleep(delay)

        print(f"[ERROR] Operation failed after {policy.max_retries} retries: {last_exception}")
        return None

    @staticmethod
    async def retry_async(
        operation: Callable,
        policy: Optional[RetryPolicy] = None,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        Execute asynchronous operation with automatic retry

        Args:
            operation: Async callable to execute
            policy: RetryPolicy (default: DEFAULT_POLICY)
            *args, **kwargs: Arguments for operation

        Returns:
            Result or None if all retries failed
        """
        if policy is None:
            policy = NetworkResilience.DEFAULT_POLICY

        last_exception = None
        for retry_count in range(policy.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                else:
                    return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if not policy.should_retry(retry_count, e):
                    break

                delay = policy.get_delay(retry_count)
                print(f"[RETRY] Async operation failed, retrying in {delay:.1f}s (attempt {retry_count + 1}/{policy.max_retries})")
                await asyncio.sleep(delay)

        print(f"[ERROR] Async operation failed after {policy.max_retries} retries: {last_exception}")
        return None


class CircuitBreaker:
    """Prevents cascading failures with circuit breaker pattern"""

    def __init__(self, failure_threshold: int = 5, timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open

    def call(self, operation: Callable, *args, **kwargs) -> Optional[Any]:
        """Execute operation with circuit breaker protection"""
        # Check if circuit should be reset
        if self.state == 'open':
            time_since_failure = time.time() - self.last_failure_time
            if time_since_failure > self.timeout_seconds:
                self.state = 'half-open'
                print(f"[CIRCUIT] Circuit breaker entering half-open state")
            else:
                print(f"[CIRCUIT] Circuit breaker is open, rejecting request")
                return None

        try:
            result = operation(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failure_count = 0
                print(f"[CIRCUIT] Circuit breaker closed, operation successful")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                print(f"[CIRCUIT] Circuit breaker opened after {self.failure_count} failures")

            raise e

    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.state = 'closed'
        self.last_failure_time = None
        print(f"[CIRCUIT] Circuit breaker reset")

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'last_failure_time': self.last_failure_time,
        }
