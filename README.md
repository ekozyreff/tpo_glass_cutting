# Minimizing the cycle lengh of a glass cutting machine

This dataset was used in a research paper on tool path optimization of a glass cutting machine (under review).

Throughout this dataset, 'unif' and 'rand' are related to instances with uniformly and randomly spaced lines, respectively; 'v' is the number of vertical lines, 'h' is the number of horizontal lines, and 'r' is the replication number (1, 2, 3, 4 or 5).

The name of every file in the folder 'instances' has the pattern 'tpo_xxxx_v_h_r', where 'xxxx' is 'unif' or 'rand'. The acronym 'tpo' stands for 'tool path optimization'.
This folder contains information about the instances tested. The first line of each file has the dimensions of the glass plate. The second line has the horizontal coordinates of the vertical lines. And the thrid line has the vertical coordinates of the horizontal lines.

The file 'tpo.py' has the Python/Gurobi code with both MIP formulations.

More details are available at http://dx.doi.org/10.17632/cwdjvnp8kk.3
