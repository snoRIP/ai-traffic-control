import sys
import os
import traceback

# Ensure the current directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from src.simulation import TrafficSimulation
except Exception:
    print("FAILED TO IMPORT src.simulation")
    traceback.print_exc()
    sys.exit(1)

def main() -> None:
    print("="*40)
    print("AI TRAFFIC CONTROL SYSTEM v2.5")
    print("Mode: Deep Reinforcement Learning (DQN)")
    print("="*40)
    
    try:
        sim = TrafficSimulation(use_drl=True)
        sim.run()
    except Exception as e:
        print("\n" + "!"*40)
        print(f"CRITICAL RUNTIME ERROR: {e}")
        print("!"*40)
        traceback.print_exc()
        # Keep console open on error
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()