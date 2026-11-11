"""Многоветвевое дерево для категориальных признаков."""

from collections import defaultdict
from dataclasses import dataclass, field
from math import log2


def entropy(p):
    if p in (0, 1):
        return 0.0
    return -p * log2(p) - (1 - p) * log2(1 - p)


def gini(p):
    return 1 - p**2 - (1 - p)**2


@dataclass
class Node:
    probability: float
    size: int
    feature: str | None = None
    gain: float = 0.0
    children: dict[str, "Node"] = field(default_factory=dict)


def fit(rows, labels, features, impurity=entropy):
    """Строит дерево, используя только переданные обучающие объекты."""
    def grow(indices, remaining):
        p = sum(labels[i] for i in indices) / len(indices)
        node = Node(p, len(indices))
        if p in (0, 1) or not remaining:
            return node

        parent_impurity = impurity(p)
        best_groups = {}
        for feature in remaining:
            groups = defaultdict(list)
            for i in indices:
                groups[rows[i][feature]].append(i)
            # Неопределённость после разбиения взвешена по размерам ветвей.
            after = sum(
                len(group) / len(indices)
                * impurity(sum(labels[i] for i in group) / len(group))
                for group in groups.values()
            )
            gain = parent_impurity - after
            # Игнорируем округление около нуля. При равенстве берём первый признак.
            if gain > node.gain + 1e-12:
                node.feature, node.gain, best_groups = feature, gain, groups

        if node.feature is not None:
            unused = tuple(f for f in remaining if f != node.feature)
            node.children = {
                value: grow(best_groups[value], unused) for value in sorted(best_groups)
            }
        return node

    return grow(range(len(rows)), tuple(features))


def route(node, row):
    """Возвращает лист или внутренний узел, если нужная ветвь отсутствует."""
    while node.feature is not None:
        child = node.children.get(row[node.feature])
        if child is None:
            break
        node = child
    return node


def walk(node, depth=0, branch="Корень"):
    """Обход дерева с глубиной и значением входящей ветви."""
    yield depth, branch, node
    for value, child in node.children.items():
        yield from walk(child, depth + 1, value)
