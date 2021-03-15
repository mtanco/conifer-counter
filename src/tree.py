import pickle

class Tree:

    def __init__(self, common_name: str, family: str):
        self.common_name = common_name
        self.family = family
        self.count = 0

    def increment_count(self):
        self.count = self.count + 1


class Trees:
    def __init__(self, file=None):
        self.trees = get_conifer_list(file)

    def get_total_trees(self):
        return sum(t.count for t in self.trees)

    def save_to_disk(self, file):
        save_object(self.trees, file)


def get_conifer_list(file):
    if file is not None:
        with open(file, 'rb') as input:
            return pickle.load(input)

    trees = list()

    trees.append(Tree('araucaria', 'Araucariaceae'))
    trees.append(Tree('cypress', 'Cupressaceae'))
    trees.append(Tree('pine', 'Pinaceae'))
    trees.append(Tree('yellow-wood', 'Podocarpaceae'))
    trees.append(Tree('umbrella-pine', 'Sciadopityaceae'))
    trees.append(Tree('yew', 'Taxaceae'))

    return trees


def save_object(obj, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)
