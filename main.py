import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# Initialize the client
client = RemoteAPIClient()
sim = client.getObject('sim')


def move_arm(joint_handles, target_positions):
    """Sets the arm joints to specific radian positions."""
    for i, handle in enumerate(joint_handles):
        sim.setJointTargetPosition(handle, target_positions[i])
    time.sleep(2)  # Give the arm time to move


def control_gripper(gripper_handle, open_gripper=True):
    """Controls the youBot gripper (typically via a specific signal or joint)."""
    # In most youBot models, the gripper is controlled by a float signal
    # 0 = closed, 1 = open
    val = 1.0 if open_gripper else 0.0
    sim.setFloatSignal('youBot_gripperState', val)
    time.sleep(1)


def main():
    # 1. Get Handles
    try:
        robot = sim.getObject('/youBot')
        box = sim.getObject('/box')

        # Arm Joints
        arm_joints = [sim.getObject(f'/youBot/youBotArmJoint{i}') for i in range(5)]

        # Wheel Joints (for base movement)
        wheels = [sim.getObject(f'/youBot/rollingJoint_fl'),
                  sim.getObject(f'/youBot/rollingJoint_rl'),
                  sim.getObject(f'/youBot/rollingJoint_fr'),
                  sim.getObject(f'/youBot/rollingJoint_rr')]
    except Exception as e:
        print(f"Error: Could not find objects in scene. {e}")
        return

    # Start Simulation
    sim.startSimulation()
    print("Simulation started.")

    # 2. Initial State: Open Gripper
    control_gripper(None, open_gripper=True)

    # 3. Move Arm to "Ready" position (Radian values)
    # [Joint 1, 2, 3, 4, 5]
    ready_pos = [0, 0.5, -1.0, -1.0, 0]
    move_arm(arm_joints, ready_pos)

    # 4. Move Base Forward (Simple velocity control)
    print("Moving toward box...")
    for w in wheels:
        sim.setJointTargetVelocity(w, 2.0)
    time.sleep(2)  # Move for 2 seconds
    for w in wheels:
        sim.setJointTargetVelocity(w, 0)

    # 5. Lower Arm to pick up box
    pick_pos = [0, 1.2, -1.5, -1.2, 0]
    move_arm(arm_joints, pick_pos)

    # 6. Close Gripper
    print("Picking up box...")
    control_gripper(None, open_gripper=False)

    # 7. Lift Arm
    lift_pos = [0, 0.5, -1.0, -1.0, 0]
    move_arm(arm_joints, lift_pos)

    # 8. Move Base Backward
    print("Moving back...")
    for w in wheels:
        sim.setJointTargetVelocity(w, -2.0)
    time.sleep(2)
    for w in wheels:
        sim.setJointTargetVelocity(w, 0)

    print("Task complete.")
    time.sleep(2)
    sim.stopSimulation()


if __name__ == "__main__":
    main()