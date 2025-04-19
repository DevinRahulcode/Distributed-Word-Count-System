import argparse


def start_node(role, letter_range=None, port=None):
    if role == "coordinator":
        print("Starting the Coordinator")
        from coordinator import run_coordinator
        run_coordinator()

    elif role in ["proposer", "proposerTwo"]:
        proposer_port = 5002 if role == "proposer" else 5006
        print(f"Starting {role} for range {letter_range} on port {proposer_port}...")
        module = proposer_port == 5002 and 'proposer' or 'proposerTwo'
        from_module = __import__(module)
        from_module.run_proposer(letter_range)

    elif role in ["acceptor", "acceptorTwo"]:
        acceptor_port = 5003 if role == "acceptor" else 5005
        print(f"Starting {role} on port {acceptor_port}...")
        module = acceptor_port == 5003 and 'acceptor' or 'acceptorTwo'
        from_module = __import__(module)
        from_module.run_acceptor()

    elif role == "learner":
        print("Starting the Learner node")
        from learner import run_learner
        run_learner()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Running a Node")
    parser.add_argument("--role", type=str,
                        choices=["coordinator", "proposer", "proposerTwo", "acceptor", "acceptorTwo", "learner"],
                        help="Role of the node to start.")
    parser.add_argument("--range", type=str, nargs='?',
                        help="Letter range assigned to proposer Optional for non-proposer roles.")
    parser.add_argument("--port", type=int, nargs='?', default=0, help="Port for proposer or acceptor.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.role in ["proposer", "proposerTwo"] and not args.range:
        print(f"Error: range is required for {args.role} role.")
    else:
        start_node(args.role, letter_range=args.range, port=args.port)