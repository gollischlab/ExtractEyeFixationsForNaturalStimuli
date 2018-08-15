# Format fixations from eye tracking database

Extract the relevant information from eye tracking data for creating visual stimuli. The data used can be found on Dryad: https://doi.org/10.5061/dryad.9pf75

The file `fixmat.py` in this repository was provided with the data.

# Usage

Download and place the file `etdb_v1.0.hdf5` into `data/` and the metadata files into `metadata/`. Additionally, create another directory named `formatted` for the output.

The file `formatdata.py` holds all relevant functions for extraction and formatting of eye movement data.

# References

Wilming N, Onat S, Ossandón J, Acik A, Kietzmann TC, Kaspar K, Gameiro RR, Vormberg A, König P (2017) An extensive dataset of eye movements during viewing of complex images. Scientific Data 4: 160126. https://doi.org/10.1038/sdata.2016.126

Wilming N, Onat S, Ossandón J, Acik A, Kietzmann TC, Kaspar K, Gameiro RR, Vormberg A, König P (2017) Data from: An extensive dataset of eye movements during viewing of complex images. Dryad Digital Repository. https://doi.org/10.5061/dryad.9pf75 
