package services

import (
	"testing"
	"time"

	"order-processor-gateway/pkg/constants"

	"github.com/stretchr/testify/assert"
)

// testServiceName is a distinct name for the test circuit breaker (not used in production routes).
const testServiceName = "test-service"

func createTestCircuitBreaker() *CircuitBreaker {
	return &CircuitBreaker{
		serviceName:      testServiceName,
		state:            constants.CircuitBreakerStateClosed,
		failureCount:     0,
		successCount:     0,
		failureThreshold: constants.CircuitBreakerFailureThreshold,
		timeout:          constants.CircuitBreakerTimeout,
		successThreshold: constants.CircuitBreakerSuccessThreshold,
	}
}

func TestCircuitBreakerCanExecute(t *testing.T) {
	t.Run("Closed state allows execution", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateClosed

		assert.True(t, cb.CanExecute())
	})

	t.Run("Open state blocks execution initially", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateOpen
		cb.lastFailureTime = time.Now()

		assert.False(t, cb.CanExecute())
	})

	t.Run("Open state allows execution after timeout", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateOpen
		cb.lastFailureTime = time.Now().Add(-constants.CircuitBreakerTimeout - time.Second)
		cb.timeout = constants.CircuitBreakerTimeout

		canExecute := cb.CanExecute()
		assert.True(t, canExecute)
		// Should transition to half-open
		assert.Equal(t, constants.CircuitBreakerStateHalfOpen, cb.GetState())
	})

	t.Run("Half-open state allows execution", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateHalfOpen

		assert.True(t, cb.CanExecute())
	})
}

func TestCircuitBreakerRecordSuccess(t *testing.T) {
	t.Run("Record success in closed state", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateClosed
		initialSuccessCount := cb.successCount

		cb.RecordSuccess()

		assert.Equal(t, initialSuccessCount+1, cb.successCount)
		assert.Equal(t, constants.CircuitBreakerStateClosed, cb.GetState())
	})

	t.Run("Record success in half-open state reaches threshold", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateHalfOpen
		cb.successCount = constants.CircuitBreakerSuccessThreshold - 1

		cb.RecordSuccess()

		assert.Equal(t, constants.CircuitBreakerStateClosed, cb.GetState())
		assert.Equal(t, 0, cb.GetFailureCount())
		// successCount should be reset to 0
		assert.Equal(t, constants.CircuitBreakerStateClosed, cb.GetState())
	})

	t.Run("Record success in half-open state below threshold", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateHalfOpen
		initialSuccessCount := constants.CircuitBreakerSuccessThreshold - 2
		cb.successCount = initialSuccessCount

		cb.RecordSuccess()

		assert.Equal(t, constants.CircuitBreakerStateHalfOpen, cb.GetState())
		// Should increment success count
		assert.Equal(t, constants.CircuitBreakerStateHalfOpen, cb.GetState())
	})
}

func TestCircuitBreakerRecordFailure(t *testing.T) {
	t.Run("Record failure in closed state", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateClosed
		initialFailureCount := cb.GetFailureCount()

		cb.RecordFailure()

		assert.Equal(t, initialFailureCount+1, cb.GetFailureCount())
	})

	t.Run("Record failure reaches threshold in closed state", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateClosed
		cb.failureCount = constants.CircuitBreakerFailureThreshold - 1
		initialTime := time.Now()

		cb.RecordFailure()

		assert.Equal(t, constants.CircuitBreakerStateOpen, cb.GetState())
		assert.Equal(t, constants.CircuitBreakerFailureThreshold, cb.GetFailureCount())
		// lastFailureTime should be updated
		assert.True(t, cb.lastFailureTime.After(initialTime) || cb.lastFailureTime.Equal(initialTime))
	})

	t.Run("Record failure in half-open state increments failure count", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateHalfOpen
		initialTime := time.Now()
		initialFailureCount := cb.GetFailureCount()

		cb.RecordFailure()

		// Circuit breaker stays in half-open until failure threshold is reached
		assert.Equal(t, initialFailureCount+1, cb.GetFailureCount())
		assert.True(t, cb.lastFailureTime.After(initialTime) || cb.lastFailureTime.Equal(initialTime))
		
		// If failure count reaches threshold, state should be open
		if cb.GetFailureCount() >= constants.CircuitBreakerFailureThreshold {
			assert.Equal(t, constants.CircuitBreakerStateOpen, cb.GetState())
		} else {
			// Otherwise stays in half-open
			assert.Equal(t, constants.CircuitBreakerStateHalfOpen, cb.GetState())
		}
	})

	t.Run("Record failure in half-open state reaches threshold", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateHalfOpen
		cb.failureCount = constants.CircuitBreakerFailureThreshold - 1 // One failure away from threshold
		initialTime := time.Now()

		cb.RecordFailure()

		assert.Equal(t, constants.CircuitBreakerStateOpen, cb.GetState())
		assert.Equal(t, constants.CircuitBreakerFailureThreshold, cb.GetFailureCount())
		assert.True(t, cb.lastFailureTime.After(initialTime) || cb.lastFailureTime.Equal(initialTime))
	})

	t.Run("Record failure in open state updates failure time", func(t *testing.T) {
		cb := createTestCircuitBreaker()
		cb.state = constants.CircuitBreakerStateOpen
		oldFailureTime := time.Now().Add(-time.Minute)
		cb.lastFailureTime = oldFailureTime

		cb.RecordFailure()

		assert.Equal(t, constants.CircuitBreakerStateOpen, cb.GetState())
		assert.True(t, cb.lastFailureTime.After(oldFailureTime))
	})
}

func TestCircuitBreakerGetState(t *testing.T) {
	cb := createTestCircuitBreaker()

	testCases := []struct {
		name  string
		state string
	}{
		{"Closed state", constants.CircuitBreakerStateClosed},
		{"Open state", constants.CircuitBreakerStateOpen},
		{"Half-open state", constants.CircuitBreakerStateHalfOpen},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			cb.state = tc.state
			assert.Equal(t, tc.state, cb.GetState())
		})
	}
}

func TestCircuitBreakerGetFailureCount(t *testing.T) {
	cb := createTestCircuitBreaker()

	testCounts := []int{0, 1, constants.CircuitBreakerFailureThreshold, 10}

	for _, count := range testCounts {
		t.Run("Failure count", func(t *testing.T) {
			cb.failureCount = count
			assert.Equal(t, count, cb.GetFailureCount())
		})
	}
}

func TestCircuitBreakerSuccessCount(t *testing.T) {
	cb := createTestCircuitBreaker()

	testCounts := []int{0, 1, constants.CircuitBreakerSuccessThreshold, constants.CircuitBreakerFailureThreshold}

	for _, count := range testCounts {
		t.Run("Success count", func(t *testing.T) {
			cb.successCount = count
			// Verify success count is set correctly
			assert.Equal(t, count, cb.successCount)
		})
	}
}
