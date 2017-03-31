from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np
import copy


class DestinationModel:
    def __init__(self, stop_connections, gamma=0.99):
        # Q with current weights
        self.model = self.get_network_structure()
        self.model.compile(optimizer='adam', loss='mse', lr=0.001)

        # Q with "frozen" weights
        self.target_network = self.get_network_structure()
        self.target_network.compile(optimizer='adam', loss='mse')

        # Set tau = 1 to use the model weights only
        self.update_target(tau=1)

        # City map
        self.connections = stop_connections

        # Discount parameter for RL
        self.gamma = gamma

    def update_target(self, tau=0.001):

        # Get weights from both networks
        model_weights = self.model.get_weights()
        target_network_weights = self.target_network.get_weights()

        # Take convex combination of the weights from both networks
        for i in range(len(target_network_weights)):
            target_network_weights[i] = tau * model_weights[i] + (1 - tau) * target_network_weights[i]

        # Set target network weights
        self.target_network.set_weights(target_network_weights)

    def get_network_structure(self):
        return Sequential([
            Dense(200, input_dim=120 + 24),
            Activation('relu'),
            Dense(100),
            Activation('relu'),
            Dense(1),
            Activation('linear'),
        ])

    def get_max_qscore(self, action_vec, next_state, use_target_network=False):
        possible_actions_id = self.connections[np.where(action_vec == 1)[0][0]]

        # generate possible actions
        possible_actions = [np.eye(1, len(self.connections), stop) for stop in possible_actions_id]
        possible_actions.append(action_vec)

        best_qscore = - np.Inf

        # get reward targets
        for next_action_vec in possible_actions:
            qscore = self.predict(next_state, next_action_vec, use_target_network)
            if qscore > best_qscore:
                best_qscore = qscore

        return best_qscore

    def save(self, file_name):
            self.model.save('{}.net'.format(file_name))
            self.target_network.save('{}_target.net'.format(file_name))

    def load(self, file_name):
        self.model.load('{}.net'.format(file_name))
        self.target_network.load('{}_target.net'.format(file_name))

    def train(self, training_batch):
        # input points ( S[t-1], A[t-1], R[t-1], S[t] )

        # Preprocessing: generate next state + long-term reward

        inputs = []
        targets = []

        for state, action_vec, reward, next_state in training_batch:
            qscore = self.get_max_qscore(action_vec, next_state, True)

            inputs.append(np.concatenate([state, action_vec], axis=1).reshape((1, -1)))
            targets.append(reward + self.gamma * qscore)

        # print(np.squeeze(np.array(inputs)).shape, np.squeeze(np.array(targets)).shape)
        self.model.fit(np.squeeze(np.array(inputs)), np.squeeze(np.array(targets)), epochs=5,
                       batch_size=len(training_batch), verbose=0)

        # Update target weights
        self.update_target()

    def predict(self, state, action, use_target_network=False):
        if use_target_network:
            return self.target_network.predict(np.concatenate([state, action], axis=1), batch_size=1)
        else:
            return self.model.predict(np.concatenate([state, action], axis=1), batch_size=1)
