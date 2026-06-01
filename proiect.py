import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient


def main():
    # 1. Initialize the ZeroMQ Client and require the regular 'sim' API
    client = RemoteAPIClient()
    sim = client.require('sim')

    # 2. Get the object handles (Rename these strings to match your scene)
    sensor_handle = sim.getObject('/senzor')
    conveyor_handle = sim.getObject('/centura')

    # Define speed limits
    normal_speed = 0.1  # Adjust as needed (m/s or rad/s)
    stop_speed = 0.0

    print("Connecting to CoppeliaSim... Make sure the simulation is running.")

    # 3. Optional: Enable 'stepping' mode so Python syncs perfectly with Coppelia's physics clock
    sim.setStepping(True)
    sim.startSimulation()
    stop = False
    try:
        # 1. Get the handle of the actual motor joint inside the conveyor
        # (Adjust '/ConveyorBelt/Joint' to match your hierarchy exactly)
        # conveyor_joint = sim.getObject('/ConveyorBelt/Joint')

        # ... (rest of your setup code) ...

        while True:
            # 1. Read the proximity sensor state
            result, distance, _, _, _ = sim.readProximitySensor(sensor_handle)

            # 2. Assign velocity based on detection
            if result == 1 or stop:
                target_speed = stop_speed
                stop = True
            else:
                target_speed = normal_speed

            # 3. Pack the Python dictionary into a buffer and send it to the conveyor
            # This directly replicates the Lua code: sim.packTable({vel=target_speed})
            packed_data = sim.packTable({'vel': target_speed})
            sim.setBufferProperty(conveyor_handle, 'customData.__ctrl__', packed_data)

            # 4. Advance the simulation step
            sim.step()

    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C to stop the simulation
        print("\nStopping simulation...")
        sim.stopSimulation()


if __name__ == '__main__':
    main()