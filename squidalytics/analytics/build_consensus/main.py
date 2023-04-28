import numpy as np
import pandas as pd
import networkx as nx

from squidalytics.constants import ABILITIES, PRIMARY_ONLY


def bin_abilities(abilities: dict[str, int], bin_size: int) -> set[str]:
    """Bin abilities into bins of size `bin_size`. Main Slot Only abilities are
    not binned.

    Args:
        abilities (dict[str, int]): A dictionary containing the ability name
            and the number of ability points.

        bin_size (int): The size of the bins.

    Raises:
        ValueError: If an invalid ability is passed.

    Returns:
        set[str]: A set of binned abilities. Main Slot Only abilities are not
            binned. Abilities are binned in the order they appear in the input
            list, and will be in the format:

                ``{ability}: {bin_start}-{bin_end}``
    """

    out = set()
    for ability, ability_points in abilities.items():
        if ability in PRIMARY_ONLY:
            out.add(ability)
        elif ability in ABILITIES:
            num_bins = ability_points // bin_size
            for i in range(num_bins):
                j = i + 1
                bin_name = f"{ability}: {i * bin_size + 1}-{j * bin_size}"
                out.add(bin_name)
        else:
            raise ValueError(f"Invalid ability: {ability}")
    return out


def generate_base_matrix(abilities: set[str]) -> pd.DataFrame:
    """Generate a base matrix for the given abilities. This matrix will have
    the given abilities as columns and rows, and will be filled with zeros.
    This should be used as a starting point for building a consensus matrix.

    Args:
        abilities (set[str]): A set of abilities.

    Returns:
        pd.DataFrame: A base matrix with the given abilities as columns and
            rows.
    """
    abilities_as_list = list(abilities)

    return pd.DataFrame(
        index=abilities_as_list, columns=abilities_as_list, data=0
    )


def generate_adjacency_matrix(
    abilities: set[str], base_matrix: pd.DataFrame
) -> pd.DataFrame:
    """Generate an adjacency matrix for the given abilities. This matrix will
    have the given abilities as columns and rows, and will be filled with
    zeros. This should be used as a starting point for building a consensus
    matrix. This will include self-adjacency, as it is assumed that the
    consensus graph will remove self-adjacency. Additionally, the self-adjacency
    can be used to determine the number of builds that have a given ability.

    Args:
        abilities (set[str]): A set of abilities.

        base_matrix (pd.DataFrame): A base matrix with the given abilities as
            columns and rows.

    Returns:
        pd.DataFrame: An adjacency matrix with the given abilities as columns
            and rows.
    """
    abilities_as_list = list(abilities)
    out_matrix = base_matrix.copy()

    for ability_1 in abilities_as_list:
        for ability_2 in abilities_as_list:
            out_matrix.loc[ability_1, ability_2] = 1

    return out_matrix


def generate_consensus_matrix(
    matrices: list[pd.DataFrame],
    weights: pd.Series | np.ndarray | list[float | int] | None = None,
) -> pd.DataFrame:
    """Generate a consensus matrix from a list of matrices. The matrices must
    have the same shape, and the weights must be the same length as the list of
    matrices. If the weights are None, all matrices will be weighted equally.

    Args:
        matrices (list[pd.DataFrame]): A list of matrices to be used to generate
            the consensus matrix. These matrices must have the same shape.
        weights (pd.Series | np.ndarray | list[float | int] | None): A vector of
            weights to be applied to each matrix. Inputs will be converted to a
            np.ndarray. If None, all matrices will be weighted equally. Defaults
            to None.

    Raises:
        TypeError: If the weights are not a pd.Series, np.ndarray, list of
            values, or None.

    Returns:
        pd.DataFrame: A consensus matrix.
    """

    adjacency_tensor = np.array([matrix.values for matrix in matrices])


    if weights is None:
        weights_vector = np.ones(len(matrices))
    elif isinstance(weights, pd.Series):
        weights_vector = weights.values
    elif isinstance(weights, np.ndarray):
        weights_vector = weights
    elif isinstance(weights, list):
        weights_vector = np.array(weights)
    else:
        raise TypeError(
            f"Invalid type for weights: {type(weights)}. Must be a "
            "pd.Series, np.ndarray, a list of values, or None."
        )

    # Use einsum to multiply the (n, m, m) tensor by the (n, ) weights vector,
    # which is equivalent to multiplying each matrix by its weight and then
    # summing them together
    aggregate_matrix = np.einsum("ijk,i->jk", adjacency_tensor, weights_vector)

    # Put the aggregate matrix, whose shape is now (m, m), into a dataframe
    return pd.DataFrame(
        aggregate_matrix,
        index=matrices[0].index,
        columns=matrices[0].columns,
    )


def calculate_width_by_connection(
    graph: nx.Graph, multiplier: float | int = 1, logarithmic: bool = False
) -> list[float]:
    """Calculate the width of each edge in the graph based on the edge weight.
    The width is calculated as the edge weight multiplied by the multiplier.
    If logarithmic is True, the width will be calculated as the log of the edge
    weight plus 1 multiplied by the multiplier.

    Args:
        graph (nx.Graph): A graph.
        multiplier (float | int): A multiplier to be applied to the edge weight.
            Defaults to 1.
        logarithmic (bool): Whether or not to calculate the width as the log of
            the edge weight plus 1. Defaults to False.

    Returns:
        list[float]: A list of edge widths.
    """
    base_widths = [graph.edges[edge]["weight"] for edge in graph.edges()]
    max_width = max(base_widths)
    altered_widths = [width / max_width for width in base_widths]
    if logarithmic:
        # Add 1 to the width to avoid taking the log of 0 and to avoid
        # negative widths
        return [multiplier * np.log(width + 1) for width in base_widths]
    else:
        return [multiplier * width for width in base_widths]
