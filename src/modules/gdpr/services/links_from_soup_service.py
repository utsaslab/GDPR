def links_from_soup_service(soup, target_element=None):
    target_area = soup

    if target_element is not None:
        if target_element.startswith('.'):
            target_element = target_element.strip('.')
            target_area = soup.find('div', class_=target_element)

        elif target_element.startswith('#'):
            target_element = target_element.strip('#')
            target_area = soup.find(id=target_element)

        else:
            raise ValueError('Unkown tag type of target_element: {}'.format(target_element))

    links = []

    for link in target_area.find_all('a'):
        links.append(link.get('href'))

    return links
