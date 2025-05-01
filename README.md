# Distributed-Word-Count-System


   # Coordinator
   python main.py --role coordinator

   # Proposer
   python main.py --role proposer --range A-M --port 5002

   # ProposerTwo
   python main.py --role proposerTwo --range N-Z --port 5006

   # Acceptor
   python script.py --role acceptor --port 5003

   # AcceptorTwo
   python main.py --role acceptorTwo --port 5005

   # Learner (Port 5004)
   python main.py --role learner
