

class Tree:

    def __init__(self, common_name: str, family: str):
        self.common_name = common_name
        self.family = family
        self.count = 0

    def increment_count(self):
        self.count = self.count + 1


class Trees:
    def __init__(self):
        self.trees = get_conifer_list()

    def get_total_trees(self):
        return sum(t.count for t in self.trees)


def get_conifer_list():
    trees = list()

    trees.append(Tree('araucaria', 'Araucariaceae'))
    trees.append(Tree('cypress', 'Cupressaceae'))
    trees.append(Tree('pine', 'Pinaceae'))
    trees.append(Tree('yellow-wood', 'Podocarpaceae'))
    trees.append(Tree('umbrella-pine', 'Sciadopityaceae'))
    trees.append(Tree('yew', 'Taxaceae'))

    return trees
