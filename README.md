# build-CARLA-graph

## Steps for building waypoint graph for CARLA
### First Iteration
1. Generate the original graph (version 0) from `build_map_graph.py`
2. Use `graph_search.py` to evaluate every point's path to goal point. It will store the points that cannot find the path to goal point using the original version of graph
3. The points that cannot find the path to goal will be stored in `{Town}_not_found.txt`

### Second Iteration
1. Run `unit_test_usage.ipynb`, input "town name" and "each test case" in the `{Town}_not_found.txt`
      - If path found:
          - Path will automatically add to the graph
      - If path not found:
          - (Option 1) Run `manual_build.py` to manually add new edge to the graph
          - (Option 2) If the distance between start and end is far, use `manual_build.py` to find the middle point, then use `manual_add.py` to find the path from "start to middle" and "middle to end"
2. Next
      - (Option 1) Keep Iterating through each testcase until solving every test case in `{Town}_not_found.txt`
      - (Option 2) Rerun `graph_search.py` to evaluate every points' path to goal point. Generate new `{Town}_not_found.txt`
