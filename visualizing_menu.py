from menu import *



class VisualizingMenu(Menu):
    def __init__(self, root):
        super().__init__()

        self.root = root

        self.title = "Visualizing menu"

        # self.actions = {
        #     "return to main menu" : self.root.welcome
        #                } | {
        #     "visualize " + measure["name"] : lambda : self.see(measure) for measure in self.root.saved_measures
        # }
        self.actions = {
            "return to main menu": self.root.welcome
        }
        for measure in self.root.saved_measures:
            self.actions["visualize " + measure["name"]] = lambda x=measure.copy(): self.see(x)

        self.seen_stuff = ""

    def print_additional_menu(self):

        if len(self.actions.keys()) <= 1:
            print(f"{bcolors.WARNING}there are no measures to be visualized, to reload insert any character")

        self.actions = {
                           "return to main menu": self.root.welcome
                       }
        for measure in self.root.saved_measures:

            self.actions["visualize " + measure["name"]] = lambda x=measure.copy(): self.see(x)

        print(self.seen_stuff)

    def see(self, x):



        scores = [int(re.findall("\d+", line)[-1]) for line in x["score_lines"]]
        mean = sum(scores) / len(scores)
        errors = list(filter(lambda y : y>=mean * 1.5, scores))
        not_errors = list(filter(lambda y : y<mean * 1.5, scores))
        no_error_mean = sum(not_errors) / len(not_errors)
        best = min(scores)

        self.seen_stuff = ""
        self.seen_stuff += x["name"]
        self.seen_stuff += "\n"

        for n, score in enumerate(x["score_lines"]):
            self.seen_stuff += f'\n{bcolors.OKGREEN if scores[n] == best else (bcolors.FAIL if scores[n] in errors else bcolors.HEADER)}{score}'
        self.seen_stuff += f'\n\n{bcolors.HEADER}'

        self.seen_stuff += f"mean: {mean:.4}ms\n"
        self.seen_stuff += f"best: {best}ms\n"
        self.seen_stuff += f"errors: {len(errors)}\n"
        self.seen_stuff += f"mean without errors: {no_error_mean:.4}ms\n"


