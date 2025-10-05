"""Helpers rehashed from past code"""

import collections.abc
import numpy as np
import re

def remove_quotation_from_string(string, leave_quotes=True):
    """Helper to strip quoted content from strings, used for depth calculation in print_obj_map."""
    # string = re.sub(r'"[^"]*"', '""', re.sub(r"'[^']*'", "''", string))
    string = re.sub(r"'[^']*'", "''", string)  # remove content between single quotes
    string = re.sub(r'"[^"]*"', '""', string)  # remove content between double quotes
    if not leave_quotes:
        string = re.sub(r"['\"]", "", string)  # remove the quote characters themselves
    return string


def mapout_obj(
    obj,
    include_dicts=False,
    include_all_iterables=False,
    mode="type_only",  # "type_only", "type_and_size", or "value"
    objmap=None,  # accumulator dict, initialized on first call
    header="",  # hierarchical key path like "OBJECT.attr.nested_attr"
    depth=0,
    min_depth=0,
    max_depth=5,
):
    """Recursively map out an object's attributes"""

    if objmap is None:
        objmap = {}
    known_modes = ["type_only", "type_and_size", "value"]
    if mode not in known_modes:
        raise KeyError(
            "Cannot recognize the mode '{}'. Please choose from {}.".format(mode, known_modes)
        )
    # Only record this level if we've reached minimum depth
    if depth >= min_depth:
        if mode == "value":
            objmap[header] = obj
        else:
            val_for_map = str(type(obj))
            if mode == "type_and_size":
                is_iterable = (
                    isinstance(obj, collections.abc.Iterable) and type(obj) is not str
                )
                if is_iterable:  # Validate iterability (handles 0-d torch.Tensor edge cases)
                    try:
                        len(obj)
                    except TypeError:
                        is_iterable = False
                val_for_map += (
                    ""
                    if not is_iterable
                    else " {}".format(str(len(obj)))
                    if not hasattr(obj, "shape")
                    else " {}".format(str(obj.shape))
                )
            objmap[header] = val_for_map

    # Continue recursion if we haven't hit max depth
    if depth < max_depth:
        # Case 1: objects with __dict__ (class instances)
        if hasattr(obj, "__dict__") and len(obj.__dict__):
            for key in obj.__dict__:
                if "__" not in key:  # Skip dunder attributes
                    val = getattr(obj, key)  # Use getattr for safe attribute access
                    objmap = mapout_obj(
                        val,
                        include_dicts=include_dicts,
                        include_all_iterables=include_all_iterables,
                        mode=mode,
                        objmap=objmap,
                        header="{}.{}".format(header, key),
                        depth=depth + 1,
                        min_depth=min_depth,
                        max_depth=max_depth,
                    )
        # Case 2: dictionaries (if enabled)
        elif (include_dicts or include_all_iterables) and isinstance(
            obj, collections.abc.MutableMapping
        ):
            for key, val in obj.items():
                objmap = mapout_obj(
                    val,
                    include_dicts=include_dicts,
                    include_all_iterables=include_all_iterables,
                    mode=mode,
                    objmap=objmap,
                    header="{}[{}]".format(
                        header, key if type(key) is not str else "'{}'".format(key)
                    ),
                    depth=depth + 1,
                    min_depth=min_depth,
                    max_depth=max_depth,
                )
        # Case 3: lists/arrays/iterables (if enabled)
        elif (
            include_all_iterables
            and isinstance(obj, collections.abc.Iterable)
            and type(obj) is not str
            and len(np.array(obj).shape)  # Ensure it has dimensionality
        ):
            if len(np.array(obj).shape) == 1:
                obj = np.array(obj)  # Normalize to numpy for consistent iteration
            for ind, val in enumerate(obj):
                objmap = mapout_obj(
                    val,
                    include_dicts=include_dicts,
                    include_all_iterables=include_all_iterables,
                    mode=mode,
                    objmap=objmap,
                    header="{}[{}]".format(header, ind),
                    depth=depth + 1,
                    min_depth=min_depth,
                    max_depth=max_depth,
                )
    return objmap


def print_obj_map(
    obj,
    include_dicts=True,
    include_all_iterables=False,
    mode="type_and_size",
    max_char=1000,
    header="OBJECT",
    min_depth=0,
    max_depth=5,
):
    """Pretty-print object structure with indentation and formatting."""
    BOLD = "\033[1m"
    UNBOLD = "\033[0m"

    # Build the object map
    mapped_out_obj = mapout_obj(
        obj,
        include_dicts=include_dicts,
        include_all_iterables=include_all_iterables,
        mode=mode,
        header=header,
        depth=0,
        min_depth=min_depth,
        max_depth=max_depth,
    )

    # Format and print each entry
    for k, v in mapped_out_obj.items():
        # Calculate indentation from nesting depth (count dots and brackets)
        depth = sum(remove_quotation_from_string(k).count(dlmtr) for dlmtr in [".", "["])
        n_indents = depth - min_depth
        left_margin = "\t" * n_indents
        v_on_new_line = "\n" if "\n" in str(v) else ""
        k_printout = left_margin + BOLD + k + ": " + UNBOLD

        # Check if this iterable will be expanded in subsequent lines
        iterable_is_expanded_later = (depth < max_depth) and (
            (
                (include_dicts or include_all_iterables)
                and isinstance(v, collections.abc.MutableMapping)
            )
            or (
                include_all_iterables
                and isinstance(v, collections.abc.Iterable)
                and type(v) is not str
                and len(np.array(v).shape)
            )
        )

        # If expanded later, just show type; otherwise show full value
        if iterable_is_expanded_later and len(v):
            v_printout = str(type(v))
        else:
            v_printout = str(v)
            v_printout = (v_on_new_line + v_printout).replace("\n", v_on_new_line + left_margin)
            # Truncate very long output
            if len(v_printout) >= max_char:
                truncation_string = "\n{} ... printout of {} truncated ... \n{}".format(
                    left_margin, k, left_margin
                )
                v_printout = (
                    v_printout[: max_char // 2] + truncation_string + v_printout[-max_char // 2 :]
                )
        print(k_printout + v_printout)
    return mapped_out_obj