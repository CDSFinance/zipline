"""
FFC-specific extensions to networkx.DiGraph
"""
from networkx import (
    DiGraph,
    topological_sort,
)
from six import itervalues, iteritems
from zipline.utils.memoize import lazyval


class CyclicDependency(Exception):
    pass


class TermGraph(DiGraph):
    """
    Graph represention of FFC Term dependencies.

    Each node in the graph has an `extra_rows` attribute, indicating how many,
    if any, extra rows we should compute for the node.  Extra rows are most
    often needed when a term is an input to a rolling window computation.  For
    example, if we compute a 30 day moving average of price from day X to day
    Y, we need to load price data for the range from day (X - 29) to day Y.

    Parameters
    ----------
    terms : dict
        A dict mapping names to final output terms.

    Attributes
    ----------
    outputs
    offset
    extra_rows

    Methods
    -------
    ordered()
        Return a topologically-sorted iterator over the terms in self.
    """
    def __init__(self, terms):
        super(TermGraph, self).__init__(self)
        parents = set()
        for term in itervalues(terms):
            self._add_to_graph(term, parents, extra_rows=0)
            # No parents should be left between top-level terms.
            assert not parents

        self._outputs = terms
        self._ordered = topological_sort(self)

    @lazyval
    def offset(self):
        """
        For all pairs (term, input) such that `input` is an input to `term`,
        compute a mapping:

            (term, input) -> offset(term, input)

        where `offset(term, input)` is defined as

            Max number of extra rows needed by any term depending on `input`
            minus
            Number of extra rows needed by `term`.

        Example
        -------

        Factor A needs 5 extra rows of USEquityPricing.close, and Factor B
        needs 3 extra rows of the same.  Factor A also requires 5 extra rows of
        USEquityPricing.high, which no other Factor uses.

        We load 5 extra rows of both `price` and `high` to ensure we can
        service Factor A, and the following offsets get computed:

        self.offset[Factor A, USEquityPricing.close] == 0
        self.offset[Factor A, USEquityPricing.high] == 0
        self.offset[Factor B, USEquityPricing.close] == 2
        self.offset[Factor B, USEquityPricing.high] raises KeyError.

        Notes
        -----
        `offset(term, input) >= 0` for all valid pairs, since `input` must be
        an input to `term` if the pair appears in the mapping.

        This value is useful because we load enough rows of each input to serve
        all possible dependencies.  However, for any given dependency, we only
        want to compute using the actual number of required extra rows for that
        dependency.  We can do so by truncating off the first `offset` rows of
        the loaded data for `input`.

        See Also
        --------
        zipline.modelling.graph.TermGraph.offset
        zipline.modelling.engine.SimpleFFCEngine._inputs_for_term
        zipline.modelling.engine.SimpleFFCEngine._mask_for_term
        """
        out = {}
        for term in self:
            extra_input_rows = term.extra_input_rows
            for input_ in term.inputs:
                out[term, input_] = self.extra_rows[input_] - extra_input_rows
            mask = term.mask
            if term.mask is not None:
                out[term, mask] = self.extra_rows[mask] - extra_input_rows
        return out

    @lazyval
    def extra_rows(self):
        """
        A dict mapping `term` -> `# of extra rows to load/compute of `term`.

        This is always the maximum number of extra **input** rows required by
        any Filter/Factor for which `term` is an input.

        Notes
        ----
        This value depends on the other terms in the graph that require `term`
        **as an input**.  This is not to be confused with
        `term.extra_input_rows`, which is how many extra rows of `term`'s
        inputs we need to load, and which is determined entirely by `Term`
        itself.

        Example
        -------
        Our graph contains the following terms:

            A = SimpleMovingAverage([USEquityPricing.high], window_length=5)
            B = SimpleMovingAverage([USEquityPricing.high], window_length=10)
            C = SimpleMovingAverage([USEquityPricing.low], window_length=8)

        To compute N rows of A, we need N + 4 extra rows of `high`.
        To compute N rows of B, we need N + 9 extra rows of `high`.
        To compute N rows of C, we need N + 7 extra rows of `low`.

        We store the following extra_row requirements:

        self.extra_rows[high] = 9  # Ensures that we can service B.
        self.extra_rows[low] = 7

        See Also
        --------
        zipline.modelling.graph.TermGraph.offset
        zipline.modelling.term.Term.extra_input_rows
        """
        return {
            term: attrs['extra_rows']
            for term, attrs in iteritems(self.node)
        }

    @property
    def outputs(self):
        """
        Dict mapping names to designated output terms.
        """
        return self._outputs

    def ordered(self):
        """
        Return a topologically-sorted iterator over the terms in `self`.
        """
        return iter(self._ordered)

    def _add_to_graph(self, term, parents, extra_rows):
        """
        Add `term` and all its inputs to the graph.
        """
        # If we've seen this node already as a parent of the current traversal,
        # it means we have an unsatisifiable dependency.  This should only be
        # possible if the term's inputs are mutated after construction.
        if term in parents:
            raise CyclicDependency(term)
        parents.add(term)

        # Idempotent if term is already in the graph.
        self.add_node(term)

        # Make sure we're going to compute at least `extra_rows` of `term`.
        self._ensure_extra_rows(term, extra_rows)

        # Number of extra rows we need to compute for this term's dependencies.
        dependency_extra_rows = extra_rows + term.extra_input_rows

        # Recursively add dependencies.
        for dependency in term.inputs:
            self._add_to_graph(
                dependency,
                parents,
                extra_rows=dependency_extra_rows,
            )
            self.add_edge(dependency, term)

        # Add term's mask, which is really just a specially-enumerated input.
        mask = term.mask
        if mask is not None:
            self._add_to_graph(mask, parents, extra_rows=dependency_extra_rows)
            self.add_edge(mask, term)

        parents.remove(term)

    def _ensure_extra_rows(self, term, N):
        """
        Ensure that we're going to compute at least N extra rows of `term`.
        """
        attrs = self.node[term]
        attrs['extra_rows'] = max(N, attrs.get('extra_rows', 0))
