#!/usr/bin/env python3

import time
import argparse

# Loader frames that create a push/pull fade effect
LOADER_FRAMES = [
    "              ", "░             ", "░░            ", "░░░           ", "░░░░          ", "▒░░░░         ", "▒▒░░░░        ", "▒▒▒░░░░       ", "▒▒▒▒░░░░      ", "▓▒▒▒▒░░░░     ", "▓▓▒▒▒▒░░░░    ", "▓▓▓▒▒▒▒░░░░   ", "▓▓▓▓▒▒▒▒░░░░  ", "▓▓▓▓▓▒▒▒▒░░░░ ", "▓▓▓▓▓▓▒▒▒▒░░░░", "▓▓▓▓▓▓▓▒▒▒▒░░░", "▓▓▓▓▓▓▓▓▒▒▒▒░░", "▓▓▓▓▓▓▓▓▓▒▒▒▒░", "▓▓▓▓▓▓▓▓▓▓▒▒▒▒", "▓▓▓▓▓▓▓▓▓▓▓▒▒▒", "▓▓▓▓▓▓▓▓▓▓▓▓▒▒", "▓▓▓▓▓▓▓▓▓▓▓▓▓▒", "▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "▓▓▓▓▓▓▓▓▓▓▓▓▓▓", "▓▓▓▓▓▓▓▓▓▓▓▓▓▒", "▓▓▓▓▓▓▓▓▓▓▓▓▒▒", "▓▓▓▓▓▓▓▓▓▓▓▒▒▒", "▓▓▓▓▓▓▓▓▓▓▒▒▒▒", "▓▓▓▓▓▓▓▓▓▒▒▒▒░", "▓▓▓▓▓▓▓▓▒▒▒▒░░", "▓▓▓▓▓▓▓▒▒▒▒░░░", "▓▓▓▓▓▓▒▒▒▒░░░░", "▓▓▓▓▓▒▒▒▒░░░░ ", "▓▓▓▓▒▒▒▒░░░░  ", "▓▓▓▒▒▒▒░░░░   ", "▓▓▒▒▒▒░░░░    ", "▓▒▒▒▒░░░░     ", "▒▒▒▒░░░░      ", "▒▒▒░░░░       ", "▒▒░░░░        ", "▒░░░░         ", "░░░░          ", "░░░           ", "░░            ", "░             ", "              ", "              ", "              ", "              ", "              ", "              ", "              ", "              ", "              "
 ]


def run_loader(duration_seconds=50, cycle_duration=1/len(LOADER_FRAMES)):
    """Run the push/pull loader animation.

    Args:
        duration_seconds: How long to run the animation
        cycle_duration: Time for one full push/pull cycle
    """
    frame_delay = cycle_duration/len(LOADER_FRAMES)
    
    n_intervals = int(duration_seconds / frame_delay)

    print()  # Add blank line before loader
    
    start = time.time()
    for i in range(n_intervals):
        # Go backwards through loader frames for push/pull effect
        loader_frame = LOADER_FRAMES[i % len(LOADER_FRAMES)]

        # Calculate which "turn" (cycle) we're on
        turn = i // len(LOADER_FRAMES)

        print(f"\rThinking {loader_frame}   {time.time()-start:.0f}                   ", end="", flush=True)
        time.sleep(frame_delay)

    print()  # New line when done


def main():
    parser = argparse.ArgumentParser(description="Push/pull text loader animation")
    parser.add_argument(
        "--duration",
        type=float,
        default=50,
        help="Duration in seconds (default: 50)"
    )
    parser.add_argument(
        "--cycle-duration",
        type=float,
        default=1,
        help="Time for one full push/pull cycle in seconds (default:1)"
    )

    args = parser.parse_args()

    try:
        run_loader(duration_seconds=args.duration, cycle_duration=args.cycle_duration)
    except KeyboardInterrupt:
        print("\n\nStopped by user")

if __name__ == "__main__":
    main()