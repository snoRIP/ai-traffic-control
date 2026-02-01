import numpy as np
import random
from collections import deque
from typing import List, Tuple, Any

class DQNAgent:
    """
    A Deep Q-Network Agent implemented from scratch using NumPy.
    Optimizes traffic light switching by learning from queue states.
    """
    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=5000)
        
        # Hyperparameters
        self.gamma = 0.95            
        self.epsilon = 1.0           
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995   
        self.learning_rate = 0.0005
        
        # Neural Network Weights (Input -> 32 -> 32 -> Output)
        self.w1 = np.random.randn(state_size, 32).astype(np.float64) * np.sqrt(2./state_size)
        self.b1 = np.zeros((1, 32), dtype=np.float64)
        self.w2 = np.random.randn(32, 32).astype(np.float64) * np.sqrt(2./32)
        self.b2 = np.zeros((1, 32), dtype=np.float64)
        self.w3 = np.random.randn(32, action_size).astype(np.float64) * 0.1
        self.b3 = np.zeros((1, action_size), dtype=np.float64)

    def _relu(self, x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)

    def _forward(self, state: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Ensure state is 2D (1, state_size)
        if state.ndim == 1:
            state = state.reshape(1, -1)
        z1 = np.dot(state, self.w1) + self.b1
        a1 = self._relu(z1)
        z2 = np.dot(a1, self.w2) + self.b2
        a2 = self._relu(z2)
        z3 = np.dot(a2, self.w3) + self.b3
        return a1, a2, z3

    def act(self, state: np.ndarray) -> int:
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        try:
            _, _, q_values = self._forward(state)
            return int(np.argmax(q_values[0]))
        except Exception:
            return random.randrange(self.action_size)

    def remember(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        self.memory.append((state.flatten(), action, reward, next_state.flatten(), done))

    def train(self, batch_size: int = 32):
        if len(self.memory) < batch_size:
            return

        minibatch = random.sample(self.memory, batch_size)
        
        # Vectorized implementation
        states = np.array([m[0] for m in minibatch])
        actions = np.array([m[1] for m in minibatch])
        rewards = np.array([m[2] for m in minibatch])
        next_states = np.array([m[3] for m in minibatch])
        dones = np.array([m[4] for m in minibatch])

        # 1. Target Q-Values
        _, _, next_q_values = self._forward(next_states)
        max_next_q = np.amax(next_q_values, axis=1)
        targets = rewards + self.gamma * max_next_q * (1 - dones)

        # 2. Forward Pass
        z1 = np.dot(states, self.w1) + self.b1
        a1 = self._relu(z1)
        z2 = np.dot(a1, self.w2) + self.b2
        a2 = self._relu(z2)
        z3 = np.dot(a2, self.w3) + self.b3
        q_values = z3

        # 3. Calculate Error (Gradient of Loss wrt Output)
        target_f = q_values.copy()
        target_f[np.arange(batch_size), actions] = targets
        error = (q_values - target_f) / batch_size # MSE gradient

        # 4. Backpropagation (Vectorized)
        grad_w3 = np.dot(a2.T, error)
        grad_b3 = np.sum(error, axis=0, keepdims=True)
        
        delta2 = np.dot(error, self.w3.T) * (a2 > 0)
        grad_w2 = np.dot(a1.T, delta2)
        grad_b2 = np.sum(delta2, axis=0, keepdims=True)
        
        delta1 = np.dot(delta2, self.w2.T) * (a1 > 0)
        grad_w1 = np.dot(states.T, delta1)
        grad_b1 = np.sum(delta1, axis=0, keepdims=True)

        # Update weights
        self.w3 -= self.learning_rate * grad_w3
        self.b3 -= self.learning_rate * grad_b3
        self.w2 -= self.learning_rate * grad_w2
        self.b2 -= self.learning_rate * grad_b2
        self.w1 -= self.learning_rate * grad_w1
        self.b1 -= self.learning_rate * grad_b1

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay