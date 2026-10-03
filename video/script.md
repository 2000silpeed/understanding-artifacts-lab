# How an LLM picks the next token

## hook {hold=0.6}
After reading context, an LLM scores possible next tokens and chooses one. [#context] A token can be a word, part of a word, or punctuation.

## logits {hold=0.5}
Toy context: [#prompt] “The cat sat on the”. Four illustrative logits are [#scores] mat 2.0, the floor token 1.0, sofa 0.3, and roof minus 0.4. These are educational values, not measured model output.

## softmax {hold=0.5}
Logits become probabilities through softmax. [#formula] It exponentiates shifted scores and normalizes them. At temperature one, mat is 60.9 percent, floor 22.4, sofa 11.1, and roof 5.5.

## temperature {hold=0.5}
Temperature changes distribution shape. [#sharp] Lower temperature sharpens it. [#flat] Higher temperature flattens it. Temperature changes variety, not correctness.

## topp {hold=0.5}
Top-p sorts probabilities and keeps the smallest prefix reaching its mass. [#sort] At p equal to 0.80, mat and floor retain 83.3 percent. [#keep] They stay, and the rest are removed. This is a mass rule.

## sample {hold=0.6}
Sampling draws a uniform number across cumulative probability. [#draw] Here u equals 0.82, so it selects floor from the filtered intervals. [#feedback] The token joins context, and the model recomputes the next step. This toy shows one step.

## outro {hold=1.0}
The loop is context, logits, probabilities, filtering, and sampling. [#caveat] These estimates predict a next token. They do not verify real-world truth.
