### Open Ended Learning

Here, we try to simulate the state-of-the-art models for human memory storage. We start from the model described in Baddeley (2012) on the Working Memory, which is a continuation of the work shown in the book Working Memory, Thought and Action.

We have a collection of `fluid` and `crystalized` systems in the following structure:

- Central Executive 
     - Visuo-spatial sketch-pad
     - Episodic Buffer
     - Phonological Loop

In the crystallized systems we have:

- Visual semantics
- episodic LTM
- Language

```
        .
        ├── central_executive
        │   ├── central_executive.py
        │   ├── episodic_buffer
        │   │   └── episodic_buffer.py
        │   ├── episodic_LTM
        │   │   └── episodic_ltm.py
        │   ├── knowldege
        │   │   ├── bayesian_knowledge.py
        │   │   ├── hebbian_knowledge.py
        │   │   ├── knowledge.py
        │   │   └── markovian_knowledge.py
        │   └── phonological_loop
        │       ├── bayesian_loop.py
        │       ├── neural_network_loop.py
        │       └── phonological_loop.py
        ├── consolidator
        │   ├── cluster_consolidator.py
        │   └── knowledge_consolidator.py
        ├── environment.yml
        ├── haveiseen
        │   └── haveiseen.py
        ├── LICENSE
        ├── observations
        │   ├── mnist_observations.py
        │   └── observations.py
        ├── README.md
        └── test
            └── test.py
```
