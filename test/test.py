#!/usr/bin/env python3

import time
import threading
from dataclasses import dataclass

from pymavlink import mavutil


# ============================================================
# CONFIGURATION — ARDUPILOT DRONES ONLY
# ============================================================

DRONES = {
    1: {
        "name": "ardupilot_iris_gimbal_0",
        "type": "ardupilot",
        "endpoint": "udp:0.0.0.0:14550",
    },
    2: {
        "name": "ardupilot_iris_gimbal_1",
        "type": "ardupilot",
        "endpoint": "udp:0.0.0.0:14560",
    },
    3: {
        "name": "ardupilot_iris_gimbal_2",
        "type": "ardupilot",
        "endpoint": "udp:0.0.0.0:14570",
    },
    4: {
        "name": "ardupilot_iris_gimbal_3",
        "type": "ardupilot",
        "endpoint": "udp:0.0.0.0:14580",
    },
}


@dataclass
class Vehicle:
    sysid: int
    name: str
    vehicle_type: str
    endpoint: str
    master: object = None
    connected: bool = False

    def connect(self, timeout=10):
        print(f"[{self.sysid}] Connecting to {self.endpoint}")

        try:
            self.master = mavutil.mavlink_connection(
                self.endpoint,
                source_system=255,
                source_component=190,
            )

            hb = self.master.wait_heartbeat(timeout=timeout)

            if hb is None:
                print(f"[{self.sysid}] Heartbeat timeout")
                return False

            # Confirm that the responding vehicle matches
            # the expected MAVLink system ID.
            actual_sysid = self.master.target_system
            if actual_sysid != self.sysid:
                print(
                    f"[{self.sysid}] WARNING: expected SYSID "
                    f"{self.sysid}, received SYSID {actual_sysid}"
                )

            self.connected = True
            print(f"[{self.sysid}] Connected: {self.name}")
            return True

        except Exception as exc:
            print(f"[{self.sysid}] Connection failed: {exc}")
            return False

    def _require_connection(self):
        if not self.connected or self.master is None:
            raise RuntimeError(f"Drone {self.sysid} is not connected")

    def wait_command_ack(self, command, timeout=5):
        """Wait for an ACK matching both command and vehicle SYSID."""
        self._require_connection()
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            msg = self.master.recv_match(
                type="COMMAND_ACK",
                blocking=True,
                timeout=0.5,
            )

            if msg is None:
                continue

            if (
                msg.get_srcSystem() == self.sysid
                and msg.command == command
            ):
                return msg.result

        return None

    def command_long(self, command, params=None):
        self._require_connection()
        params = params or [0] * 7

        self.master.mav.command_long_send(
            self.sysid,
            self.master.target_component,
            command,
            0,
            *params,
        )

    def set_mode(self, mode):
        self._require_connection()
        mode_map = self.master.mode_mapping()

        if not mode_map or mode not in mode_map:
            print(f"[{self.sysid}] Mode unavailable: {mode}")
            return False

        self.master.set_mode(mode_map[mode])
        print(f"[{self.sysid}] Requested mode: {mode}")
        return True

    def arm(self):
        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
        print(f"[{self.sysid}] Requesting arm")

        self.command_long(command, [1, 0, 0, 0, 0, 0, 0])
        result = self.wait_command_ack(command)

        if result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print(f"[{self.sysid}] Arm accepted")
            return True

        print(f"[{self.sysid}] Arm not confirmed; ACK={result}")
        return False

    def disarm(self):
        command = mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM
        print(f"[{self.sysid}] Requesting disarm")

        self.command_long(command, [0, 0, 0, 0, 0, 0, 0])
        result = self.wait_command_ack(command)

        if result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print(f"[{self.sysid}] Disarm accepted")
            return True

        print(f"[{self.sysid}] Disarm not confirmed; ACK={result}")
        return False

    def takeoff(self, altitude):
        if altitude <= 0:
            raise ValueError("Takeoff altitude must be positive")

        # ArduCopter GUIDED mode is required.
        if not self.set_mode("GUIDED"):
            return False

        if not self.arm():
            print(f"[{self.sysid}] Takeoff cancelled: arm not confirmed")
            return False

        command = mavutil.mavlink.MAV_CMD_NAV_TAKEOFF
        self.command_long(
            command,
            [0, 0, 0, float("nan"), 0, 0, float(altitude)],
        )

        result = self.wait_command_ack(command)
        print(f"[{self.sysid}] Takeoff ACK={result}")
        return result == mavutil.mavlink.MAV_RESULT_ACCEPTED

    def move_local(self, north, east, down, duration=5):
        """
        Send a LOCAL_NED position target in metres.

        north > 0: north
        east  > 0: east
        down  < 0: above the local origin

        Repeated setpoints maintain the target for `duration`
        seconds. This does not guarantee the vehicle has arrived.
        """
        self._require_connection()

        if duration <= 0:
            raise ValueError("Duration must be positive")

        if not self.set_mode("GUIDED"):
            return False

        # Ignore velocity, acceleration, yaw and yaw rate.
        type_mask = (
            (1 << 3) | (1 << 4) | (1 << 5) |
            (1 << 6) | (1 << 7) | (1 << 8) |
            (1 << 10)
        )

        print(
            f"[{self.sysid}] Target LOCAL_NED: "
            f"N={north}, E={east}, D={down}"
        )

        deadline = time.monotonic() + duration

        while time.monotonic() < deadline:
            self.master.mav.set_position_target_local_ned_send(
                int(time.monotonic() * 1000) & 0xFFFFFFFF,
                self.sysid,
                self.master.target_component,
                mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                type_mask,
                float(north),
                float(east),
                float(down),
                0, 0, 0,       # velocity
                0, 0, 0,       # acceleration
                0, 0,           # yaw, yaw rate
            )
            time.sleep(0.1)

        print(f"[{self.sysid}] Setpoint stream finished")
        return True

    def position(self):
        self._require_connection()

        msg = self.master.recv_match(
            type="LOCAL_POSITION_NED",
            blocking=True,
            timeout=2,
        )

        if msg is None:
            print(f"[{self.sysid}] No local position received")
            return None

        print(
            f"[{self.sysid}] N={msg.x:.2f} m, "
            f"E={msg.y:.2f} m, D={msg.z:.2f} m"
        )
        return msg.x, msg.y, msg.z

    def status(self):
        self._require_connection()

        msg = self.master.recv_match(
            type="HEARTBEAT",
            blocking=True,
            timeout=2,
        )

        if msg is None:
            print(f"[{self.sysid}] Heartbeat unavailable")
            return

        armed = bool(
            msg.base_mode
            & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        )

        print(
            f"[{self.sysid}] {self.name} | "
            f"armed={armed} | mode={mavutil.mode_string_v10(msg)}"
        )


