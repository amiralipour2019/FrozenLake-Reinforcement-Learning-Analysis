# -*- coding: utf-8 -*-
"""STA-6367-RL-MiniProject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Wjlwi0yT_o2Hw5PqE71QipuJaDk-fcnO
"""



#Load my google derive
from google.colab import drive
drive.mount('/content/drive')

# Install gymnasium
!pip install gymnasium

# Install lake_envs package
import sys
sys.path.append('/content/lake_envs.py')
from lake_envs import *

# Load the required packages
import numpy as np
import gymnasium as gym
import time
from lake_envs import *

"""# Policy Evaluation Algorithm

* Define a function to evalaute the policy
"""

# complete the policy_evaluation function

def policy_evaluation(P, nS, nA, policy, gamma=0.9, tol=1e-3):
    """

    Parameters
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    policy: np.array[nS]
        The policy to evaluate. Maps states to actions.
    tol: float
        Terminate policy evaluation when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns
    -------
    value_function: np.ndarray[nS]
        The value function of the given policy, where value_function[s] is
        the value of state s
    """

    value_function = np.zeros(nS)

    while True:
        delta = 0
        for s in range(nS):
            v = 0
            # Look at the action recommended by the policy for this state
            a = policy[s]
            # For each outcome of taking action a in state s
            for prob, next_state, reward, done in P[s][a]:
                # Calculate the expected value
                v += prob * (reward + gamma * value_function[next_state] * (not done))
            # Calculate the absolute difference between old and new values
            delta = max(delta, np.abs(v - value_function[s]))
            value_function[s] = v

        # Check if the change in value function is below the tolerance
        if delta < tol:
            break

    return value_function

"""* Define a function to improve the Policy:

It makes the best choice at each state given the current value function.
"""

def policy_improvement(P, nS, nA, value_from_policy, gamma):
    """
    Performs policy improvement given a value function.

    Parameters
    ----------
    P : dict
    nS : int
    nA : int
    value_from_policy : np.ndarray
        The value of each state under the current policy.
    gamma : float

    Returns
    -------
    policy : np.ndarray
        An improved policy.
    """
    new_policy = np.zeros(nS, dtype=int)
    for s in range(nS):
        q_sa = np.zeros(nA)
        for a in range(nA):
            for prob, next_state, reward, done in P[s][a]:
                q_sa[a] += prob * (reward + gamma * value_from_policy[next_state] * (not done))
        new_policy[s] = np.argmax(q_sa)
    return new_policy

"""* Iterattion Policy Function:

It iterates between evaluation and improvement continues until the policy is stable
"""

def policy_iteration(P, nS, nA, gamma=0.9, tol=1e-3):
    """
    Runs policy iteration.

    Parameters
    ----------
    P, nS, nA, gamma, tol

    Returns
    ----------
    value_function: np.ndarray[nS],
    policy: np.ndarray[nS]
    """

    policy = np.zeros(nS, dtype=int)
    while True:
        value_function = policy_evaluation(P, nS, nA, policy, gamma, tol)
        new_policy = policy_improvement(P, nS, nA, value_function, gamma)

        # If the new policy is the same as the old policy, stop iteration
        if np.array_equal(new_policy, policy):
            break

        policy = new_policy

    return value_function, policy

"""* Value Iteration Function:

Value iteration is a method for finding the optimal policy and value function for a given Markov Decision Process (MDP)
"""

def value_iteration(P, nS, nA, gamma=0.9, tol=1e-3):
    """
    Learn value function and policy by using value iteration method for a given
    gamma and environment.

    Parameters:
    ----------
    P, nS, nA, gamma:
        defined at beginning of file
    tol: float
        Terminate value iteration when
            max |value_function(s) - prev_value_function(s)| < tol
    Returns:
    ----------
    value_function: np.ndarray[nS]
    policy: np.ndarray[nS]
    """

    value_function = np.zeros(nS)
    policy = np.zeros(nS, dtype=int)

    while True:
        delta = 0
        for s in range(nS):
            # Perform a one-step lookahead to find the best action for the current state
            A = np.zeros(nA)
            for a in range(nA):
                for prob, next_state, reward, done in P[s][a]:
                    A[a] += prob * (reward + gamma * value_function[next_state] * (not done))
            best_action_value = np.max(A)

            # Calculate the delta to check the change in value function
            delta = max(delta, np.abs(best_action_value - value_function[s]))
            value_function[s] = best_action_value

        # If the change in value function is smaller than the tolerance, break the loop
        if delta < tol:
            break

    # Output a deterministic policy using the optimal value function
    for s in range(nS):
        # One-step lookahead to find the best action for this state
        A = np.zeros(nA)
        for a in range(nA):
            for prob, next_state, reward, done in P[s][a]:
                A[a] += prob * (reward + gamma * value_function[next_state] * (not done))
        best_action = np.argmax(A)
        policy[s] = best_action

    return value_function, policy

