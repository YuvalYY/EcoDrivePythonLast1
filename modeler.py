# this class would take the centers list (load from file) and a dir, for each file it will create the file
# it will generate the drive matrix with another column s4et to false
# for each line it will find the closest center and insert into a map of center->all the lines with it
# each center will choose its closest point to be its representation, which will be marked by true in the new column
# we will also need to save in each one, who is its relevant center
# then we will calculate the cost between the points (which will also include normalized speed),
# and the cost between the current one to the next one, with the last one having cost of 0 to the next
