import tensorflow as tf

def build_dense_network(network_sizes, activation='relu'):
    networks = list()
    for i, network_size in enumerate(network_sizes):
        networks.append(tf.keras.layers.Dense(network_size, activation=activation, name=f'dense_network_{i}'))
        networks.append(tf.keras.layers.BatchNormalization(name=f'batch_norm_{i}'))

    return networks

