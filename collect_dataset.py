import click
from click import secho
import time
import os
import numpy as np
import board

# Accel and Gyro imports
from adafruit_lsm6ds import Rate as LSM6DSRate
from adafruit_lsm6ds import AccelRange, GyroRange
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX

from adafruit_lis3mdl import Rate as LIS3MDLRate
from adafruit_lis3mdl import PerformanceMode, Range, OperationMode
from adafruit_lis3mdl import LIS3MDL
from pyplink import Plink


def create_experiment_dir(name: str = None):
    if name is None:
        name = time.strftime("experiment_%Y-%m-%d_%H-%M-%S")

    experiment_dir = f"experiments/{name}"

    # If it exists, raise an error
    if os.path.exists(experiment_dir):
        raise ValueError(f"Directory {experiment_dir} already exists")

    os.makedirs(experiment_dir)
    return experiment_dir


def setup_external_imu():
    i2c = board.I2C()  # uses board.SCL and board.SDA
    gyro_accel = LSM6DSOX(i2c)
    mag = LIS3MDL(i2c)

    gyro_accel.accelerometer_range = AccelRange.RANGE_8G
    gyro_accel.gyro_range = GyroRange.RANGE_2000_DPS
    gyro_accel.accelerometer_data_rate = LSM6DSRate.RATE_208_HZ
    gyro_accel.gyro_data_rate = LSM6DSRate.RATE_208_HZ

    mag.range = Range.RANGE_4_GAUSS
    mag.data_rate = LIS3MDLRate.RATE_300_HZ
    mag.performance_mode = PerformanceMode.HIGH_PERFORMANCE
    mag.operation_mode = OperationMode.CONTINUOUS

    return gyro_accel, mag


def setup_plink():
    plink = Plink()
    plink.connect()

    return plink


@click.command()
@click.argument("experiment_name")
@click.option(
    "--data_collection_period", default=10, help="Period in seconds to collect data"
)
def main(experiment_name: str, data_collection_period: int = 10):

    experiment_dir = create_experiment_dir(experiment_name)

    secho(
        f"Starting experiment {experiment_name} in directory {experiment_dir}",
        fg="green",
    )

    gyro_accel, mag = setup_external_imu()
    plink = setup_plink()

    # Three second countdown
    for i in range(5, 0, -1):
        secho(f"Starting in {i} seconds", fg="yellow")
        time.sleep(1)

    plink.channel_1.power_command = 1.0

    secho("Starting data collection", fg="green")

    start_time = time.perf_counter()  # Use perf_counter for higher resolution
    end_time = start_time + data_collection_period

    # Preallocate arrays
    estimated_sample_rate = 1000  # Hz
    MAX_SAMPLES = int(
        data_collection_period * estimated_sample_rate * 1.1
    )  # Extra buffer

    timestamps = np.zeros(MAX_SAMPLES, dtype=np.float64)

    external_accel_data_array = np.zeros((MAX_SAMPLES, 3), dtype=np.float32)
    external_gyro_data_array = np.zeros((MAX_SAMPLES, 3), dtype=np.float32)
    external_mag_data_array = np.zeros((MAX_SAMPLES, 3), dtype=np.float32)

    internal_accel_data_array = np.zeros((MAX_SAMPLES, 3), dtype=np.float32)
    internal_gyro_data_array = np.zeros((MAX_SAMPLES, 3), dtype=np.float32)
    internal_mag_data_array = np.zeros((MAX_SAMPLES, 3), dtype=np.float32)

    sample_idx = 0

    # Set up variables for time management
    next_sample_time = start_time
    sample_period = 1.0 / estimated_sample_rate

    while True:
        current_time = time.perf_counter()
        if current_time >= end_time:
            break

        # Wait until the next sample time
        if current_time < next_sample_time:
            time_to_wait = next_sample_time - current_time
            if time_to_wait > 0:
                time.sleep(time_to_wait)

        # Record the precise timestamp
        timestamp = time.perf_counter() - start_time

        # Read data from sensors
        try:
            external_accel_data = gyro_accel.acceleration
            external_gyro_data = gyro_accel.gyro
            external_mag_data = mag.magnetic

            internal_accel_data = plink.imu.accel
            internal_gyro_data = plink.imu.gyro
            internal_mag_data = plink.imu.mag
        except Exception as e:
            secho(f"Error reading sensors: {e}", fg="red")
            continue  # Skip this sample

        if sample_idx >= MAX_SAMPLES:
            secho(
                "Maximum sample capacity reached. Ending data collection.", fg="yellow"
            )
            break

        timestamps[sample_idx] = timestamp

        external_accel_data_array[sample_idx, :] = external_accel_data
        external_gyro_data_array[sample_idx, :] = external_gyro_data
        external_mag_data_array[sample_idx, :] = external_mag_data

        internal_accel_data_array[sample_idx, :] = internal_accel_data
        internal_gyro_data_array[sample_idx, :] = internal_gyro_data
        internal_mag_data_array[sample_idx, :] = internal_mag_data

        sample_idx += 1
        next_sample_time += sample_period

    # Slice the arrays to the actual number of samples collected
    timestamps = timestamps[:sample_idx]
    external_accel_data_array = external_accel_data_array[:sample_idx, :]
    external_gyro_data_array = external_gyro_data_array[:sample_idx, :]
    external_mag_data_array = external_mag_data_array[:sample_idx, :]

    internal_accel_data_array = internal_accel_data_array[:sample_idx, :]
    internal_gyro_data_array = internal_gyro_data_array[:sample_idx, :]
    internal_mag_data_array = internal_mag_data_array[:sample_idx, :]

    # Save the data to npz file
    np.savez(
        os.path.join(experiment_dir, "data.npz"),
        timestamps=timestamps,
        external_accel=external_accel_data_array,
        external_gyro=external_gyro_data_array,
        external_mag=external_mag_data_array,
        internal_accel=internal_accel_data_array,
        internal_gyro=internal_gyro_data_array,
        internal_mag=internal_mag_data_array,
    )

    secho("Data collection complete. Data saved to 'data.npz'.", fg="green")


if __name__ == "__main__":
    main()
