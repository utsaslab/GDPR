from urllib.parse import urlparse
from anytree import Node
from ..specifications import ssl_scheme_specification

def url_trees_from_sources_service(sources):
    root_nodes = []

    for source in sources:
        if ssl_scheme_specification.is_satisfied_by(source) is False:
            source = 'https://' + source

        o = urlparse(source)

        host = "{}://{}".format(o.scheme, o.netloc)

        host_node = None

        if len(root_nodes) > 0:
            for node in root_nodes:
                if node.name == host:
                    host_node = node
                    break

        if host_node is None:
            host_node = Node(host)
            root_nodes.append(host_node)

        paths = o.path.split('/')
        paths = list(filter(None, paths)) # filter away empty strs

        if len(o.query) > 0:
            tail_subpath = paths[-1]
            tail_subpath += '?' + o.query
            paths[-1] = tail_subpath # override tail path in paths list.

        tmp_path_nodes = []

        for i in range(0, len(paths)):
            subpath = paths[i]
            if i == 0:
                subpath_node = Node(subpath, parent=host_node)
            else:
                subpath_node = Node(subpath, parent=tmp_path_nodes[i-1]) # nope. should be subpath_nodes[i-1]

            tmp_path_nodes.append(subpath_node)

    # return host_node
    return root_nodes
