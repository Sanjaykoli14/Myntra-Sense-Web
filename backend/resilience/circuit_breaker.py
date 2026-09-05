"""
Hystrix-Style 3-State Circuit Breaker for Myntra Sense Serving Orchestrator.
Protects upstream services against Triton ML or Feast timeouts (> 60ms SLA).
Manages CLOSED -> OPEN -> HALF-OPEN state transitions.
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Dict, Optional

logger = logging.getLogger("SenseCircuitBreaker")


class CircuitState(Enum):
    CLOSED = "CLOSED"        # Normal operation: requests routed to ML Service
    OPEN = "OPEN"            # Tripped: requests immediately routed to Fallback Engine
    HALF_OPEN = "HALF_OPEN"  # Testing recovery: trial probe requests allowed


class CircuitBreaker:
    def __init__(
        self,
        name: str = "TritonInferenceCircuitBreaker",
        failure_threshold: int = 5,
        recovery_time_seconds: float = 10.0,
        timeout_budget_ms: float = 60.0
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_time_seconds = recovery_time_seconds
        self.timeout_budget_ms = timeout_budget_ms
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_state_change = time.time()
        self.total_fallback_executions = 0

    def call(self, primary_fn: Callable[[], Any], fallback_fn: Callable[[], Any]) -> Any:
        now = time.time()
        
        # State transition: OPEN -> HALF_OPEN after recovery timeout
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change >= self.recovery_time_seconds:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                logger.info(f"[{self.name}] Transitioned from OPEN -> HALF_OPEN (Probing recovery)")
            else:
                self.total_fallback_executions += 1
                return fallback_fn()

        start_t = time.perf_counter()
        try:
            result = primary_fn()
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            
            # Check if SLA breached
            if elapsed_ms > self.timeout_budget_ms:
                logger.warning(f"[{self.name}] Call breached SLA ({elapsed_ms:.2f}ms > {self.timeout_budget_ms}ms)")
                self._record_failure()
                self.total_fallback_executions += 1
                return fallback_fn()
                
            self._record_success()
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] Primary call failed: {str(e)}")
            self._record_failure()
            self.total_fallback_executions += 1
            return fallback_fn()

    def _record_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = time.time()
                logger.info(f"[{self.name}] Recovery successful! Transitioned -> CLOSED")
        else:
            self.failure_count = 0

    def _record_failure(self):
        self.failure_count += 1
        if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_state_change = time.time()
                self.success_count = 0
                logger.error(f"[{self.name}] Circuit TRIPPED -> OPEN (Failures: {self.failure_count})")

    def force_open(self):
        self.state = CircuitState.OPEN
        self.last_state_change = time.time()

    def force_close(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_state_change = time.time()

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_fallback_executions": self.total_fallback_executions,
            "timeout_budget_ms": self.timeout_budget_ms
        }
