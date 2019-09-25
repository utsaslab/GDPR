from heapq import heappush, heappop

def select_target_area(target_area, target_element):
    class_prefix = (1, '.')
    id_prefix = (2, '#')
    prefix_map = {
        '.': '#',
        '#': '.'
    }

    if target_element.startswith(class_prefix[1]) is True:
        target_element = 'div' + target_element

    heap = []
    heappush(heap, class_prefix)
    heappush(heap, id_prefix)

    while(len(heap) != 0):
        prefix = heappop(heap)[1] # (priority, prefix) :: (int, str)

        neg_prefix = prefix_map[prefix]

        if prefix in target_element:
            elements = target_element.split(prefix)
            elements = list(filter(None, elements))

            subelements = elements[1].split(neg_prefix)

            if prefix == id_prefix[1]:
                id_ = subelements[0]
                target_area = target_area.find(id=id_)
            else:
                type_ = elements[0]
                class_ = subelements[0]
                target_area = target_area.find(type_, class_=class_)
            break

    return target_area

def links_from_soup_service(soup, target_element=None):
    target_area = soup

    if target_element is not None:
        target_area = select_target_area(target_area, target_element)

    links = []

    if target_area is None:
        return links

    for link in target_area.find_all('a'):
        href = link.get('href')
        text = link.get_text()
        text = text if len(text) > 0 else None

        link_tuple = (text, href)
        links.append(link_tuple)

    return links
