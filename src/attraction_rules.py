## target = 0, antshrike = 1, antwren = 2, others = 3.
attraction_matrix = [ [0,0,0,0], # target does not have outgoing edges
                      [1,1,1,1], # antshrike equally attracted to target and birds
                      [1,1,1,1], # same for antwren
                      [0,1,1,1] ] # others don't have a target
