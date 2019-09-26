from anytree.search import findall
DELIMITER = '/'

def max_points(A):
    n = len(A)
    points = []

    if n == 0:
        return points

    if A[0] >= A[1]:
        points.append(0)

    for i in range(1, n-2):
        if A[i] >= A[i-1] and A[i] >= A[i+1]:
            points.append(i)

    if A[n-2] <= A[n-1]:
        points.append(n-1)

    return points

def absolute_urls_from_tree_service(root_node):
    paths = []
    for node in findall(root_node):
        path = DELIMITER.join([n.name for n in node.path]).strip(DELIMITER) # .strip is ugly.
        paths.append(path)

    path_lengths = [len(p) for p in paths]
    max_path_indexes = max_points(path_lengths)

    urls = []

    for i in range(len(paths)):
        path = paths[i]
        if i in max_path_indexes:
            urls.append(path)

    return urls