"""
* Define a function can  visualize the performance of a policy in a Gym environment
"""

def render_single(env, policy, max_steps=100):
    """
    Renders policy once on environment. Watch your agent play!

    Parameters
    ----------
    env: gym.core.Environment
      Environment to play on. Must have nS, nA, and P as
      attributes.
    Policy: np.array of shape [env.nS]
      The action to take at a given state
    """
    episode_reward = 0
    ob = env.reset()  # Corrected this line to handle the single return value
    for t in range(max_steps):
        env.render()
        time.sleep(0.25)
        a = policy[ob]
        ob, rew, done, info = env.step(a)  # Adjusted for the typical return values of env.step()
        episode_reward += rew
        if done:
            break
    env.render()
    if not done:
        print("The agent didn't reach a terminal state in {} steps.".format(max_steps))
    else:
        print("Episode reward: %f" % episode_reward)

if __name__ == "__main__":
    # comment/uncomment these lines to switch between deterministic/stochastic environments
    # If specific deterministic/stochastic versions are not directly supported, you may need to adjust these lines
    env = gym.make("FrozenLake-v1", is_slippery=False) # Deterministic version, assuming `is_slippery` flag controls it
    # env = gym.make("FrozenLake-v1", is_slippery=True) # Stochastic version, assuming `is_slippery` flag controls it

    # Extracting the number of states and actions from the environment
    nS = env.observation_space.n
    nA = env.action_space.n

    print("\n" + "-" * 25 + "\nBeginning Policy Iteration\n" + "-" * 25)

    V_pi, p_pi = policy_iteration(env.P, nS, nA, gamma=0.9, tol=1e-3)
    render_single(env, p_pi, 100)

    print("\n" + "-" * 25 + "\nBeginning Value Iteration\n" + "-" * 25)

    V_vi, p_vi = value_iteration(env.P, nS, nA, gamma=0.9, tol=1e-3)
    render_single(env, p_vi, 100)



if __name__ == "__main__":
    # Adjust environment creation to match available configurations for deterministic and stochastic versions
    deterministic_env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=False)  # Assuming deterministic version
    stochastic_env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=True)  # Assuming stochastic version

    # Extracting the number of states and actions from the environments
    deterministic_nS = deterministic_env.observation_space.n
    deterministic_nA = deterministic_env.action_space.n
    stochastic_nS = stochastic_env.observation_space.n
    stochastic_nA = stochastic_env.action_space.n

    print("\n" + "-" * 25 + "\nDeterministic FrozenLake-v1\n" + "-" * 25)
    print("\n" + "-" * 25 + "\nBeginning Policy Iteration\n" + "-" * 25)
    V_pi_det, p_pi_det = policy_iteration(
        deterministic_env.P, deterministic_nS, deterministic_nA, gamma=0.9, tol=1e-3
    )
    print("Optimal Value Function (Policy Iteration):")
    print(V_pi_det)
    print("Optimal Policy (Policy Iteration):")
    print(p_pi_det)

    print("\n" + "-" * 25 + "\nBeginning Value Iteration\n" + "-" * 25)
    V_vi_det, p_vi_det = value_iteration(
        deterministic_env.P, deterministic_nS, deterministic_nA, gamma=0.9, tol=1e-3
    )
    print("Optimal Value Function (Value Iteration):")
    print(V_vi_det)
    print("Optimal Policy (Value Iteration):")
    print(p_vi_det)

    print("\n" + "-" * 25 + "\nStochastic FrozenLake-v1\n" + "-" * 25)
    print("\n" + "-" * 25 + "\nBeginning Policy Iteration\n" + "-" * 25)
    V_pi_sto, p_pi_sto = policy_iteration(
        stochastic_env.P, stochastic_nS, stochastic_nA, gamma=0.9, tol=1e-3
    )
    print("Optimal Value Function (Policy Iteration):")
    print(V_pi_sto)
    print("Optimal Policy (Policy Iteration):")
    print(p_pi_sto)

    print("\n" + "-" * 25 + "\nBeginning Value Iteration\n" + "-" * 25)
    V_vi_sto, p_vi_sto = value_iteration(
        stochastic_env.P, stochastic_nS, stochastic_nA, gamma=0.9, tol=1e-3
    )
    print("Optimal Value Function (Value Iteration):")
    print(V_vi_sto)
    print("Optimal Policy (Value Iteration):")
    print(p_vi_sto)

