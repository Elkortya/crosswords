# crosswords generator

A take on automatic crosswords grid generation. 
The user provides a grid of any shape, with any black squares already placed (or none) and letters already placed, ant the algorithm will try to find a combination of existing words from a given dictionnary to fill up the grid.

Usage ``` python main.py -grid_shape path/to/gridshape/text/file ```.  
See ```ressources/grid_template_example.txt``` for an example file.

If success (or after a certain number of tries), returns an image of the completed grid in ```res``` folder. 

The basic algorithm is as follows :
* Find the word slot with the least possible words given the current letters placed
* Choose a word among those possible for this slot. The choice has a random part, but is weighted by the impact on the rest of the grid (basically, words which significantly reduce the number of possible words for other slots are chosen less often than others)
* Continue with next word slot
* If at some point you get stuck, return the grid as is (no backtracking), and try again from a new initialisation for a given number of times.

The current dictionnary (in ```ressources``` folder) is in French, but can be easily changed.

___

Some nice outputs (no fixed letters in initial grid) :

![cw1](https://user-images.githubusercontent.com/69635385/124143996-dee83000-da8b-11eb-9584-137031a01c14.png)
![cw2](https://user-images.githubusercontent.com/69635385/124144004-e0b1f380-da8b-11eb-96c6-08142712dad0.png)
![cw3](https://user-images.githubusercontent.com/69635385/124144008-e1e32080-da8b-11eb-90d8-e56f9a4bf56e.png)

