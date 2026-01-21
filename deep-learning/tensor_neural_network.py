import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from keras_tuner import RandomSearch
import pickle

data = pd.read_csv('dataset/Liver_disease_data.csv')

# Separate features and target
X = data.drop(columns=['Diagnosis'])
y = data['Diagnosis']

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define a model-building function for Keras Tuner
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Define a model-building function for Keras Tuner
def build_model(hp):
    model = keras.Sequential()
    
    # Tune the number of layers
    for i in range(hp.Int('num_layers', 4, 6)):
        model.add(keras.layers.Dense(
            units=hp.Int('units_' + str(i), min_value=2, max_value=100, step=5),
            activation=hp.Choice('activation_' + str(i), ['relu', 'tanh', 'sigmoid'])
        ))
        
    model.add(keras.layers.Dense(1, activation='sigmoid'))
    
    model.compile(
        optimizer=keras.optimizers.Adam(
            hp.Choice('learning_rate', [1e-2, 1e-3, 1e-4])
        ),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

# Initialize the Keras Tuner
tuner = RandomSearch(
    build_model,
    objective='val_accuracy',
    max_trials=25,
    executions_per_trial=2,
    directory='tuner',
    project_name='liver_disease_prediction_10'
)

# Perform hyperparameter tuning
tuner.search(X_train, y_train, epochs=20, validation_split=0.2)

# Get the best model and hyperparameters
best_model = tuner.get_best_models(num_models=1)[0]
best_hyperparameters = tuner.get_best_hyperparameters(num_trials=1)[0]
print(best_model.summary())

# Train the best model
best_model.fit(X_train, y_train, epochs=50, validation_split=0.2)

# Evaluate the model on the test set
loss, accuracy = best_model.evaluate(X_test, y_test)
print(f'Test Accuracy: {accuracy:.4f}')

model_details = {}
weights = []
biases = []

for layer in best_model.layers:
    layer_weights =  layer.get_weights()
    if len(layer_weights) > 0:
        weights.append(layer_weights[0].tolist())
        biases.append(layer_weights[1].tolist())

for i in range(len(weights)):
    model_details[f"W{i+1}"] = np.array(weights[i])
    model_details[f"b{i+1}"] = np.array(biases[i])

# Save the model details to a file
with open('model_details.py', 'w') as file:
    file.write(repr(model_details))

    # Save the model details to a .pkl file
with open('model_details.pkl', 'wb') as file:
    pickle.dump(model_details, file)