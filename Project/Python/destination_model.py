from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np
import copy


class DestinationModel:

	def __init__(self , stop_connections, gamma=0.9):
		self.model = Sequential([
		    Dense(200, input_dim=625 + 24),
		    Activation('relu'),
		    Dense(100),
		    Activation('relu'),
		    Dense(1),
		    Activation('linear'), 
		    ])

		self.model.compile(optimizer='adam',
              loss='mse')
		self.connections = stop_connections 
		self.frozen_model = None # TODO
		self.gamma = gamma

	def get_max_qscore(self, action_vec, next_state):
		possible_actions_id = self.connections[np.where(action_vec == 1)[0][0]]

		# generate possible actions
		possible_actions = [np.eye(1 , len(self.connections), stop) for stop in possible_actions_id]
		possible_actions.append(action_vec)

		best_qscore = - np.Inf

		# get reward targets
		for next_action_vec in possible_actions:

			qscore = self.predict(next_state, next_action_vec) 

			if qscore > best_qscore:
				best_qscore = qscore

		return best_qscore


	def train(self, training_batch):
		# input points ( S[t-1], A[t-1], R[t-1], S[t] )

		# Preprocessing: generate next state + long-term reward
		
		inputs = []
		targets = []

		for state, action_vec, reward, next_state in training_batch:

			qscore = self.get_max_qscore(action_vec, next_state)

			inputs.append(np.concatenate([state,action_vec], axis=1).reshape((1,-1)))
			targets.append(reward + self.gamma * qscore)

		print(np.squeeze(np.array(inputs)).shape, np.squeeze(np.array(targets)).shape)
		self.model.fit(np.squeeze(np.array(inputs)), np.squeeze(np.array(targets)), nb_epoch=1, batch_size=len(training_batch), verbose=1)
		


	def predict(self, state, action):
		return self.model.predict(np.concatenate([state,action], axis=1), batch_size=1)
