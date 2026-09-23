??? info "Know the Term: Neural network"
    A **neural network** is a mathematical model loosely inspired by the brain. It is made of
    many simple units ("neurons") arranged in layers. Each unit takes in numbers, multiplies them
    by adjustable settings called **weights** (also called **parameters**), adds them up and
    passes the result on to the next layer. During **training**, the network sees millions of
    examples, and after each one its weights are nudged slightly so that its output gets closer
    to the right answer. Nobody writes the rules by hand; the rules end up spread across the
    weights. A **deep** network simply has many layers, and today's large language models have
    billions of weights.

    **Analogy:** a huge mixing desk with billions of small dials. Training is a patient sound
    engineer turning each dial a fraction at a time until the music sounds right.

    **Why you care:** because the "knowledge" is spread across billions of weights, nobody can
    open the model and point to the line where a fact or a bias lives. That is why we test AI
    by checking its outputs, not by reading its rules.
