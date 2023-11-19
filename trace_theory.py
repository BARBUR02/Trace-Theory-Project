import re
import json
from typing import Any, Iterable
import networkx as nx

from dekiert_graph import create_dekiert_graph

CONFIGURATION_FILE = "input.json"

ParsedAction = tuple[str, list[str]]
Stacks = dict[str, list[str]]


def create_graphs(actions: dict[str, Any]) -> tuple[nx.Graph, nx.Graph]:
    labels = list(actions.keys())
    D = create_starting_graph_from_labels(labels)
    I = create_starting_graph_from_labels(labels)
    for i, label1 in enumerate(labels):
        for label2 in labels[i:]:
            if dependent(actions[label1], actions[label2]):
                D[label1].append(label2)
                D[label2].append(label1)
            else:
                I[label1].append(label2)
                I[label2].append(label1)
    return nx.DiGraph(D), nx.DiGraph(I)


def dependent(action1: ParsedAction, action2: ParsedAction) -> bool:
    return action1 == action2 or action1[0] in action2[1] or action2[0] in action1[1]


def create_starting_graph_from_labels(labels: list[str]) -> dict[str, list[Any]]:
    return dict([(label, []) for label in labels])


def parse_input(
    input: dict[str, str]
) -> tuple[dict[str, ParsedAction], list[str], str]:
    actions = extract_actions(input["actions"])
    A = sorted(actions.keys())
    w = input["w"]
    return actions, A, w


def extract_actions(actions_input: str) -> dict[str, ParsedAction]:
    return dict([label_actions(line) for line in actions_input.split("\n")])


def label_actions(action_line: str) -> tuple[str, ParsedAction]:
    action_label, action = action_line.split(":=")
    label, left_action_part = extract_lowercase_letters(action_label)
    return label, (
        left_action_part,
        list(set(extract_lowercase_letters(action))),
    )


# Extracting left/right dependencies of equations from five str format
def extract_lowercase_letters(input_string: str) -> list[str]:
    return re.findall(r"[a-z]", input_string)


# Compute Foata Normals Forms
def compute_foata_normal_form(word: str, D: nx.DiGraph) -> list[list[str]]:
    stack = create_starting_graph_from_labels(D.nodes)
    #  Building stack
    for letter in word[::-1]:
        stack[letter].append(letter)
        for neighbor in D.neighbors(letter):
            if not neighbor == letter:
                stack[neighbor].append("")  # empty in order to be evaluated to False :)

    # print_stack(stack)
    foata_groups = []
    remove_markers = False
    while not stack_empty(stack):
        if foata_group := iterate_stack(stack.values(), remove_markers):
            foata_groups.append(foata_group)
        # print_stack(stack)
        remove_markers = not remove_markers
    return foata_groups


def print_stack(stacks: dict[str, list[str]]) -> None:
    for stack in stacks:
        print(f"{stack}: {stacks[stack]}")


def iterate_stack(stack_set: Iterable[list[str]], remove_markers: bool) -> list[str]:
    iteration_group = []
    if remove_markers:
        for stack in stack_set:
            if stack and stack[-1] == "":
                stack.pop()
    else:
        for stack in stack_set:
            if stack:
                if popped := stack.pop():
                    iteration_group.append(popped)
                elif remove_markers is False:
                    stack.append("")

    return iteration_group


def value_present(stack_set: Iterable[list[str]]) -> bool:
    return any(stack[-1] if stack else False for stack in stack_set)


def stack_empty(stack_dict) -> bool:
    return all([len(stack) == 0 for stack in stack_dict.values()])


def print_results(D: nx.DiGraph, I: nx.DiGraph, foata_normal_form: list[list[str]]):
    result = (
        "RESULTS:\n"
        f"\tD = {D.edges}\n"
        f"\tI = {I.edges}\n"
        f"\tFNF(|w|) = {parse_fnf(foata_normal_form)}"
    )
    print(result)


def parse_fnf(fnf_list: list[list[str]]) -> str:
    return "".join(map(lambda x: f"({''.join(x)})", fnf_list))


if __name__ == "__main__":
    with open(CONFIGURATION_FILE) as f:
        input_data = json.load(f)

    # Parse input from json file in format from exercise description
    actions, A, word = parse_input(input_data)

    # Create Graph of Dependencies D and Independencies I
    D, I = create_graphs(actions)
    foata_normal_form = compute_foata_normal_form(word, D)
    print_results(D, I, foata_normal_form)
    dekiert_graph = create_dekiert_graph(word, D)
