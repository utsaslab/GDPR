import json

def anti_patterns_for_article_service(article, delimiter='.'):
    article = article.lower()
    # article.(section:optional).(subsection:optional).(enumerated_clause:optional)
    with open('./modules/gdpr/assets/anti-patterns.json') as f:
        anti_patterns = json.load(f)

    matches = []

    descriptions = []
    examples = []
    references = []

    for anti_pattern in anti_patterns:
        gdpr_articles = anti_pattern['gdpr_articles']
        for gdpr_article in gdpr_articles:
            description = anti_pattern['anti_pattern']
            example = anti_pattern['example']
            reference = gdpr_article.split('.')[0]

            if isinstance(reference, int) is False: # eg. 5(1e) or 5(1b)
                reference = reference.replace('(', delimiter)
                reference = reference.strip(')')

            matches = 0
            art_comps = article.split(delimiter)
            ref_comps = reference.split(delimiter)
            
            for c1 in art_comps:
                for c2 in ref_comps:
                    if c1 == c2:
                        matches += 1

            if matches >= len(art_comps):
                descriptions.append(description)
                examples.append(example)
                references.append(reference)

                break

    return (descriptions, examples, references)
