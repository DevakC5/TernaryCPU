"""TritTensor — a small tensor/matrix structure for ternary data.

Supports 1D vectors and 2D matrices of ternary digits (0, 1, 2).
Provides shape inspection, transpose, flatten, dot product, matrix
multiplication, and element-wise function application.
"""

from trinary.ai.activations import (
    trit_to_signed,
    signed_to_trit,
    ternary_step,
)


class TritTensor:
    """A tensor of ternary digits with basic linear algebra operations.

    Args:
        data: Nested list of ternary digits (0/1/2). Can be 1D or 2D.

    Raises:
        ValueError: If data contains values other than 0, 1, 2, or
            if rows have inconsistent lengths.
    """

    def __init__(self, data):
        self._validate(data)
        self._data = data
        self._shape = self._compute_shape(data)

    @staticmethod
    def _validate(data):
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Data must be a non-empty list")
        if isinstance(data[0], list):
            rows = len(data)
            if rows == 0:
                raise ValueError("Data must have at least one row")
            cols = len(data[0])
            if cols == 0:
                raise ValueError("Each row must have at least one element")
            for i, row in enumerate(data):
                if not isinstance(row, list):
                    raise ValueError(f"Row {i} is not a list")
                if len(row) != cols:
                    raise ValueError(
                        f"All rows must have the same length (row {i} "
                        f"has {len(row)}, expected {cols})"
                    )
                for j, val in enumerate(row):
                    if val not in (0, 1, 2):
                        raise ValueError(
                            f"Invalid ternary digit {val} at [{i}][{j}]"
                        )
        else:
            for i, val in enumerate(data):
                if val not in (0, 1, 2):
                    raise ValueError(
                        f"Invalid ternary digit {val} at index {i}"
                    )

    @staticmethod
    def _compute_shape(data):
        if isinstance(data[0], list):
            return (len(data), len(data[0]))
        return (len(data),)

    @property
    def shape(self):
        """Return the shape of the tensor as a tuple."""
        return self._shape

    @property
    def data(self):
        """Return the underlying nested list data."""
        return self._data

    def is_vector(self) -> bool:
        """Check if this tensor is 1D (a vector)."""
        return len(self._shape) == 1

    def is_matrix(self) -> bool:
        """Check if this tensor is 2D (a matrix)."""
        return len(self._shape) == 2

    def transpose(self):
        """Return a new TritTensor that is the transpose of this matrix.

        For 1D tensors (vectors), returns the same tensor.

        Returns:
            A new TritTensor with transposed dimensions.

        Raises:
            ValueError: If the tensor is not 2D.
        """
        if self.is_vector():
            return TritTensor(self._data[:])
        rows, cols = self._shape
        transposed = [[self._data[r][c] for r in range(rows)] for c in range(cols)]
        return TritTensor(transposed)

    def flatten(self):
        """Return a new 1D TritTensor with all elements in row-major order.

        Returns:
            A new 1D TritTensor.
        """
        if self.is_vector():
            return TritTensor(self._data[:])
        flat = [val for row in self._data for val in row]
        return TritTensor(flat)

    def dot(self, other):
        """Compute the dot product with another 1D tensor.

        Both tensors must be vectors of the same length. Values are
        converted to signed representation before computation, then
        the result is returned as an integer (not a ternary digit).

        Args:
            other: Another TritTensor of the same length.

        Returns:
            Integer dot product result.

        Raises:
            ValueError: If either tensor is not a vector, or lengths differ.
        """
        if not self.is_vector() or not other.is_vector():
            raise ValueError("Dot product requires two 1D tensors (vectors)")
        if self._shape[0] != other._shape[0]:
            raise ValueError(
                f"Vector length mismatch: {self._shape[0]} vs {other._shape[0]}"
            )
        total = 0
        for i in range(self._shape[0]):
            a = trit_to_signed(self._data[i])
            b = trit_to_signed(other._data[i])
            total += a * b
        return total

    def matmul(self, other):
        """Multiply this matrix with another matrix or vector.

        Standard matrix multiplication. Values are converted to signed
        representation, multiplied, then the result is converted back
        to ternary digits using ternary_step.

        Args:
            other: A TritTensor (matrix or vector) with compatible dimensions.

        Returns:
            A new TritTensor with the result.

        Raises:
            ValueError: If dimensions are incompatible.
        """
        if not self.is_matrix():
            raise ValueError("matmul requires a 2D tensor (matrix)")
        rows_a, cols_a = self._shape
        if other.is_vector():
            if cols_a != other._shape[0]:
                raise ValueError(
                    f"Incompatible dimensions: ({rows_a},{cols_a}) x ({other._shape[0]},)"
                )
            result = []
            for r in range(rows_a):
                total = 0
                for k in range(cols_a):
                    a = trit_to_signed(self._data[r][k])
                    b = trit_to_signed(other._data[k])
                    total += a * b
                result.append(ternary_step(total))
            return TritTensor(result)
        if other.is_matrix():
            rows_b, cols_b = other._shape
            if cols_a != rows_b:
                raise ValueError(
                    f"Incompatible dimensions: ({rows_a},{cols_a}) x ({rows_b},{cols_b})"
                )
            result = []
            for r in range(rows_a):
                row = []
                for c in range(cols_b):
                    total = 0
                    for k in range(cols_a):
                        a = trit_to_signed(self._data[r][k])
                        b = trit_to_signed(other._data[k][c])
                        total += a * b
                    row.append(ternary_step(total))
                result.append(row)
            return TritTensor(result)
        raise ValueError("matmul operand must be a vector or matrix")

    def apply(self, fn):
        """Apply a function element-wise to every ternary digit.

        The function receives an integer (0/1/2) and should return
        a valid ternary digit.

        Args:
            fn: Callable that maps an integer to 0, 1, or 2.

        Returns:
            A new TritTensor with the function applied.
        """
        if self.is_vector():
            return TritTensor([fn(x) for x in self._data])
        return TritTensor([[fn(x) for x in row] for row in self._data])

    def to_signed(self):
        """Convert all ternary digits to signed values (-1, 0, +1).

        Returns:
            A nested list (same shape) of signed integers.
        """
        if self.is_vector():
            return [trit_to_signed(x) for x in self._data]
        return [[trit_to_signed(x) for x in row] for row in self._data]

    def from_signed(self, signed_data):
        """Replace data with values converted from signed to ternary digits.

        Mutates this tensor in place and returns self for chaining.

        Args:
            signed_data: Nested list of values -1, 0, or 1 matching shape.

        Returns:
            Self, for chaining.

        Raises:
            ValueError: If shape or values are invalid.
        """
        if self.is_vector():
            if len(signed_data) != self._shape[0]:
                raise ValueError(
                    f"Expected {self._shape[0]} values, got {len(signed_data)}"
                )
            self._data = [signed_to_trit(x) for x in signed_data]
        else:
            if len(signed_data) != self._shape[0]:
                raise ValueError(
                    f"Expected {self._shape[0]} rows, got {len(signed_data)}"
                )
            for r in range(self._shape[0]):
                if len(signed_data[r]) != self._shape[1]:
                    raise ValueError(
                        f"Row {r}: expected {self._shape[1]} values, "
                        f"got {len(signed_data[r])}"
                    )
                self._data[r] = [signed_to_trit(x) for x in signed_data[r]]
        return self

    def __repr__(self):
        return f"TritTensor(shape={self._shape}, data={self._data})"

    def __eq__(self, other):
        if not isinstance(other, TritTensor):
            return NotImplemented
        return self._data == other._data and self._shape == other._shape
