import keras
import sys
import os
sys.path.append(os.path.abspath('/scratch/users/pdanie20/silicon/PD-stopping-power-ml'))
from stopping_power_ml.keras import build_fn

def change_layers( build_fn,input_size=10, dense_layers=((10,10),(20,20)), activation='linear',
            optimizer_options=[dict(loss='mean_absolute_error', optimizer='rmsprop', metrics=['mean_absolute_error']),dict(loss='mean_absolute_error', optimizer='rmsprop', metrics=['mean_absolute_error'])],regularizer=keras.regularizers.L2(0.01), use_regularizer=False):
    """Creates a list of Keras NN models with different complex architectures
    
    Args:
        input_size (int) - Number of features in input vector
        dense_layers ((int,int)) - Number of units in the dense layers
        activation (str) - Activation function in the dense layers
        use_linear_block (bool) - Whether to use the linear regression block
        optimizer_options (dict) - Any options for the optimization routine
    Returns:
        (keras.models.Model) a Keras model
    """
    
    models = [None] * len(dense_layers)
    count = 0; 

    if len(dense_layers) == 1:
        models[0] = build_fn(input_size, dense_layers[0], activation, use_linear_block=False, optimizer_options=optimizer_options[count],regularizer=regularizer,use_regularizer=use_regularizer) 
    else:
        for no_layers in dense_layers:
            model = build_fn(input_size, no_layers, activation, use_linear_block=False,
                       optimizer_options=optimizer_options[count],regularizer=regularizer,use_regularizer=use_regularizer) 
            models[count] = model         
            count += 1
    return models