class Swarm:
    def __init__(self):
        self.vehicles = {
            sysid: Vehicle(
                sysid=sysid,
                name=cfg["name"],
                vehicle_type=cfg["type"],
                endpoint=cfg["endpoint"],
            )
            for sysid, cfg in DRONES.items()
        }

    def get(self, sysid):
        if sysid not in self.vehicles:
            raise ValueError(f"Unknown drone SYSID: {sysid}")
        vehicle = self.vehicles[sysid]
        if not vehicle.connected:
            raise RuntimeError(f"Drone {sysid} is not connected")
        return vehicle

    def connect_all(self):
        print("\nConnecting to ArduPilot swarm...")
        for vehicle in self.vehicles.values():
            vehicle.connect()

        print("\nConnection summary:")
        for sid, vehicle in self.vehicles.items():
            state = "CONNECTED" if vehicle.connected else "FAILED"
            print(f"  {sid}: {state} — {vehicle.name}")

    def run_all(self, method, *args):
        """Run commands concurrently across connected drones."""
        threads = []

        def worker(vehicle):
            try:
                getattr(vehicle, method)(*args)
            except Exception as exc:
                print(f"[{vehicle.sysid}] {method} failed: {exc}")

        for vehicle in self.vehicles.values():
            if vehicle.connected:
                thread = threading.Thread(
                    target=worker,
                    args=(vehicle,),
                    daemon=True,
                )
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

    def status_all(self):
        for vehicle in self.vehicles.values():
            if vehicle.connected:
                vehicle.status()


HELP = """
Commands
--------
connect
vehicles
status
arm <id|all>
disarm <id|all>
takeoff <id|all> <altitude_m>
move <id> <north_m> <east_m> <down_m> [duration_s]
moveall <north_m> <east_m> <down_m> [duration_s]
pos <id>
mode <id> <mode>
help
quit

Examples
--------
connect
status
arm 1
takeoff 1 3
move 1 5 0 -3 5
moveall 5 0 -3 5
pos 1
"""


def main():
    swarm = Swarm()
    print("InsynQ — ArduPilot Swarm REPL (SYSIDs 1–4)")
    print(HELP)

    while True:
        try:
            parts = input("swarm> ").strip().split()
            if not parts:
                continue

            cmd = parts[0].lower()

            if cmd in ("quit", "exit"):
                break
            elif cmd in ("help", "?"):
                print(HELP)
            elif cmd == "connect":
                swarm.connect_all()
            elif cmd == "vehicles":
                for sid, v in swarm.vehicles.items():
                    print(f"{sid}: {v.name} — {v.endpoint}")
            elif cmd == "status":
                swarm.status_all()
            elif cmd in ("arm", "disarm"):
                target = parts[1].lower()
                method = cmd
                if target == "all":
                    swarm.run_all(method)
                else:
                    getattr(swarm.get(int(target)), method)()
            elif cmd == "takeoff":
                target, altitude = parts[1].lower(), float(parts[2])
                if target == "all":
                    swarm.run_all("takeoff", altitude)
                else:
                    swarm.get(int(target)).takeoff(altitude)
            elif cmd == "move":
                sid = int(parts[1])
                north, east, down = map(float, parts[2:5])
                duration = float(parts[5]) if len(parts) > 5 else 5
                swarm.get(sid).move_local(
                    north, east, down, duration
                )
            elif cmd == "moveall":
                north, east, down = map(float, parts[1:4])
                duration = float(parts[4]) if len(parts) > 4 else 5
                swarm.run_all(
                    "move_local", north, east, down, duration
                )
            elif cmd == "pos":
                swarm.get(int(parts[1])).position()
            elif cmd == "mode":
                swarm.get(int(parts[1])).set_mode(parts[2].upper())
            else:
                print("Unknown command. Type 'help'.")

        except (ValueError, IndexError) as exc:
            print(f"Invalid command arguments: {exc}")
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit.")
        except Exception as exc:
            print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()
