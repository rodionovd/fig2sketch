from . import base

BOOLEAN_OPERATIONS = {
    'UNION': 0,
    'INTERSECT': 2,
    'SUBTRACT': 1,
    'XOR': 3
}


def convert(figma_bool_ops):
    return {
        '_class': 'shapeGroup',
        **base.base_shape(figma_bool_ops),
        'name': figma_bool_ops.name,
        'shouldBreakMaskChain': True,
        'hasClickThrough': False,
        "groupLayout": {
            "_class": "MSImmutableFreeformGroupLayout"
        },
        'windingRule': 0
    }


def post_process(figma_bool_ops, sketch_bool_ops):
    op = BOOLEAN_OPERATIONS[figma_bool_ops.booleanOperation]
    for l in sketch_bool_ops['layers']:
        l['booleanOperation'] = op

    return sketch_bool_ops