import numpy as np
import gym
import matplotlib.pyplot as plt
from lake_envs import *  # Ensure you have this module for custom environments

np.set_printoptions(precision=3)

def draw_grid_environment(environment, title):
    grid_size = environment.desc.shape[0]  # Assume square grid
    fig, ax = plt.subplots(figsize=(grid_size, grid_size))

    ax.matshow(np.zeros((grid_size, grid_size)), cmap='Wistia')
    ax.set_xticks(np.arange(-0.5, grid_size, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, grid_size, 1), minor=True)
    ax.grid(which='minor', color='k', linestyle='-', linewidth=2)

    for y in range(grid_size):
        for x in range(grid_size):
            char = environment.desc[y, x].decode('utf-8')
            color = 'green' if char == 'G' else 'blue' if char == 'S' else 'white'
            ax.text(x, y, char, ha='center', va='center', color=color, fontsize=20, weight='bold')

    plt.title(title)
    plt.xticks([])
    plt.yticks([])
    plt.show()


def illustrate_agent_path(environment, path):
    nrows, ncols = environment.desc.shape
    trajectory_img = np.zeros((nrows, ncols))
    plt.imshow(trajectory_img, cmap='Greys', origin='upper', extent=(0, ncols, 0, nrows))

    for r in range(nrows):
        for c in range(ncols):
            if environment.desc[r, c] == b'H':
                plt.gca().add_patch(plt.Rectangle((c, r), 1, 1, color='darkred'))
            if environment.desc[r, c] == b'G':
                plt.text(c + 0.5, r + 0.5, 'G', color='gold', ha='center', va='center', fontsize=14)

    for index, (state, action, _, next_state, done) in enumerate(path):
        r, c = state // ncols, state % ncols
        nr, nc = next_state // ncols, next_state % ncols
        plt.plot([c + 0.5, nc + 0.5], [r + 0.5, nr + 0.5], 'y', linewidth=2)
        if not done:
            plt.text(c + 0.5, r + 0.5, str(index), color='lime', ha='center', va='center', fontsize=10)

    plt.title('Path of the Agent', fontsize=16)
    plt.gca().invert_yaxis()  # Invert y-axis to match the gridworld layout
    plt.axis('off')
    plt.show()

# ... Your policy evaluation, improvement, and iteration functions ...
def show_policy_execution(environment, policy, max_steps=100):
    episode_reward = 0
    state = environment.reset()
    # If the state is a tuple (due to the environment's design), extract the first element.
    state = state[0] if isinstance(state, tuple) else state
    path_taken = []

    for _ in range(max_steps):
        action = policy[state]
        # Unpack the returned values correctly. If there are additional values, ignore them with '*_'.
        new_state, reward, finished, *_ = environment.step(action)
        # If the new_state is a tuple, extract the state information correctly.
        new_state = new_state[0] if isinstance(new_state, tuple) else new_state
        path_taken.append((state, action, reward, new_state, finished))
        episode_reward += reward
        state = new_state
        if finished:
            break

    illustrate_agent_path(environment, path_taken)
    print("Total reward received: ", episode_reward)


# ... Main execution ...

# Note: Ensure the 'lake_envs.py' module has the appropriate environments or adjust the environment names accordingly.

# Main execution
if __name__ == "__main__":
    # Initialize the environment - replace with the appropriate environment name
    # Ensure the 'lake_envs.py' module has the appropriate environments or adjust the environment names accordingly.
    env = gym.make("FrozenLake-v1", desc=None, map_name="4x4", is_slippery=True)

    # Extracting the number of states and actions from the environment
    nS = env.observation_space.n
    nA = env.action_space.n

    # Run Policy Iteration
    print("\n" + "-" * 25 + "\nRunning Policy Iteration\n" + "-" * 25)
    V_pi, p_pi = policy_iteration(env.P, nS, nA, gamma=0.9, tol=1e-3)
    draw_grid_environment(env, title="Optimal Policy Grid - Policy Iteration")
    show_policy_execution(env, p_pi, max_steps=100)

    # Run Value Iteration
    print("\n" + "-" * 25 + "\nRunning Value Iteration\n" + "-" * 25)
    V_vi, p_vi = value_iteration(env.P, nS, nA, gamma=0.9, tol=1e-3)
    draw_grid_environment(env, title="Optimal Policy Grid - Value Iteration")
    show_policy_execution(env, p_vi, max_steps=100)