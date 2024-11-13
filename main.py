from collections import defaultdict

class State:
    def __init__(self, name, production, dot, start, end):
        self.name = name
        self.production = production
        self.dot = dot
        self.start = start
        self.end = end

    def next_symbol(self):
        if self.dot < len(self.production):
            return self.production[self.dot]
        return None

    def is_complete(self):
        return self.dot >= len(self.production)

    def __eq__(self, other):
        return (self.name == other.name and
                self.production == other.production and
                self.dot == other.dot and
                self.start == other.start and
                self.end == other.end)

    def __hash__(self):
        return hash((self.name, tuple(self.production), self.dot, self.start, self.end))

    def __repr__(self):
        prod = self.production.copy()
        prod.insert(self.dot, '•')
        prod_str = ' '.join(prod)
        return f"[{self.name} → {prod_str}, {self.start}, {self.end}]"

class EarleyParser:
    def __init__(self, grammar, start_symbol):
        self.grammar = defaultdict(list)
        for lhs, rhs_list in grammar.items():
            for rhs in rhs_list:
                self.grammar[lhs].append(rhs)
        self.start_symbol = start_symbol

    def parse(self, tokens):
        tokens.append('EOS')
        chart = [set() for _ in range(len(tokens) + 1)]
        start_state = State('γ', [self.start_symbol], 0, 0, 0)
        chart[0].add(start_state)

        for i in range(len(tokens)):
            added = True
            new_states = set()
            while added:
                added = False
                for state in list(chart[i]):
                    if not state.is_complete():
                        next_sym = state.next_symbol()
                        if next_sym in self.grammar:
                            for prod in self.grammar[next_sym]:
                                new_state = State(next_sym, prod, 0, i, i)
                                if new_state not in chart[i]:
                                    chart[i].add(new_state)
                                    new_states.add(new_state)
                                    added = True
                        elif next_sym == tokens[i]:
                            new_state = State(state.name, state.production, state.dot + 1, state.start, i + 1)
                            if new_state not in chart[i + 1]:
                                chart[i + 1].add(new_state)
                                new_states.add(new_state)
                                added = True
                    else:
                        for prev_state in chart[state.start]:
                            if not prev_state.is_complete() and prev_state.next_symbol() == state.name:
                                new_state = State(prev_state.name, prev_state.production, prev_state.dot + 1,
                                                  prev_state.start, i)
                                if new_state not in chart[i]:
                                    chart[i].add(new_state)
                                    new_states.add(new_state)
                                    added = True
            # Display only the important states
            self.display_important_states(chart, i, tokens, new_states)

        for state in chart[len(tokens) - 1]:
            if (state.name == 'γ' and state.is_complete() and state.start == 0 and
                    state.end == len(tokens) - 1):
                return True
        return False

    def display_important_states(self, chart, position, tokens, new_states):
        word = tokens[position] if position < len(tokens) - 1 else 'EOS'
        for idx in range(position + 1):
            states = chart[idx]
            important_states = [state for state in states if self.is_important(state, new_states)]
            if not important_states:
                continue
            for state in important_states:
                state_text = self.format_state(state)

    def is_important(self, state, new_states):
        # Define criteria for important states
        return (
            state.is_complete() or
            state.name == self.start_symbol or
            state in new_states
        )

    def format_state(self, state):
        lhs = f"[bold]{state.name}[/bold]"
        rhs = []
        for idx, symbol in enumerate(state.production):
            if idx == state.dot:
                rhs.append("[green]•[/green]")
            if symbol in self.grammar:
                rhs.append(f"[blue]{symbol}[/blue]")
            else:
                rhs.append(f"[yellow]{symbol}[/yellow]")
        if state.dot == len(state.production):
            rhs.append("[green]•[/green]")
        rhs_str = ' '.join(rhs)
        return f"{lhs} → {rhs_str}   [{state.start}, {state.end}]"

# Example usage
if __name__ == "__main__":
    # Define the grammar
    grammar = {
        'S': [['NP', 'VP']],
        'NP': [['Det', 'Noun']],
        'VP': [['Verb', 'NP']],
        'Det': [['the'], ['a']],
        'Noun': [['cat'], ['dog']],
        'Verb': [['sees'], ['pets']]
    }

    parser = EarleyParser(grammar, 'S')

    # Tokenize the input sentence
    sentence = 'the dog sees a cat'.split()
    result = parser.parse(sentence)

    print(f"\nSentence {'is' if result else 'is not'} in the language.")
