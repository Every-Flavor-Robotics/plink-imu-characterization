import os
import numpy as np
import matplotlib.pyplot as plt
import click

@click.command()
@click.argument('experiment_name')
def plot_data(experiment_name):
    experiment_dir = f'experiments/{experiment_name}'
    data_file = os.path.join(experiment_dir, 'data.npz')
    if not os.path.exists(data_file):
        print(f"Data file '{data_file}' not found.")
        return

    # Load the data
    data = np.load(data_file)
    timestamps = data['timestamps']
    external_accel = data['external_accel']
    external_gyro = data['external_gyro']
    external_mag = data['external_mag']
    internal_accel = data['internal_accel']
    internal_gyro = data['internal_gyro']
    internal_mag = data['internal_mag']

    # Plot settings
    plt.rcParams['figure.figsize'] = (12, 8)

    # Accelerometer Data
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[0].plot(timestamps, external_accel[:, 0], label='External Accel X')
    axs[0].plot(timestamps, internal_accel[:, 0], label='Internal Accel X', linestyle='--')
    axs[0].set_ylabel('Acceleration X (m/s²)')
    axs[0].legend()

    axs[1].plot(timestamps, external_accel[:, 1], label='External Accel Y')
    axs[1].plot(timestamps, internal_accel[:, 1], label='Internal Accel Y', linestyle='--')
    axs[1].set_ylabel('Acceleration Y (m/s²)')
    axs[1].legend()

    axs[2].plot(timestamps, external_accel[:, 2], label='External Accel Z')
    axs[2].plot(timestamps, internal_accel[:, 2], label='Internal Accel Z', linestyle='--')
    axs[2].set_xlabel('Time (s)')
    axs[2].set_ylabel('Acceleration Z (m/s²)')
    axs[2].legend()

    plt.suptitle('Accelerometer Data Comparison')
    plt.tight_layout()
    plt.savefig(os.path.join(experiment_dir, 'accelerometer_data_comparison.png

    # Gyroscope Data
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[0].plot(timestamps, external_gyro[:, 0], label='External Gyro X')
    axs[0].plot(timestamps, internal_gyro[:, 0], label='Internal Gyro X', linestyle='--')
    axs[0].set_ylabel('Angular Velocity X (°/s)')
    axs[0].legend()

    axs[1].plot(timestamps, external_gyro[:, 1], label='External Gyro Y')
    axs[1].plot(timestamps, internal_gyro[:, 1], label='Internal Gyro Y', linestyle='--')
    axs[1].set_ylabel('Angular Velocity Y (°/s)')
    axs[1].legend()

    axs[2].plot(timestamps, external_gyro[:, 2], label='External Gyro Z')
    axs[2].plot(timestamps, internal_gyro[:, 2], label='Internal Gyro Z', linestyle='--')
    axs[2].set_xlabel('Time (s)')
    axs[2].set_ylabel('Angular Velocity Z (°/s)')
    axs[2].legend()

    plt.suptitle('Gyroscope Data Comparison')
    plt.tight_layout()
    plt.savefig(os.path.join(experiment_dir, 'gyroscope_data_comparison.png'))

    # Magnetometer Data
    fig, axs = plt.subplots(3, 1, sharex=True)
    axs[0].plot(timestamps, external_mag[:, 0], label='External Mag X')
    axs[0].plot(timestamps, internal_mag[:, 0], label='Internal Mag X', linestyle='--')
    axs[0].set_ylabel('Magnetic Field X (µT)')
    axs[0].legend()

    axs[1].plot(timestamps, external_mag[:, 1], label='External Mag Y')
    axs[1].plot(timestamps, internal_mag[:, 1], label='Internal Mag Y', linestyle='--')
    axs[1].set_ylabel('Magnetic Field Y (µT)')
    axs[1].legend()

    axs[2].plot(timestamps, external_mag[:, 2], label='External Mag Z')
    axs[2].plot(timestamps, internal_mag[:, 2], label='Internal Mag Z', linestyle='--')
    axs[2].set_xlabel('Time (s)')
    axs[2].set_ylabel('Magnetic Field Z (µT)')
    axs[2].legend()

    plt.suptitle('Magnetometer Data Comparison')
    plt.tight_layout()
    plt.savefig(os.path.join(experiment_dir, 'magnetometer_data_comparison.png'))

if __name__ == '__main__':
    plot_data()