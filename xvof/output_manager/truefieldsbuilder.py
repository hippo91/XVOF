#!/usr/bin/env python2.7
"""
A collection of methods for building True fields from classical and enriched ones
"""
import numpy as np


def build_node_true_field(classical_field, enriched_field, node_status):
    """
    Build the node true field based on the node status

    :param classical_field: field of classical values
    :param enriched_field: field of enriched values
    :param node_status: boolean mask where True indicates an enriched item
    :return: the node true field

    >>> import numpy as np
    >>> a = np.array([1., 2., -1., 1.])
    >>> b = np.array([0., 0.5, 1.5, 0.])
    >>> s = np.array([False, True, True, False])
    >>> build_node_true_field(a, b, s).tolist()
    [1.0, 1.5, 0.5, 1.0]
    >>> b = np.array([1.5, 0.5, 0., 0.])
    >>> s = np.array([True, True, False, False])
    >>> build_node_true_field(a, b, s).tolist()
    [-0.5, 2.5, -1.0, 1.0]
    >>> s = np.array([True, True, True, False])
    >>> build_node_true_field(a, b, s).tolist() # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError
    >>> a = np.array([1., 2., -1., 1., -0.5, -2, 3.])
    >>> b = np.array([0., 0.5, 1.5, 0., 0., 2.5, -3.0])
    >>> s = np.array([False, True, True, False, False, True, True])
    >>> build_node_true_field(a, b, s).tolist()
    [1.0, 1.5, 0.5, 1.0, -0.5, -4.5, 0.0]
    """
    true_field = np.copy(classical_field)
    sign = -1
    for i, b in enumerate(node_status):
        if b:
            true_field[i] = classical_field[i] + sign * enriched_field[i]
            sign *= -1
    if sign == 1:
        raise ValueError("""We don't know yet how to handle discontinuities so close"""
                         """ that enrichment functions share support!""")
    return true_field


def build_cell_true_field(classical_field, enriched_field, cell_status):
    """
    Build the cell true field based on the cell status

    :param classical_field: field of classical values
    :param enriched_field: field of enriched values
    :param cell_status: boolean mask where True indicates an enriched item
    :return the cell true field

    >>> import numpy as np
    >>> a = np.array([1., 2., 1.])
    >>> b = np.array([0., 0.5, 0.])
    >>> s = np.array([False, True, False])
    >>> build_cell_true_field(a, b, s).tolist()
    [1.0, 1.5, 2.5, 1.0]
    >>> b = np.array([0.25, 0., 0.])
    >>> s = np.array([True, False, False])
    >>> build_cell_true_field(a, b, s).tolist()
    [0.75, 1.25, 2.0, 1.0]
    >>> a = np.array([1., -2., 2., 3., -7, 10.])
    >>> b = np.array([0., -2., 0., 0., 2., 0.])
    >>> s = np.array([False, True, False, False, True, False])
    >>> build_cell_true_field(a, b, s).tolist()
    [1.0, 0.0, -4.0, 2.0, 3.0, -9.0, -5.0, 10.0]
    >>> a = np.array([-3., 2., 1., -3., -5, 9.])
    >>> b = np.array([0., -2., 3., 0., 0., 0.])
    >>> s = np.array([False, True, True, False, False, False])
    >>> build_cell_true_field(a, b, s).tolist()
    [-3.0, 4.0, 0.0, -2.0, 4.0, -3.0, -5.0, 9.0]
    """
    true_field = np.copy(classical_field)
    offset = 0
    for stable_index in np.where(cell_status)[0]:
        moving_index = stable_index + offset
        true_field = np.insert(true_field, moving_index+1, true_field[moving_index])
        true_field[moving_index] -= enriched_field[stable_index]
        true_field[moving_index+1] += enriched_field[stable_index]
        offset += 1
    return true_field.reshape((len(true_field), 1))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
