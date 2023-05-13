import itertools as it

import networkx as nx
import numpy as np
import numpy.typing as npt
import pandas as pd

from squidalytics.constants import ABILITIES, PRIMARY_ONLY


def calculate_num_bins(ability_points: int, bin_size: int = 10) -> int:
    """Calculate the number of bins for an ability.

    Args:
        ability_points (int): The number of ability points.

        bin_size (int): The size of the bins. Defaults to 10.

    Returns:
        int: The number of bins.
    """

    return int(np.ceil(ability_points / bin_size))


def bin_abilities(abilities: dict[str, int], bin_size: int = 10) -> set[str]:
    """Bin abilities into bins of size `bin_size`. Main Slot Only abilities are
    not binned.

    Args:
        abilities (dict[str, int]): A dictionary containing the ability name
            and the number of ability points.

        bin_size (int): The size of the bins. Defaults to 10.

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
            num_bins = calculate_num_bins(ability_points, bin_size)
            for i in range(num_bins):
                j = i + 1
                bin_name = f"{ability}: {i * bin_size + 1}-{j * bin_size}"
                out.add(bin_name)
        else:
            raise ValueError(f"Invalid ability: {ability}")
    return out


def generate_all_abilities(bin_size: int = 10) -> list[str]:
    """Generate a list of all abilities, including binned abilities.

    Args:
        bin_size (int, optional): The size of the bins. Defaults to 10.

    Returns:
        list[str]: A list of all abilities, including binned abilities.
    """
    out = []
    num_bins = calculate_num_bins(57, bin_size)
    for ability in PRIMARY_ONLY:
        out.append(ability)
    for ability in ABILITIES:
        for i in range(num_bins):
            j = i + 1
            bin_name = f"{ability}: {i * bin_size + 1}-{j * bin_size}"
            out.append(bin_name)
    return out


def generate_adjacency_matrix(
    abilities: set[str], all_abilities: list[str], tensor_rank: int = 2
) -> np.ndarray:
    """Generate an adjacency matrix for the given abilities. This matrix will
    have the abilities from the given set as columns and rows and will be filled
    with ones for connected abilities and zeros for unconnected abilities. This
    matrix should be used as a starting point for building a consensus matrix.
    This will include self-adjacency, as it is assumed that the consensus graph
    will remove self-adjacency. Additionally, the self-adjacency can be used to
    determine the number of builds that have a given ability.

    Args:
        abilities (set[str]): A set of abilities to be included in the adjacency
            matrix.
        all_abilities (list[str]): A list of all abilities, used for determining
            the index of each ability in the matrix.
        tensor_rank (int): The rank of the adjacency tensor. Defaults to 2.

    Returns:
        np.ndarray: An adjacency matrix with the abilities from the given set as
            columns and rows, filled with ones for connected abilities and zeros
            for unconnected abilities.
    """
    num_abilities = len(all_abilities)
    shape = (num_abilities,) * tensor_rank
    adjacency_matrix = np.zeros(shape, dtype=np.int64)
    abilities_list = list(abilities)

    for i in range(len(abilities_list)):
        for j in range(i, len(abilities_list)):
            ability_i_idx = all_abilities.index(abilities_list[i])
            ability_j_idx = all_abilities.index(abilities_list[j])
            adjacency_matrix[ability_i_idx, ability_j_idx] = 1
            adjacency_matrix[ability_j_idx, ability_i_idx] = 1
    return adjacency_matrix


def generate_adjacency_tensor(
    abilities: set[str], all_abilities: list[str], tensor_rank: int = 2
) -> list[int]:
    """Generate an adjacency tensor for the given abilities. This tensor is
    sparse and as a result is stored as a list of integers. This is much more
    memory efficient than a dense adjacency matrix.


    Args:
        abilities (set[str]): A set of abilities to be included in the adjacency
            tensor.
        all_abilities (list[str]): A list of all abilities, used for determining
            the index of each ability in the tensor.
        tensor_rank (int): The rank of the adjacency tensor. Defaults to 2.

    Returns:
        list[int]: An index representation of the sparse adjacency tensor.
    """
    abilities_list = list(abilities)
    abilities_idx = [all_abilities.index(ability) for ability in abilities_list]
    return list(it.product(abilities_idx, repeat=tensor_rank))


def einsum_str(rank: int) -> str:
    """Generate an einsum string for a tensor of the given rank.

    Args:
        rank (int): The rank of the tensor.

    Returns:
        str: An einsum string for a tensor of the given rank.
    """
    tensor = "".join([chr(i) for i in range(97, 97 + rank)])
    return f"{tensor},{tensor[0]}->{tensor[1:]}"


def generate_consensus_matrix(
    matrices: list[npt.NDArray[np.int64]] | npt.NDArray[np.int64],
    weights: pd.Series | np.ndarray | list[float | int] | None = None,
) -> np.ndarray:
    """
    Generate a consensus matrix from a list of adjacency matrices. The matrices
    must have the same shape, and the weights must be the same length as the
    list of matrices. If the weights are None, all matrices will be weighted
    equally.

    Args:
        matrices (list[npt.NDArray[np.int64]]): A list of adjacency matrices to
            be used to generate the consensus matrix. These matrices must have
            the same shape.
        weights (pd.Series | np.ndarray | list[float | int] | None): A vector of
            weights to be applied to each matrix. Inputs will be converted to a
            np.ndarray. If None, all matrices will be weighted equally. Defaults
            to None.

    Raises:
        ValueError: If matrices is a numpy array and the shape is not (n, m, m).
        TypeError: If the matrices are not a list of matrices or a (n, m, m)
            tensor.
        TypeError: If the weights are not a pd.Series, np.ndarray, list of
            values, or None.

    Returns:
        np.ndarray: A consensus tensor computed as the weighted sum of the input
            matrices.
    """
    if isinstance(matrices, list):
        adjacency_tensor = np.stack(matrices, axis=0)
    elif isinstance(matrices, np.ndarray):
        if all([dim == matrices.shape[1] for dim in matrices.shape[1:]]):
            adjacency_tensor = matrices
        else:
            raise ValueError(
                "Invalid shape for adjacency matrix. Must be a (n, m, m, ...) "
                "tensor."
            )
    else:
        raise TypeError(
            f"Invalid type for matrices: {type(matrices)}. Must be a list of "
            "matrices or a (n, m, m) tensor."
        )

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

    # Use einsum to multiply the (n, m, m, ...) tensor by the (n, ) weights
    # vector, which is equivalent to multiplying each matrix by its weight and
    # then summing them together
    einsum_string = einsum_str(adjacency_tensor.ndim)
    return np.einsum(einsum_string, adjacency_tensor, weights_vector)


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
        return [multiplier * np.log(width + 1) for width in altered_widths]
    else:
        return [multiplier * width for width in altered_widths]
