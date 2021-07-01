from Grid import *
from Dictionnary import *
from Graphical import *
import argparse

if __name__ == "__main__":

    # get arguments
    parser = argparse.ArgumentParser(description='Hyperparameters')
    parser.add_argument('-debug', type=bool, default=False,
                        help='debug mode')
    parser.add_argument('-nb_tries', type=int, default=10,
                        help='number of tries for a given grid')
    # Grid shape means the size, position of black squares, possible initial letters of the grid.
    # It must be provided in the form of a text file. For an example, see ressources/grid_template_example.txt
    # . means empty square
    # $ means black square
    # a letter means that letter
    parser.add_argument('-grid_shape', type=str, required=True,
                        help='empty grid template the algorithm will try to fill')
    args = parser.parse_args()

    # path to dictionary of recognized words (default is French one, but customazible)
    path_dictionnary = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ressources", "list_mots_clean.txt")

    # the algorithm is stochastic, and gets stuck in local minima. It's good practice to run it a couple of times
    # for a given grid template to get better odds of success.
    for try_ in range(args.nb_tries):
        print("Try number", try_)

        # Create Dictionnary object from a dictionnary text file
        dictionnary = Dictionnary(path_dictionnary)

        # Create the grid object from a grid shape.
        grid = Grid(args.grid_shape, dictionnary, args.debug)

        success = grid.fill_up_grid()
        print("Success :") if success else print(
            "Couldn't complete the grid, here's the best we could do for this try :")
        final_grid = grid.print_current_grid_state()

        # A graphical version of the grid is produced
        if success or try_ == args.nb_tries -1:
            print("Saving result in res/result.png")
            make_pretty_output_out_of_grid(final_grid, grid.h, grid.w)