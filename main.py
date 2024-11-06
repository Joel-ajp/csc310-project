# The point of this parsing algoritm is to return true or false based on wheter or not the input string is a valid sentence in the grammar.
class EarleyParser:
    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.start_symbol = start_symbol

    def parse(self, string):
        n = len(string)
        # Initialize the chart, an array of sets for each position
        chart = [set() for _ in range(n + 1)]
        # Seed the chart with the start symbol
        chart[0].add((self.start_symbol, 0, 0))

        for i in range(n + 1):
            for state in list(chart[i]):
                rule, dot, start = state
                if dot < len(rule) and rule[dot] in self.grammar:  # non-terminal (prediction)
                    self.predictor(chart, rule[dot], i)
                elif dot < len(rule):  # terminal (scan)
                    self.scanner(chart, state, i, string)
                else:  # completion
                    self.completer(chart, state, i)

        # Check if the parse was successful
        final_state = (self.start_symbol, len(self.start_symbol), 0)
        return final_state in chart[n]

    def predictor(self, chart, non_terminal, index):
        """Add all productions for a non-terminal in the chart."""
        for production in self.grammar[non_terminal]:
            chart[index].add((production, 0, index))

    def scanner(self, chart, state, index, string):
        """Match terminal symbols with the input string."""
        rule, dot, start = state
        if index < len(string) and rule[dot] == string[index]:
            chart[index + 1].add((rule, dot + 1, start))

    def completer(self, chart, state, index):
        """Complete and add states when all symbols in a rule have been matched."""
        rule, dot, start = state
        for prev_state in list(chart[start]):
            prev_rule, prev_dot, prev_start = prev_state
            if prev_dot < len(prev_rule) and prev_rule[prev_dot] == rule:
                chart[index].add((prev_rule, prev_dot + 1, prev_start))

# Example usage
grammar = {
    'S': [['NP', 'VP']],
    'NP': [['Det', 'N']],
    'VP': [['V', 'NP']],
    'Det': [['the']],
    'N': [['dog'], ['cat']],
    'V': [['chased'], ['saw']]
}

parser = EarleyParser(grammar, 'S')
input_string = "the dog chased the cat".split()
print(parser.parse(input_string))  
