from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np


class DestinationModel:

	def __init__(self):
		self.model = Sequential([
		    Dense(32, input_dim=625 + 24),
		    Activation('relu'),
		    Dense(1),
		    Activation('linear'), 
		    ])

		self.model.compile(optimizer='adam',
              loss='mse')

	def predict(self, state, action):
		return self.model.predict(np.concatenate([state,action], axis=1), batch_size=1)
