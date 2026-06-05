#
#     [10,20,30,40,50,60] => [10,20,30,40,50,60], [0, 0, 0, 0, 0, 0]
#     [8,9,-7,-8,-9,-1]=> [-7,-8,-9,-1,8,9]
#     
# **Answer**

# + nbgrader={"grade": false, "grade_id": "cell-f56b2403c0c2e4d4", "locked": false, "schema_version": 1, "solution": true}


# + deletable=false editable=false nbgrader={"grade": true, "grade_id": "cell-84b2e41f792e50a0", "locked": true, "points": 3, "schema_version": 1, "solution": false}
assert (not [10,20,30,40,50,60] == [10,20,30,40,50,60]) and ([10,20,30,40,50,60] != [-7,-8,-9,-1,8,9])